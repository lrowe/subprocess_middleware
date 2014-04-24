import os.path
from setuptools import setup, find_packages

here = os.path.dirname(__file__)
try:
    with open(os.path.join(here, 'README.txt')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.txt')) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''  # tox

requires = [
    'WebOb',
]

tests_require = [
    'WebTest',
    'pyramid',
    'pytest',
]

setup(
    name='subprocess_middleware',
    version='0.1',
    description='Subprocess WSGI middleware and Pyramid tween.',
    long_description=README + '\n\n' + CHANGES,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,
    author='Laurence Rowe',
    author_email='laurence@lrowe.co.uk',
    url='http://github.com/lrowe/subprocess_middleware',
    license='MIT',
    install_requires=requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
)
