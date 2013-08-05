import re
from functools import wraps
from IPython.core.magic import register_line_magic


GLOBAL_NAMESPACE_DICT = {}

MATH_OPERATORS = set(['-', '+', '/', '*'])


COMMA_USAGE_HELP = \
'''
|   When calling a function without brackets, whitespace must be used in
|   place of commas. For example:
|   
|      >>> function a b [1 2 3] 'c'
|      
|   is equivalent to:
|   
|      >>> function(a, b, [1, 2, 3], 'c')
|      
'''


MATH_OPERATOR_USEAGE_HELP = \
'''
|    When calling a function without brackets, whitespace is used in place of
|    commas. Therefore terms which require evaluation must contain no space.
|    These will fail for example:
|
|      >>> function - 1
|      >>> function a() * 2

|    But this

|       >>> function -1 1-1 +1 a()+1 [-1 0+1 b()] c+1
|        
|    is okay and equivalent to:
|    
|       >>> function(-1, 0, 1, a() + 1, [-1, 1, b()], c + 1)
|       
      
'''

comma_finder = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')
space_finder = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
hash_finder = re.compile(r'''((?:[^#"']|"[^"]*"|'[^']*')+)''')
open_square_finder = re.compile(r'''((?:[^["']|"[^"]*"|'[^']*')+)''')
close_square_finder = re.compile(r'''((?:[^]"']|"[^"]*"|'[^']*')+)''')

def _tokenify(s):
    
    # Don't accept commas outside strings.
    # Users are frustrated by not knowing when commas _are_ required.
    # Making it clear when they are not helps them understand the
    # difference.

    if ',' in comma_finder.split(s):
        print COMMA_USAGE_HELP
        print "(string was: %s)" % s
        raise SyntaxError('unexpected comma')
    
    # ignore comment  
    hash_split = hash_finder.split(s)
    if '#' in hash_split:
        s = '' if hash_split[0] == '#' else hash_split[1]
    
    # surround square brackets with spaces to simplify token extraction
    s = ''.join(' [ ' if e == '[' else e for e in open_square_finder.split(s))
    s = ''.join(' ] ' if e == ']' else e for e in close_square_finder.split(s))
    
    
    # tokens are now separated by spaces
    
    tokens = space_finder.split(s)[1::2]
    tokens = [tok for tok in tokens if tok != '']
    return tokens


def parse(s, d):
    s = str(s)
    tokens = _tokenify(s)
    for tok in tokens:
        if tok in MATH_OPERATORS:
            print MATH_OPERATOR_USEAGE_HELP
            raise SyntaxError('could not evaluate: "%s"' % tok)
    
    
    s = ', '.join(tokens)

    s = s.replace('[, ', '[')
    s = s.replace(',]', ']')
    s = s.replace(', ]', ']')
    
    try:
        args = eval('[' + s + ']', d)
    except SyntaxError:
        raise SyntaxError('could not evaluate: "%s"' % s)
    return args


def parse_line(f):
    '''A decorator that parses a single string argument into a list of arguments
    and calls the wrapped function with these.
    '''
    @wraps(f)
    def wrapper(line):
        args = parse(line, GLOBAL_NAMESPACE_DICT)
        return f(*args)
    return wrapper
