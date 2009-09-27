"""Unit-tests for lrange.lrange class.

Usage:

    $ python -W error test_lrange.py --with-doctest

Requires: nose (``$ easy_install nose``)
"""
import sys

from nose.tools import assert_raises, eq_ as eq, raises

from lrange import lrange


def eq_lrange(a, b):
    """Assert that `a` equals `b`.

    Where `a`, `b` are `lrange` objects
    """
    assert a._start == b._start
    assert a._stop == b._stop
    assert a._step == b._step
    assert a.length == b.length
    if a.length < 100:
        assert list(a) == list(b)
        try:
             assert list(a) == range(a._start, a._stop, a._step)
        except OverflowError:
            pass


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
        help(assert_raises)
        lrange(*map(int, args))
        assert_raises(TypeError, lrange, *args)
    _test(1.0)
    _test(1e10, 1e10)
    _test(1e1, 1e1)
    _test(-1, 2, 1.0)
    _test(1.0, 2)
    _test(1, 2, 1.0)
    _test(1e100, 1e101, 1e101)


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
        assert len(r) == 0
        L = list(r)
        assert len(L) == 0


def test_small_ints():
    for args in _get_short_lranges_args():
        ir, r = lrange(*args), xrange(*args)
        assert len(ir) == len(r)
        assert list(ir) == list(r)


def test_big_ints():
    N = 10**100
    for args, len_ in [
        [(N,), N],
        [(N, N+10), 10],
        [(N, N-10, -2), 5],
        ]:
        try:
            xrange(*args)
            assert 0
        except OverflowError:
            pass

        ir = lrange(*args)
        assert ir.length == len_
        try:
            assert ir.length == len(ir)
        except OverflowError:
            pass
        #
        ir[ir.length-1]
        #
        if len(args) >= 2:
            r = range(*args)
            assert list(ir) == r
            assert ir[ir.length-1] == r[-1]
            assert list(reversed(ir)) == list(reversed(r))
        #


def test_negative_index():
    assert lrange(10)[-1] == 9
    assert lrange(2**100+1)[-1] == 2**100


def test_reversed():
    for r in _get_lranges():
        if r.length > 1000: continue # skip long
        assert list(reversed(reversed(r))) == list(r)
        assert list(r) == range(r._start, r._stop, r._step)


def test_pickle():
    import pickle
    for r in _get_lranges():
        rp = pickle.loads(pickle.dumps(r))
        eq_lrange(rp, r)


def test_equility():
    for args in _get_lranges_args():
        a, b = lrange(*args), lrange(*args)
        assert a is not b
        assert a != b
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
                    assert lr.length == s

def test_new():
    assert repr(lrange(True)) == repr(lrange(1))
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
    lo, hi, step = sys.maxint-2, 4*sys.maxint+3, sys.maxint // 10
    lr = lrange(lo, hi, step)
    xr = lrange(sys.maxint/4, sys.maxint/2, sys.maxint // 10)
    assert list(lr) == list(range(lo, hi, step))


def test_getitem():
    r = lrange(sys.maxint-2, sys.maxint+3)
    L = []
    L[:] = r
    assert len(L) == len(r)
    assert L == list(r)


if __name__ == "__main__":
    import nose
    nose.main()
