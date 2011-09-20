from nose.tools import assert_almost_equal #@UnresolvedImport
# This is in there, but is dynamically copied in from unittest.Testcase and is
# not seen by pydev.


def assert_array_almost_equal(first, second, places=7, msg=None):
    assert len(first) == len(second), "%r != %r as lengths differ" % (first, second)
    for f, s in zip(first, second):
        assert_almost_equal(f, s, places, msg or "%r != %r within %i places" 
                            % (first, second, places))

arrayeq_ = assert_array_almost_equal
        
def assert_2darray_almost_equal(first, second, places=7, msg=None):
    assert len(first) == len(second), "%r != %r as sizes differ" % (first, second)
    for f2, s2 in zip(first, second):
        assert len(f2) == len(s2), "%r != %r as sizes differ" % (first, second)
        for f, s in zip(f2, s2):
            assert_almost_equal(f, s, places, msg or "%r != %r within %i places"
                                 % (first, second, places))


def assert_matrix_almost_equal(first, second, places=7, msg=None):
    assert_2darray_almost_equal(first.array, second.array, places, msg)

 
def assert_dict_almost_equal(first, second, places=7, msg=None):
    assert set(first.keys()) == set(second.keys()), msg or ("%r != %r as keys differ" % (first, second))
    keys = first.keys()
    keys.sort()
    for key in keys:
        f = first[key]
        s = second[key]
        if isinstance(f, float) or isinstance(s, float):
            assert_almost_equal(f, s, places, msg or ("For key %s, %r != %r within %i places" % (`key`, f, s, places)))
        else:
            if f != s:
                raise AssertionError("For key %s, %r != %r" % (`key`, f, s))
            
def assert_iterable_almost_equal(first, second, places=7, msg=None):
    assert len(first) == len(second), msg or ("%r != %r as lengths differ" % (first, second))
    for f, s in zip(first, second):
        if isinstance(f, float) or isinstance(s, float):
            assert_almost_equal(f, s, places, msg)
        else:
            if f != s:
                raise AssertionError("%r != %r" % (f, s))
        
            
matrixeq_ = assert_matrix_almost_equal

