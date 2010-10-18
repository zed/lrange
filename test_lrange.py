"""Unit-tests for lrange.lrange class.

Usage:

    $ python -W error test_lrange.py --with-doctest

Requires: nose (``$ pip install nose``)
"""
from __future__ import nested_scopes
import pickle
import sys
import unittest

try: long
except NameError:
    long = int           # Python 3.x

try: xrange
except NameError:
    xrange = range       # Python 3.x

from nose import SkipTest
from nose.tools import assert_raises, eq_ as eq, make_decorator, raises

from lrange import lrange


if hasattr(sys, "maxint"):
    MAXINT = sys.maxint
else:
    MAXINT = sys.maxsize # Python 3.x

BIGINT = 10**200


def skipif(predicate, msg=None):
    """Skip the test if `predicate()` is true."""
    if msg is None:
        msg = predicate.__name__

    def decorator(test_fun):
        @make_decorator(test_fun)
        def wrapper(*args, **kwargs):
            if not predicate():
                return test_fun(*args, **kwargs)
            else:
                raise SkipTest(msg)
        return wrapper
    return decorator


def ispypy():
    """Whether the running interpreter is pypy."""
    return hasattr(sys, 'pypy_version_info')


def isjython():
    """Whether the running interpreter is jython."""
    return sys.platform.startswith('java')

def eq_range(a, start, stop, step):
    """Assert that `a` is a range defined by `start`, `stop`, `step`."""
    i = start
    for j in a:
        eq(j, i)
        i += step


def eq_lrange(a, b):
    """Assert that `a` equals `b`.

    Where `a`, `b` are `lrange` objects
    """
    eq(a._start, b._start)
    eq(a._stop, b._stop)
    eq(a._step, b._step)
    eq(a.length, b.length)
    
    if a.length < 100: # test equility for small ranges
        eq(list(a), list(b))
        eq_range(a, a._start, a._stop, a._step)


def _get_short_lranges_args():
    # perl -E'local $,= q/ /; $n=100; for (1..20)
    # >    { say map {int(-$n + 2*$n*rand)} 0..int(3*rand) }'
    input_args = """\
    67
    -11
    51
    -36
    -15 38 19
    43 -58 79
    -91 -71
    -56
    3 51
    -23 -63
    -80 13 -30
    24
    -14 49
    10 73
    31
    38 66
    -22 20 -81
    79 5 84
    44
    40 49
    """
    return [[int(arg) for arg in line.split()]
            for line in input_args.splitlines() if line.strip()]


def _get_lranges_args():
    N = 2**100
    return [(start, stop, step)
            for start in range(-2*N, 2*N, N//2+1)
            for stop in range(-4*N, 10*N, N+1)
            for step in range(-N//2, N, N//8+1)]


def _get_short_lranges():
    return [lrange(*args) for args in _get_short_lranges_args()]


def _get_lranges():
    return (_get_short_lranges() +
            [lrange(*args) for args in _get_lranges_args()])


@raises(TypeError)
def test_kwarg():
    lrange(stop=10)


def test_float_arg():
    def _test(*args):
        lrange(*map(int, args)) # args work as ints
        assert_raises(TypeError, lrange, *args) # args raise TypeError as floats
    _test(1.0)
    _test(1e10, 1e10)
    _test(1e1, 1e1)
    _test(-1, 2, 1.0)
    _test(1.0, 2)
    _test(1, 2, 1.0)
    _test(1e100, 1e101, 1e101)


def test_int_subclass_args():
    class Int(int):
        pass
    class Long(long):
        pass

    for args in [ (Int(10,),),
                  (Int(1), Int(2), Int(1)),
                  (Long(1),),
                  (1, 2, Long(1e100)),
                  (True,),]:
        lrange(*args)


@raises(TypeError)
def test_empty_args():
    lrange()


def test_empty_range():
    for args in (
        "-3",
        "1 3 -1",
        "1 1",
        "1 1 1",
        "-3 -4",
        "-3 -2 -1",
        "-3 -3 -1",
        "-3 -3",
        ):
        r = lrange(*[int(a) for a in args.split()])
        eq(len(r), 0)
        L = list(r)
        eq(len(L), 0)


def test_small_ints():
    for args in _get_short_lranges_args():
        ir, r = lrange(*args), xrange(*args)
        eq(len(ir), len(r))
        eq(list(ir), list(r))


def test_len_type():
    ir = lrange(10)
    eq(type(len(ir)), int)
    eq(type(len(xrange(10))), int)
    eq(type(len(range(10))), int)


def test_big_ints():
    N = 10**100
    for args, len_ in [
        [(N,), N],
        [(N, N+10), 10],
        [(N, N-10, -2), 5],
        ]:
        ir = lrange(*args)
        #
        ir[ir.length-1]
        #
        if len(args) >= 2:
            r = range(*args)
            eq(list(ir), list(r))
            eq(ir[ir.length-1], r[-1])
            eq(list(reversed(ir)), list(reversed(r)))


def test_negative_index():
    eq(lrange(10)[-1], 9)
    eq(lrange(2**100+1)[-1], 2**100)


def test_reversed():
    for r in _get_lranges():
        if r.length > 1000: continue # skip long
        eq(list(reversed(list(reversed(r)))), list(r))
        eq_range(r, r._start, r._stop, r._step)


def test_pickle_all_but_highest_protocol():    
    for proto in range(pickle.HIGHEST_PROTOCOL):
        yield _test_pickle, proto

@skipif(ispypy, msg="known failure. It causes 'segmentation fault' with pypy-c")
def test_pickle_highest_protocol():
    yield _test_pickle, pickle.HIGHEST_PROTOCOL
    yield _test_pickle, -1
    yield _test_pickle, None


def _test_pickle(proto):
    for r in _get_lranges():
        if proto is None:
            rp = pickle.loads(pickle.dumps(r))
        else:
            rp = pickle.loads(pickle.dumps(r, proto))
        eq_lrange(rp, r)


def test_equility():
    for args in _get_lranges_args():
        a, b = lrange(*args), lrange(*args)
        assert a is not b
        assert a != b
        eq(a.length, b.length)
        if a.length < 1000: # skip long
            eq(list(a), list(b), (a, b))
        eq_lrange(a, b)


def test_contains():
    class IntSubclass(int):
        pass

    r10 = lrange(10)
    for i in range(10):
        assert i in r10
        assert IntSubclass(i) in r10

    assert 10 not in r10
    assert -1 not in r10
    assert IntSubclass(10) not in r10
    assert IntSubclass(-1) not in r10


def test_repr():
    for r in _get_lranges():
        eq_lrange(eval(repr(r)), r)


class _indices(object):
    def __getitem__(self, slices):
        # make sure slices is iterable
        try: slices = iter(slices)
        except TypeError:
            slices = [slices]
        # behaviour for short and long integers must be the same
        for N in (None, 2**101):
            for s in slices:
                if type(s) == slice:
                    start, stop, step = s.start, s.stop, s.step
                    if N is not None:
                        start = start and start+N
                        stop = stop and stop+N
                        step = step
                    # try from 0 to 3 arguments
                    for args in [(), (stop,), (start, stop),
                                 (start, stop, step)]:
                        try:
                            lr = lrange(*args)
                            if len(args) == 1:
                                nstart, nstep, nstop = 0, 1, stop
                                assert stop is not None
                            if len(args) == 2:
                                nstart, nstop, nstep = start, stop, 1
                                assert start is not None
                                assert stop is not None
                            if len(args) == 3:
                                nstart, nstop, nstep = start, stop, step
                                assert start is not None
                                assert stop is not None
                                assert step is not None
                            assert 0 <= len(args) < 4

                            eq(lr._start, nstart)
                            eq(lr._stop, nstop)
                            eq(lr._step, nstep)
                            eq(list(lr), list(range(nstart, nstop, nstep)))

                        except TypeError:
                            # expected if any of the arguments is None
                            if len(args) > 0:
                                assert start is None or stop is None or \
                                       step is None
                else: # s is not slice
                    assert s is not None
                    if N is not None:
                        s = s + N
                    lr = lrange(s)
                    eq(lr.length, s)

def test_new():
    eq(repr(lrange(True)), repr(lrange(1)))
    #
    try:
        lrange(None)
        assert 0
    except TypeError:
        pass
    #
    _indices()[3,4:,:5,6:7,7:8,8:13:2,:,-1:,:-2,10:6:-2,::11,::]
    _indices()[0,0:,:0,0:0]

@raises(ValueError)
def test_zero_step():
    _indices()[1:2:0]

def test_overflow():
    lo, hi, step = MAXINT-2, 4*MAXINT+3, MAXINT // 10
    lr = lrange(lo, hi, step)
    xr = lrange(MAXINT//4, MAXINT//2, MAXINT // 10)
    eq(list(lr), list(range(lo, hi, step)))


def test_getitem():
    r = lrange(MAXINT-2, MAXINT+3)
    L = []
    L[:] = r
    eq(len(L), len(r))
    eq(L, list(r))


class TestBIGINT(unittest.TestCase):

    def setUp(self):
        self.lr = lrange(BIGINT)

    def test_big_length(self):
        eq(self.lr.length, BIGINT)

    @raises(OverflowError)
    def test_overflow_len(self):
        len(self.lr)

    def tearDown(self):
        self.lr = None


if __name__ == "__main__":
    import nose
    sys.exit(nose.main())
