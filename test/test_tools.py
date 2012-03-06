from test.tools import assert_almost_equal, assert_array_almost_equal, \
    assert_2darray_almost_equal, assert_matrix_almost_equal, \
    assert_dict_almost_equal
from nose.tools import eq_  # @UnresolvedImport

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix


class test_assert_almost_equal():

    def test_fails(self):
        try:
            assert_almost_equal(1, 1.0000001)
            assert False
        except AssertionError:
#            eq_(e.args[0], '1 != 1.0000001000000001 within 7 places')
            pass

    def test__passes(self):
        assert_almost_equal(1, 1.00000001)
        assert_almost_equal(1, 1.0000001, 6)


class test_assert_array_almost_equal():

    def test__passes(self):
        assert_array_almost_equal((1, 2, 3), (1.00000001, 2, 3.))
        assert_array_almost_equal((1, 2, 3), (1.0000001, 2, 3.), 6)
        assert_array_almost_equal((1, 2, 3), [1, 2, 3])
        assert_array_almost_equal((), ())
        assert_array_almost_equal([], ())

    def test_wrong_length(self):
        try:
            assert_array_almost_equal((1, 2, 3), (1, 2))
            assert False
        except AssertionError, e:
            eq_(e.args[0], '(1, 2, 3) != (1, 2) as lengths differ')

    def test_wrong_value(self):
        try:
            assert_array_almost_equal((3, 2, 1), (3, 2, 1.0000001))
            assert False
        except AssertionError:
            pass


class test_assert_2darray_almost_equal():

    def test__passes(self):
        assert_2darray_almost_equal(((1, 2), (3, 4)),
                                    ((1.00000001, 2), (3, 4)))
        assert_2darray_almost_equal(((1, 2), (3, 4)),
                                    ((1.0000001, 2), (3, 4)), 6)
        assert_2darray_almost_equal(((1, 2), (3, 4)),
                                    [(1, 2), [3, 4]])
        assert_2darray_almost_equal(((), ()), ((), ()))
        assert_2darray_almost_equal([(), []], ([], ()))

    def test_wrong_length(self):
        try:
            assert_2darray_almost_equal(((1, 2), (3, 4)), ((1, 2), (3, 4, 5)))
            assert False
        except AssertionError, e:
            eq_(e.args[0],
                '((1, 2), (3, 4)) != ((1, 2), (3, 4, 5)) as sizes differ')

    def test_wrong_value(self):
        try:
            assert_2darray_almost_equal(((1, 2), (3, 4)),
                                        ((1.0000001, 2), (3, 4)))
            assert False
        except AssertionError:
            pass


class test_assert_matrix_almost_equal():

    def test__passes(self):
        assert_matrix_almost_equal(matrix([[1, 2], [3, 4]]),
                                   matrix([[1.00000001, 2], [3, 4]]))
        assert_matrix_almost_equal(matrix([[1, 2], [3, 4]]),
                                   matrix([[1.0000001, 2], [3, 4]]), 6)

    def test_wrong_length(self):
        try:
            assert_matrix_almost_equal(matrix([[1, 2], [3, 4]]),
                                       matrix([[1, 2, 3], [4, 5, 6]]))
            assert False
        except AssertionError:
            pass

    def test_wrong_value(self):
        try:
            assert_matrix_almost_equal(matrix([[1, 2], [3, 4]]),
                                        matrix([[1.0000001, 2], [3, 4]]))
            assert False
        except AssertionError:
            pass


class test_assert_dict_almost_equal():

    def test__passes(self):
        assert_dict_almost_equal({}, {})
        assert_dict_almost_equal({'a': 1}, {'a': 1})
        assert_dict_almost_equal({'a': 1.}, {'a': 1.})
        assert_dict_almost_equal({'a': 1.00000001}, {'a': 1.00000001})

    def test_wrong_keys(self):
        try:
            assert_dict_almost_equal({'a': 1}, {'a': 1, 'b': 2})
            assert False
        except AssertionError:
            pass

    def test_wrong_object(self):
        try:
            assert_dict_almost_equal({'a': 1}, {'a': '1'})
            assert False
        except AssertionError, e:
            eq_(e.args[0], "For key 'a', 1 != '1'")

    def test_wrong_int(self):
        try:
            assert_dict_almost_equal({'a': 1}, {'a': 2})
            assert False
        except AssertionError, e:
            eq_(e.args[0], "For key 'a', 1 != 2")

    def test_wrong_float1(self):
        try:
            assert_dict_almost_equal({'a': 1.}, {'a': 2.})
            assert False
        except AssertionError, e:
            eq_(e.args[0], "For key 'a', 1.0 != 2.0 within 7 places")

    def test_wrong_float2(self):
        try:
            assert_dict_almost_equal({'a': 1}, {'a': 2.})
            assert False
        except AssertionError, e:
            eq_(e.args[0], "For key 'a', 1 != 2.0 within 7 places")

    def test_wrong_float3(self):
        try:
            assert_dict_almost_equal({'a': 1.}, {'a': 2})
            assert False
        except AssertionError, e:
            eq_(e.args[0], "For key 'a', 1.0 != 2 within 7 places")

    def test_okay_differing_types1(self):
        assert_dict_almost_equal({'a': 1.}, {'a': 1})

    def test_okay_differing_types2(self):
        assert_dict_almost_equal({'a': 1}, {'a': 1.})
