import os

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup


def read_file(relpath):
    return open(os.path.join(os.path.dirname(__file__), relpath)).read()

_readme_lines = read_file("README.rst").splitlines()

CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Software Development :: Libraries :: Python Modules
"""

NAME = 'lrange'
VERSION = '1.0.0'
DESCRIPTION = _readme_lines[0]
LONG_DESCRIPTION = "\n".join(_readme_lines[2:])
URL = "http://github.com/zed/lrange/"
DOWNLOAD_URL = ("http://pypi.python.org/packages/source/l/lrange/"
                "lrange-%s.tar.gz" % (VERSION,))
LICENSE = 'MIT'
CLASSIFIERS = list(filter(len, CLASSIFIERS.split('\n')))
AUTHOR = "zed"
AUTHOR_EMAIL = "arn.zart+zed@gmail.com"
PLATFORMS = ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    platforms=PLATFORMS,
    # NOTE: setup.py test might fail on the first attempt
    tests_require=['nose'],
    test_suite="nose.collector",
    py_modules=[NAME],
    provides=[NAME],
)
