from nose.tools import assert_almost_equal  # @UnresolvedImport
from nose.tools import ok_

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix


def format_note(note):
    return " # %s" % note if note else ""


def assert_array_almost_equal(first, second, places=7, msg=None, note=None):
    err = "%r != %r as lengths differ%s" % (first, second, format_note(note))
    assert len(first) == len(second), err
    for f, s in zip(first, second):
        default_msg = (
            "\n%r != \n%r within %i places%s" % (format_array(first, places),
            format_array(second, places), places, format_note(note)))
        assert_almost_equal(f, s, places, msg or default_msg)


def format_array(a, places):
    fmt = '% .' + str(places) + 'f'
    return '(' + ', '.join((fmt % el) for el in a) + ')'


aneq_ = arrayeq_ = assert_array_almost_equal


def assert_2darray_almost_equal(first, second, places=7, msg=None, note=None):
    err = "%r != %r as sizes differ%s" % (first, second, format_note(note))
    assert len(first) == len(second), err
    for f2, s2 in zip(first, second):
        err = "%r != %r as sizes differ%s" % (first, second, format_note(note))
        assert len(f2) == len(s2), err
        for f, s in zip(f2, s2):
            message = "within %i places%s" % (places, format_note(note))
            message += '\n' + format_2darray(first, places) + "!=\n"
            message += format_2darray(second, places)
            assert_almost_equal(f, s, places, msg or message)


def format_2darray(array, places):
    fmt = '% .' + str(places) + 'f'
    s = ""
    for row in array:
        line = [fmt % el for el in row]
        s += '[' + ', '.join(line) + ']\n'
    return s


def _array(m):
    if isinstance(m, matrix):  # numpy
        return m.tolist()
    else:                       # assume Jama
        return m.array


def assert_matrix_almost_equal(first, second, places=7, msg=None, note=None):
    assert_2darray_almost_equal(_array(first), _array(second), places, msg)


def assert_dict_almost_equal(first, second, places=7, msg=None, note=None):
    def_msg = "%r != %r as keys differ%s" % (first, second, format_note(note))
    assert set(first.keys()) == set(second.keys()), msg or def_msg
    keys = first.keys()
    keys.sort()
    for key in keys:
        f = first[key]
        s = second[key]
        if isinstance(f, float) or isinstance(s, float):
            def_msg = ("For key %s, %r != %r within %i places%s" %
                       (repr(key), f, s, places, format_note(note)))
            assert_almost_equal(f, s, places, msg or def_msg)
        else:
            if f != s:
                raise AssertionError(
                    "For key %s, %r != %r%s" %
                    (repr(key), f, s, format_note(note)))


def assert_second_dict_almost_in_first(value, expected, places=7, msg=None):
    value = value.copy()
    for key in value.keys():
        if key not in expected.keys():
            del value[key]
    assert_dict_almost_equal(value, expected, places=7, msg=None)


def assert_iterable_almost_equal(first, second, places=7, msg=None, note=None):
    def_msg = ("%r != %r as lengths differ%s" %
               (first, second, format_note(note)))
    assert len(first) == len(second), msg or def_msg
    for f, s in zip(first, second):
        if isinstance(f, float) or isinstance(s, float):
            assert_almost_equal(f, s, places, msg)
        else:
            if f != s:
                raise AssertionError("%r != %r%s" % (f, s, format_note(note)))


mneq_ = matrixeq_ = assert_matrix_almost_equal


def meq_(a, b):
    ok_((a == b).all(), '\n%s\n  !=\n%s' % (a, b))
