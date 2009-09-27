"""Define `lrange.lrange` class

`xrange`, py3k's `range` analog for large integers

See help(lrange.lrange)

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
"""


def toindex(arg):
    """Convert `arg` to integer type that could be used as an index.

    """
    if not any(isinstance(arg, cls) for cls in (long, int, bool)):
        raise TypeError("'%s' object cannot be interpreted as an integer" % (
            type(arg).__name__,))
    return int(arg)


class lrange(object):
    """lrange([start,] stop[, step]) -> lrange object

    Return an iterator that generates the numbers in the range on demand.
    Return `xrange` for small integers

    Pure Python implementation of py3k's `range()`.

    (I.e. it supports large integers)

    If `xrange` and py3k `range()` differ then prefer `xrange`'s behaviour

    Based on `[1]`_

    .. [1] http://svn.python.org/view/python/branches/py3k/Objects/rangeobject.c?view=markup

    >>> # on Python 2.6
    >>> N = 10**80
    >>> len(range(N, N+3))
    3
    >>> len(xrange(N, N+3))
    Traceback (most recent call last):
    ...
    OverflowError: long int too large to convert to int
    >>> len(lrange(N, N+3))
    3
    >>> xrange(N)
    Traceback (most recent call last):
    ...
    OverflowError: long int too large to convert to int
    >>> lrange(N).length() == N
    True
    """
    def __new__(cls, *args):
        try: return xrange(*args) # use `xrange` for small integers
        except OverflowError: pass

        nargs = len(args)
        if nargs == 1:
            stop = toindex(args[0])
            start = 0
            step = 1
        elif nargs in (2, 3):
            start = toindex(args[0])
            stop = toindex(args[1])
            if nargs == 3:
                step = args[2]
                if step is None:
                    step = 1

                step = toindex(step)
                if step == 0:
                    raise ValueError("lrange() arg 3 must not be zero")
            else:
                step = 1
        else:
            raise ValueError("lrange(): wrong number of arguments," +
                             " got %s" % args)

        r = super(lrange, cls).__new__(cls)
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

    __len__ = length

    def __getitem__(self, i): # for L[:] = lrange(..)
        if i < 0:
            i = i + self.length()
        if i < 0 or i >= self.length():
            raise IndexError("lrange object index out of range")

        return self._start + i * self._step

    def __repr__(self):
        if self._step == 1:
            return "lrange(%r, %r)" % (self._start, self._stop)
        else:

            return "lrange(%r, %r, %r)" % (
                self._start, self._stop, self._step)

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
        len_ = self.length()
        i = 0
        while i < len_:
            yield self._start + i * self._step
            i += 1

    def __reversed__(self):
        len_ = self.length()
        new_start = self._start + (len_ - 1) * self._step
        new_stop = self._start
        if self._step > 0:
            new_stop -= 1
        else:
            new_stop += 1
        return lrange(new_start, new_stop, -self._step)
