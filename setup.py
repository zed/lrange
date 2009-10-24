import os

try: import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup

def read_file(relpath):
    return open(os.path.join(os.path.dirname(__file__), relpath)).read()

_readme_lines = read_file("README.rst").splitlines()

CLASSIFIERS = """\
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
License :: OSI Approved
Programming Language :: Python
Topic :: Software Development
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

NAME             = 'lrange'
VERSION          = '0.0.2.dev'
DESCRIPTION      = _readme_lines[0]
LONG_DESCRIPTION = "\n".join(_readme_lines[2:])
URL              = "http://github.com/zed/lrange/"
LICENSE          = 'MIT'
CLASSIFIERS      = filter(len, CLASSIFIERS.split('\n'))
AUTHOR           = "zed"
AUTHOR_EMAIL     = "arn.zart+zed@gmail.com"
PLATFORMS        = ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    platforms=PLATFORMS,
    tests_require=['nose'],
    test_suite="nose.collector",      # for ``setup.py test`` command
    py_modules=[NAME],
)
