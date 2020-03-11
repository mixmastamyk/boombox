#!/usr/bin/env python
import sys
from os.path import dirname, join

from setuptools import setup


if sys.version_info < (3, 6):
    raise NotImplementedError('Sorry, only Python 3.6 and above is supported.')


def get_version(filename, version='1.00'):
    ''' Read version as text to avoid machinations at import time. '''
    with open(filename) as infile:
        for line in infile:
            if line.startswith('__version__'):
                try:
                    version = line.split("'")[1]
                except IndexError:
                    pass
                break
    return version


def slurp(filename):
    try:
        with open(join(dirname(__file__), filename), encoding='utf8') as infile:
            return infile.read()
    except FileNotFoundError:
        pass  # needed at upload time, not install time


# meta
name = 'boombox'
repo_provider = 'github.com'
install_requires = (
    #~ 'ezenv',
)
extras_require = dict(
    mac=('pyobjc',),
    gstreamer=('PyGObject',),
    pyaudio=('pyaudio',),
)
# build entry for all extras:
from itertools import chain
extras_require['all'] = tuple(chain.from_iterable(extras_require.values()))


setup(
    name                = name,
    version             = get_version(name + '.py'),
    description         = 'A short cross-platform pure-python audio file player module.',
    author              = 'Mike Miller',
    author_email        = 'mixmastamyk@%s' % repo_provider,
    url                 = 'https://%s/mixmastamyk/%s' % (repo_provider, name),
    download_url        = 'https://%s/mixmastamyk/%s/get/default.tar.gz' % (repo_provider, name),
    license             = 'LGPLv3',
    py_modules           = (name,),

    extras_require      = extras_require,
    install_requires    = install_requires,
    python_requires     = '>=3.6',
    setup_requires      = install_requires,

    long_description    = slurp('readme.rst'),
    classifiers         = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Topic :: Utilities',
    ],
)
