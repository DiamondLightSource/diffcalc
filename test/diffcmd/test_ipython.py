from nose.tools import assert_sequence_equal  # @UnresolvedImport
from nose.tools import eq_
from nose import SkipTest

try:
    import IPython.core.magic  # @UnusedImport
    from diffcmd.ipython import parse
    IPYTHON = True
except ImportError:
    IPYTHON = False

class CallableNamedObject(object):
    
    def __init__(self, name, val):
        self._name = name
        self._val = val
        
    def method(self):
        return self._val
        
    def __repr__(self):
        return self._name
    
    def __call__(self):
        return self._val
    

o1 = CallableNamedObject('o1', 1)
o2 = CallableNamedObject('o2', 2)
o3 = CallableNamedObject('o3', 3)
c = 4
d = {
     'o1' : o1,
     'o2' : o2,
     'o3' : o3,
     'c' : 4
     }
       
         
def check(s, *expected):
    assert_sequence_equal(parse(s, d), expected)    


def assert_raises_syntax_error_with_message(msg, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        raise AssertionError()
    except SyntaxError as e:
        eq_(e.message, msg)



def setup_module():
    if not IPYTHON:
        raise SkipTest('ipython not available')
    
    
def test_parse_spaces():
    check('')
    check(' ')
    check('  ')

def test_parse_commas():
    assert_raises_syntax_error_with_message(
        'unexpected comma', parse, '1 2, 3', d)
    
def test_parse_numbers():
    check('1', 1)
    check('10', 10)
    check('10 2 3', 10, 2, 3)
    
def test_parse_negative_numbers():
    check('-1', -1)
    check('-10', -10)
    check('-10 2 -3', -10, 2, -3)

def test_parse_negative_number_with_space_between_sign_and_digit():
    msg = 'could not evaluate: "-"'
    assert_raises_syntax_error_with_message(msg, parse, '- 1', d)
    assert_raises_syntax_error_with_message(msg, parse, '1 - 1', d)

def test_parse_strings():
    check("'s1'", 's1')
    check("'s1' 's2'", 's1', 's2')
    check('"s1"', 's1')
    check('"s1" "s2"', 's1', 's2')

def test_parse_strings_containing_spaces():
    check("'ab cd'", 'ab cd')
    check("' ab cd '", ' ab cd ')
    
def test_parse_strings_containing_commas():
    check("'ab,cd'", 'ab,cd')
    check("', ab, cd, '", ', ab, cd, ')

def test_parse_strings_containing_hashes():
    check("'ab #cd'", 'ab #cd')
    check("' ab cd# '", ' ab cd# ')

def test_parse_strings_containing_strings():
    check(''' 1 'ab cd' 2''', 1, 'ab cd', 2)
    check(''' 1 '"ab" cd' 2''', 1, '"ab" cd', 2)

def test_parse_strings_containing_square_brackets():
    check("'ab[cd'", 'ab[cd')
    check("'[ ab cd ]'", '[ ab cd ]')
    
def test_parse_objects_and_numbers():
    check('o1', o1)
    check('c', 4)
    check('o1 o2', o1, o2)
    check('1 o1 o2 2 c', 1, o1, o2, 2, 4)

def test_parse_numbers_with_math():
    check('1+1', 2)
    check('-1 1-1 1 1+1', -1, 0, 1, 2)

def test_parse_callables_and_methods():
    check('o1()', 1)
    check('o1.method()', 1)
    
def test_parse_objects_numbers_and_strings():
    check(" o1 's2'", o1, 's2')
    check("1 's1' 's2' -2 o2", 1, 's1', 's2', -2, o2)
    
def test_parse_objects_and_numbers_and_extra_spaces():
    check('  o1   ', o1)
    check(' o1  o2 ', o1, o2)
    check('1 o1  o2   -2   ', 1, o1, o2, -2)

def test_parse_lists():
    check('[]', [])
    check('[1]', [1])
    check('[-1 2 3]', [-1, 2, 3])
    check('[1 2 -3][4]', [1, 2, -3], [4])
    check('[1 2 3][4 -5]', [1, 2, 3], [4, -5])
    
def test_parse_nested_lists():
    check('[[]]', [[]])
    check('[[1]]', [[1]])
    check('[[1 2 3]]', [[1, 2, 3]])
    check('[[1 2 3] [4 5 6]]', [[1, 2, 3], [4, 5, 6]])
    check('[[1 2 3][4 5 6]]', [[1, 2, 3], [4, 5, 6]])
    check('[[1 2 3][4 5 [6 7]]]', [[1, 2, 3], [4, 5, [6, 7]]])

def test_parse_lists_and_others():
    check('[[]]', [[]])
    check('[[o1]]', [[o1]])
    check('[[o1 o2() -3]]', [[o1, 2, -3]])
    
def test_parse_unexpected_list_closure():
    msg = 'could not evaluate: "1, 2], 3"'
    assert_raises_syntax_error_with_message(msg, parse, '1 2] 3', d)
    assert_raises_syntax_error_with_message(msg, parse, '1 2 ] 3', d)
    assert_raises_syntax_error_with_message(msg, parse, '1 2 ]3', d)
    
def test_parse_with_trailing_comments():
    check('1# comment', 1)
    check('1 # comment', 1)
    check('1# comment # comment2', 1)
    check('o1# comment', o1)
    check('o1()# comment', 1)
    check('-1# comment', -1)
    check('1-1# comment', 0)

def test_parse_with_only_comments():
    check('# comment')
    check(' # comment')
    check('  # comment')
    
    
    
