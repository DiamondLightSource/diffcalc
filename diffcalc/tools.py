from nose.tools import assert_almost_equal #@UnresolvedImport
# This is in there, but is dynamically copied in from unittest.Testcase and is
# not seen by pydev.

def format_note(note):
    return " # %s" % note if note else ""

def assert_array_almost_equal(first, second, places=7, msg=None, note=None):
    assert len(first) == len(second), "%r != %r as lengths differ%s" % (first, second, format_note(note))
    for f, s in zip(first, second):
        assert_almost_equal(f, s, places, msg or "\n%r != \n%r within %i places%s" 
                            % (first, second, places, format_note(note)))

arrayeq_ = assert_array_almost_equal
        
def assert_2darray_almost_equal(first, second, places=7, msg=None, note=None):
    assert len(first) == len(second), "%r != %r as sizes differ%s" % (first, second, format_note(note))
    for f2, s2 in zip(first, second):
        assert len(f2) == len(s2), "%r != %r as sizes differ%s" % (first, second, format_note(note))
        for f, s in zip(f2, s2):
            message = "within %i places%s"%(places, format_note(note)) + '\n' + format_2darray(first, places) + "!=\n" + format_2darray(second, places)
            assert_almost_equal(f, s, places, msg or message)

def format_2darray(array, places):
    format = '% .' + str(places) + 'f'
    s = ""
    for row in array:
        line = [format%el for el in row]
        s += '[' + ', '.join(line) + ']\n'
    return s

def assert_matrix_almost_equal(first, second, places=7, msg=None, note=None):
    assert_2darray_almost_equal(first.array, second.array, places, msg)

 
def assert_dict_almost_equal(first, second, places=7, msg=None, note=None):
    assert set(first.keys()) == set(second.keys()), msg or ("%r != %r as keys differ%s" % (first, second, format_note(note)))
    keys = first.keys()
    keys.sort()
    for key in keys:
        f = first[key]
        s = second[key]
        if isinstance(f, float) or isinstance(s, float):
            assert_almost_equal(f, s, places, msg or ("For key %s, %r != %r within %i places%s" % (`key`, f, s, places, format_note(note))))
        else:
            if f != s:
                raise AssertionError("For key %s, %r != %r%s" % (`key`, f, s, format_note(note)))

def assert_second_dict_almost_in_first(value, expected, places=7, msg=None):
    value = value.copy()
    for key in value.keys():
        if key not in expected.keys():
            del value[key]
    assert_dict_almost_equal(value, expected, places=7, msg=None)
                
def assert_iterable_almost_equal(first, second, places=7, msg=None, note=None):
    assert len(first) == len(second), msg or ("%r != %r as lengths differ%s" % (first, second, format_note(note)))
    for f, s in zip(first, second):
        if isinstance(f, float) or isinstance(s, float):
            assert_almost_equal(f, s, places, msg)
        else:
            if f != s:
                raise AssertionError("%r != %r%s" % (f, s, format_note(note)))
        
matrixeq_ = assert_matrix_almost_equal