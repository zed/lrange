"""Define `lrange.lrange` class

`xrange`, py3k's `range` analog for large integers

See help(lrange.lrange)

>>> r = lrange(2**100, 2**101, 2**100)
>>> len(r) == 1
True
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
"""

try: long
except NameError:
    long = int # Python 3.x

try: xrange
except NameError:
    xrange = range # Python 3.x

try: any
except NameError: # pragma: no cover
    def any(iterable): # for Python 2.4
        for i in iterable:
            if i:
                return True
        return False

import sys as _sys
if hasattr(_sys, "maxint"):
    _MAXINT = _sys.maxint
else:
    _MAXINT = _sys.maxsize # Python 3.x


def _toindex(arg):
    """Convert `arg` to integer type that could be used as an index.

    """
    for cls in (int, long):
        if isinstance(arg, cls): # allow int subclasses
           return int(arg)

    raise TypeError("'%s' object cannot be interpreted as an integer" % (
        type(arg).__name__,))


class lrange(object):
    """lrange([start,] stop[, step]) -> lrange object

    Return an iterator that generates the numbers in the range on demand.

    Pure Python implementation of py3k's `range()`.

    (I.e. it supports large integers)

    If `xrange` and py3k `range()` differ then prefer `xrange`'s behaviour

    Based on `[1]`_

    .. [1] http://svn.python.org/view/python/branches/py3k/Objects/rangeobject.c?view=markup

    >>> # on Python 2.6
    >>> N = 10**80
    >>> len(range(N, N+3))
    3
    >>> len(xrange(N, N+3)) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    OverflowError: long int too large to convert to int
    >>> len(lrange(N, N+3)) == 3
    True
    >>> xrange(N)           #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    OverflowError: long int too large to convert to int
    >>> lrange(N).length == N
    True
    """

    def __new__(cls, *args):
        nargs = len(args)
        if nargs == 1:
            stop = _toindex(args[0])
            start = 0
            step = 1
        elif nargs in (2, 3):
            start = _toindex(args[0])
            stop = _toindex(args[1])
            if nargs == 3:
                step = _toindex(args[2])
                if step == 0:
                    raise ValueError("lrange() arg 3 must not be zero")
            else:
                step = 1
        else:
            raise TypeError("lrange(): wrong number of arguments," +
                             " got %s" % (args,))

        r = super(lrange, cls).__new__(cls)
        assert start is not None
        assert stop is not None
        assert step is not None
        r._start, r._stop, r._step = start, stop, step
        return r

    def length(self):
        """len(self) might throw OverflowError, this method shouldn't."""
        if self._step > 0:
            lo, hi = self._start, self._stop
            step = self._step
        else:
            hi, lo = self._start, self._stop
            step = -self._step
            assert step

        if lo >= hi:
            return 0
        else:
            return (hi - lo - 1) // step + 1

    def __len__(self):
        L = self.length
        if L > _MAXINT:
            raise OverflowError(
                "cannot fit '%.200s' into an index-sized integer" % type(L).__name__)
        return int(L)

    def __bool__(self):
        return bool(self.length)

    __nonzero__ = __bool__

    length = property(length)

    def __getitem__(self, i):
        if i < 0:
            i = i + self.length
        if i < 0 or i >= self.length:
            raise IndexError("lrange object index out of range")

        return self._start + i * self._step

    def __repr__(self):
        if self._step == 1:
            return "%s(%r, %r)" % (
                self.__class__.__name__, self._start, self._stop)
        else:

            return "%s(%r, %r, %r)" % (
                self.__class__.__name__, self._start, self._stop, self._step)

    def __contains__(self, ob):
        if type(ob) not in (int, long, bool): # mimic py3k
            # perform iterative search
            return any(i == ob for i in self)

        # if long or bool
        if self._step > 0:
            inrange = self._start <= ob < self._stop
        else:
            assert self._step
            inrange = self._stop < ob <= self._start

        if not inrange:
            return False
        else:
            return ((ob - self._start) % self._step) == 0

    def __iter__(self):
        try:
            return iter(xrange(self._start, self._stop,
                               self._step)) # use `xrange`'s iterator
        except (NameError, OverflowError):
            return self._iterator()

    def _iterator(self):
        len_ = self.length
        i = 0
        while i < len_:
            yield self._start + i * self._step
            i += 1


    def __reversed__(self):
        len_ = self.length
        new_start = self._start + (len_ - 1) * self._step
        new_stop = self._start
        if self._step > 0:
            new_stop -= 1
        else:
            new_stop += 1
        return lrange(new_start, new_stop, -self._step)

    def __getnewargs__(self):
        return self._start, self._stop, self._step
