from webob.compat import bytes_
import atexit
import logging
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess
import time
import threading
import weakref
import webob

log = logging.getLogger(__name__)


class TransformError(Exception):
    def __init__(self, detail, comment=''):
        self.detail = detail
        self.comment = comment

    def __str__(self):
        return '%s\n%s' % (self.detail, self.comment)


def cleanup(*processes, **kw):
    for process in processes:
        if kw.get('close', True):
            if process.stdin is not None:
                process.stdin.close()
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
        if process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass

    # sum(0.01 * (2 ** n) for n in range(6)) -> 0.63
    for n in range(6):
        time.sleep(0.01 * (2 ** n))
        if all(process.poll() is not None for process in processes):
            return

    for process in processes:
        if process.poll() is None:
            try:
                process.kill()
            except OSError:
                pass

    for process in processes:
        process.wait()


# Hold a weakreference to each subprocess for cleanup during shutdown
worker_processes = weakref.WeakSet()


@atexit.register
def cleanup_processes():
    cleanup(*list(worker_processes))


def response_to_file(self, fp):
    # Force enumeration of the body (to set content-length)
    self.body
    parts = [self.status, '\r\n']
    parts += map('%s: %s\r\n'.__mod__, self.headerlist)
    parts += ['\r\n']
    fp.write(bytes_(''.join(parts)))
    fp.write(self.body)


class TransformWorker(object):
    def __init__(self, args, reload_process=False, Response=webob.Response, **kw):
        self.args = args
        self.kw = kw
        self.reload_process = reload_process
        self.Response = Response
        self.scope = threading.local()

    def new_process(self):
        """ defer creation as __init__ also called in management thread
        """
        process = subprocess.Popen(
            self.args, close_fds=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            **self.kw
        )
        worker_processes.add(process)
        return process

    def get_process(self):
        try:
            return self.scope.process
        except AttributeError:
            self.scope.process = self.new_process()
            return self.scope.process

    def return_process(self, process):
        pass

    def clear_process(self, process):
        del self.scope.process
        process.stdin.close()
        cleanup(process, close=False)
        process.stdout.close()
        errout = process.stderr.read()
        process.stderr.close()
        return errout

    def _transform(self, process, response_in):
        start = time.time()

        response_to_file(response_in, process.stdin)
        process.stdin.flush()

        headerlist = []

        # This is essentially Response.from_file with more error handling
        status = process.stdout.readline().strip()
        if not status:
            raise TransformError('missing status line')

        while 1:
            line = process.stdout.readline()
            if not line:
                raise TransformError('missing CRLF terminating headers')
            line = line.strip()
            if not line:
                # end of headers
                break
            try:
                header_name, value = line.split(b':', 1)
            except ValueError:
                raise TransformError('bad header line: %r' % (line))

            value = value.strip()
            header_name = header_name.decode('utf-8')
            value = value.decode('utf-8')
            headerlist.append((header_name, value))

        r = self.Response(
            status=status,
            headerlist=headerlist,
            app_iter=(),
        )

        content_length = r.content_length or 0
        body = process.stdout.read(content_length)
        end = time.time()

        if len(body) != content_length:
            raise TransformError('process stdout closed while reading body')

        r.body = body
        r._extfilter_duration = end - start

        return r

    def __call__(self, response_in):
        for attempt in [1, 2]:

            process = self.get_process()

            try:
                response_out = self._transform(process, response_in)

            except TransformError as e:
                e.comment = self.clear_process(process)
                if attempt == 1:
                    log.warn('Retrying: %s: %s' % (type(e).__name__, e))
                    continue
                raise

            except Exception as e:
                self.clear_process(process)
                raise

            else:
                if self.reload_process:
                    self.clear_process(process)
                else:
                    self.return_process(process)
                break

        return response_out
