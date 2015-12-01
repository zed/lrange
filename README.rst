lrange - unlimited xrange in pure Python
========================================

.. image:: https://img.shields.io/coveralls/zed/lrange.svg
    :target: https://coveralls.io/r/zed/lrange

.. image:: https://img.shields.io/travis/zed/lrange/master.svg
    :target: https://travis-ci.org/zed/lrange

`lrange` is a lazy range function for Python 2.x or `xrange` drop-in
replacement for long integers.

`lrange` is a pure Python analog of the builtin `range` function from
Python 3.x.

    >>> from lrange import lrange
    >>> r = lrange(2**100, 2**101, 2**100)
    >>> len(r)
    1
    >>> for i in r:
    ...     print i,
    1267650600228229401496703205376
    >>> for i in r:
    ...     print i,
    1267650600228229401496703205376
    >>> 2**100 in r
    True
    >>> r[0], r[-1]
    (1267650600228229401496703205376L, 1267650600228229401496703205376L)
    >>> L = list(r)
    >>> L2 = [1, 2, 3]
    >>> L2[:] = r
    >>> L == L2 == [2**100]
    True

Files are licensed under the MIT License. See the file MIT-LICENSE.txt
for details.

The latest version is at https://github.com/zed/lrange/
