from webob.compat import (
    bytes_,
    native_,
    text_type,
)


def response_to_file(self, fp, block_size=1 << 16):  # 64KB
    chunked = self.content_length is None and self.headers.get('Connection', '').lower() != 'close'
    parts = ['HTTP/1.1 ', self.status, '\r\n']
    parts += map('%s: %s\r\n'.__mod__, self.headerlist)
    if chunked:
        parts += ['Transfer-Encoding: chunked\r\n']
    parts += ['\r\n']
    fp.write(bytes_(''.join(parts)))

    status_code = self.status_code
    if status_code in (204, 304) or status_code // 100 == 1:
        return

    if not chunked:
        block = bytearray()
        for item in self.app_iter:
            block.extend(item)
            if len(block) >= block_size:
                fp.write(block)
                block = bytearray()
        if block:
            fp.write(block)

        return

    chunk = bytearray()
    for item in self.app_iter:
        chunk.extend(item)
        if len(chunk) < block_size:
            continue
        fp.write(bytes_('%x\r\n' % block_size))
        fp.write(chunk[:block_size])
        fp.write(b'\r\n')
        chunk = chunk[block_size:]

    if chunk:
        fp.write(bytes_('%x\r\n' % len(chunk)))
        chunk.extend(b'\r\n')
        fp.write(chunk)

    fp.write(b'0\r\n\r\n')


def response_from_file(cls, fp):
    """Reads a response from a file-like object (it must implement
    ``.read(size)`` and ``.readline()``).

    It will read up to the end of the response, not the end of the
    file.

    This reads the response as represented by ``str(resp)``; it
    may not read every valid HTTP response properly.  Responses
    must have a ``Content-Length``"""
    headerlist = []
    status_line = fp.readline().strip()
    if not status_line:
        return None

    is_text = isinstance(status_line, text_type)
    if is_text:
        _colon = ':'
    else:
        _colon = b':'

    if not status_line.startswith(b'HTTP/1.1 '):
        raise ValueError("malformed status line, expected: 'HTTP/1.1 ', got: %r" % status_line)

    http_version, status = status_line.split(None, 1)

    chunked = False
    keep_alive = True
    while 1:
        line = fp.readline()
        if not line:
            raise ValueError('missing CRLF terminating headers')
        line = line.strip()
        if not line:
            # end of headers
            break
        try:
            header_name, value = line.split(_colon, 1)
        except ValueError:
            raise ValueError('bad header line: %r' % (line))

        value = value.strip()
        if not is_text:
            header_name = native_(header_name, 'utf-8')
            value = native_(value, 'utf-8')

        header_name_lower = header_name.lower()
        if header_name_lower == 'transfer-encoding':
            value = value.lower()
            if value == 'chunked':
                chunked = True
            elif value == 'identity':
                pass
            else:
                raise ValueError('unsupported Transfer-Encoding: %s' % value)

        elif header_name_lower == 'connection':
            value = value.lower()
            if value == 'close':
                keep_alive = False
            elif value == 'keep-alive':
                pass
            else:
                raise ValueError('unsupported Connection: %s' % value)

        else:
            headerlist.append((header_name, value))

    r = cls(
        status=status,
        headerlist=headerlist,
        app_iter=[],
    )

    if chunked:
        end_chunk = False
        while not end_chunk:
            line = fp.readline()
            if not line:
                break  # EOF

            try:
                remaining = int(line, 16)
            except ValueError:
                raise ValueError('invalid chunk header')

            if remaining == 0:
                end_chunk = True

            chunk = fp.read(remaining)
            while chunk:
                r.app_iter.append(chunk)
                remaining -= len(chunk)
                chunk = fp.read(remaining)

            if remaining:
                raise ValueError('EOF while reading chunk')

            line = fp.readline()
            if not line:
                raise ValueError('missing CRLF terminating chunk')
            if line.strip():
                raise ValueError('chunk too long')

    elif r.content_length is not None:
        remaining = r.content_length
        chunk = fp.read(remaining)
        while chunk:
            r.app_iter.append(chunk)
            remaining -= len(chunk)
            chunk = fp.read(remaining)

        if remaining:
            raise ValueError('EOF while reading body')

    elif keep_alive:
        raise ValueError('missing Content-Length')

    else:
        chunk = fp.read()
        while chunk:
            r.app_iter.append(chunk)
            chunk = fp.read()

    return r
