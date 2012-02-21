from nose.tools import eq_, ok_, assert_almost_equal  # @UnresolvedImport
from nose.plugins.skip import SkipTest
from diffcalc.tools import assert_2darray_almost_equal

try:
    import numpy
    __NUMPY_AVAILABLE__ = True
except ImportError:
    __NUMPY_AVAILABLE__ = False

try:
    import numjy
    __NUMJY_AVAILABLE__ = True
except ImportError:
    __NUMJY_AVAILABLE__ = False


def meq_(a, b):
    ok_((a == b).all(), '\n%s\n  !=\n%s' % (a, b))


class _TestNumpyMatrix():

    def m(self, args):
        raise NotImplementedError()

    def test__init__(self):
        m = self.m([[1, 2], [3, 4]])
        meq_(self.m('1 2;3 4'), m)
        meq_(self.m('1 2; 3 4'), m)
        meq_(self.m('1, 2; 3, 4'), m)
        meq_(self.m('1, 2; 3 4'), m)
        meq_(self.m('1 ,  2;  3  4  '), m)

    def test_shape(self):
        shape = self.m('1 2 3; 4 5 6').shape
        eq_(len(shape), 2)
        eq_(shape[0], 2)
        eq_(shape[1], 3)

    def test_len(self):
        eq_(len(self.m('1 2 3; 4 5 6')), 2)

    def test_2dslice(self):
        m = self.m('0 1; 10 11')
        eq_(m[0, 0], 00)
        eq_(m[0, 1], 01)
        eq_(m[1, 0], 10)
        eq_(m[1, 1], 11)

    def test_set_2dslice(self):
        m = self.m('1 2; 3 4')
        m[1, 1] = 40
        meq_(m, self.m('1 2; 3 40'))

    def test_tolist(self):
        l = [[1, 2], [3, 4]]
        assert_2darray_almost_equal(self.m(l).tolist(), l)

    def test__str__(self):
        eq_(str(self.m('1.234 2.; 3.1 4.')),
            '[[ 1.234  2.   ]\n [ 3.1    4.   ]]')

    def test__repr__(self):
        eq_(repr(self.m('1. 2.; 3. 4.')),
            'matrix([[ 1.,  2.],\n        [ 3.,  4.]])')

    def test_all(self):
        ok_(self.m([[True, True], [True, True]]).all())
        ok_(not self.m([[True, False], [True, True]]).all())

    def test_eq(self):
        meq_(self.m('1 2; 3 4'),
             self.m('1 2; 3 4.'))

    def test_eq_false(self):
        ok_(not (self.m('1 2; 3 4') == self.m('1 2; 3 5')).all())

    def test__eq__(self):
        meq_(self.m('1 2; 3 4') == self.m('1 2; 3 4.1'),
             self.m([[True, True], [True, False]]))

    def test__mul__matrix(self):
        meq_(self.m('1 2; 3 4') * self.m('5 6; 7 8'),
             self.m('19 22; 43 50'))

    def test__mul__vector(self):
        meq_(self.m('1 2; 3 4') * self.m('5; 7'),
             self.m('19; 43'))

    def test__mul__scaler(self):
        meq_(self.m('1, 2; 3, 4') * 10,
             self.m('10 20; 30 40'))

    def test__sum__(self):
        meq_(self.m('1 2; 3 4') + self.m('5 6; 7 8'),
             self.m(' 6 8; 10 12'))

    def test__sum__scaler(self):
        meq_(self.m('1 2; 3 4') + 10,
             self.m('11 12; 13 14'))

    def test__sub__(self):
        meq_(self.m('1 2; 3 4') - self.m('5 6; 7 8'),
             self.m('-4 -4; -4 -4'))

    def test__sub__scaler(self):
        meq_(self.m('11 12; 13 14') - 10,
             self.m('1 2; 3 4'))

    def test__div__(self):
        r = self.m('1 2; 3 4') / self.m('5. 6.; 7. 8.')
        assert_almost_equal(r[0, 0], .2)
        assert_almost_equal(r[0, 1], .33333333)
        assert_almost_equal(r[1, 0], 0.42857143)
        assert_almost_equal(r[1, 1], .5)

    def test__div__scaler(self):
        meq_(self.m('10 20; 30 40') / 10.,
             self.m('1 2; 3 4'))

    def test_I(self):
        inverse = self.m('1 2; 3 4').I
        assert_almost_equal(inverse[0, 0], -2)
        assert_almost_equal(inverse[0, 1], 1)
        assert_almost_equal(inverse[1, 0], 1.5)
        assert_almost_equal(inverse[1, 1], -.5)

    def test_T(self):
        meq_(self.m('1 2; 3 4').T,
             self.m('1 3; 2 4'))


class _TestLinalg():

    def matrix(self, args):
        raise NotImplementedError()

    def norm(self, args):
        raise NotImplementedError()

    def test_norm_frobenius(self):
        m1 = self.matrix('1 1 1; 1 1 1; 1 1 1')
        assert_almost_equal(self.norm(m1), 3, places=13)
        m2 = self.matrix('1 2 3; 4 5 6; 7 8 9')
        assert_almost_equal(self.norm(m2), 16.881943016134134, places=13)


class _TestNumpy():

    def matrix(self, args):
        raise NotImplementedError()

    def hstack(self, args):
        raise NotImplementedError()

    def test_hstack(self):
        v1 = self.matrix('1;2;3')
        v2 = self.matrix('4;5;6')
        v3 = self.matrix('7;8;9')
        meq_(self.hstack([v1, v2, v3]), self.matrix('1,4,7;2,5,8;3,6,9'))


if __NUMPY_AVAILABLE__:

    class TestNumpyMatrix(_TestNumpyMatrix):

        def m(self, args):
            return numpy.matrix(args)

    class TestLinalgNumpy(_TestLinalg):

        def matrix(self, args):
            return numpy.matrix(args)

        def norm(self, args):
            return numpy.linalg.norm(args)

    class TestNumpy(_TestNumpy):

        def matrix(self, args):
            return numpy.matrix(args)

        def hstack(self, args):
            return numpy.hstack(args)


if __NUMJY_AVAILABLE__:

    class TestNumjyMatrix(_TestNumpyMatrix):

        def m(self, args):
            return numjy.matrix(args)

        def test__str__(self):
            eq_(str(self.m('1.234 2.0; 3.1 4.0')),
                '[[1.234  2.0]\n [3.1  4.0]]')

        def test__repr__(self):
            print repr(self.m('1. 2.; 3. 4.'))
            eq_(repr(self.m('1. 2.; 3. 4.')),
                'matrix([[1.0  2.0]\n        [3.0  4.0]])')

        def test__div__(self):
            raise SkipTest()

    class TestLinalgNumjy(_TestLinalg):

        def matrix(self, args):
            return numjy.matrix(args)

        def norm(self, args):
            return numjy.linalg.norm(args)

        def hstack(self, args):
            return numjy.hstack(args)

    class TestNumjy(_TestNumpy):

        def matrix(self, args):
            return numjy.matrix(args)

        def hstack(self, args):
            return numjy.hstack(args)
