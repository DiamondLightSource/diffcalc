import re
from functools import wraps
from IPython.core.magic import register_line_magic
from IPython import get_ipython  # @UnusedImport (used by register_line_magic)
from diffcalc.gdasupport.scannable.hkl import Hkl

"""
For wrapping functions:

    In [1]: import diffcmd.ipython
    
    In [2]: diffcmd.ipython.GLOBAL_NAMESPACE_DICT = globals()
    
    In [3]: from IPython.core.magic import register_line_magic
    
    In [4]: from diffcmd.ipython import parse_line
    
    In [5]: @register_line_magic
       ...: @parse_line
       ...: def check_parser(*args):
       ...:         return args
       ...: 
    
    In [6]: check_parser
    Out[6]: <function __main__.check_parser>
    
    In [7]: del check_parser
    
    In [8]: check_parser
    Out[8]: ()
    
    In [9]: check_parser 1
    Out[9]: (1,)
    
    In [10]: check_parser 1 2
    Out[10]: (1, 2)
    
    In [11]: check_parser 1 2 [3]
    Out[11]: (1, 2, [3])
    
    In [12]: b='bbb'
    
    In [13]: check_parser 1 2 [3] b
    Out[13]: (1, 2, [3], 'bbb')


And to create something dynamically from a function:

    In [28]: def f(a, b, c):
       ....:        ....:     return a, b, c
       ....: 
    
    In [29]: register_line_magic(parse_line(f))
    Out[29]: <function __main__.f>
    
    In [30]: del f
    
    In [31]: f 'a' -2 [1 3 -4]
    Out[31]: ('a', -2, [1, 3, -4])

And from a list of functions:

    In [32]: def one(a):
       ....:     return a
       ....: 
    
    In [33]: def two(a, b):
       ....:     return a, b
       ....: 
    
    In [34]: functions = one, two
    
    In [35]: del one, two
    
    In [36]: for f in functions:
       ....:     register_line_magic(parse_line(f))
       ....:     
    
    In [37]: one 1
    Out[37]: 1

    In [39]: two 1 2
    Out[39]: (1, 2)

And to check if we are running in iPython:

    In [47]: 'get_ipython' in globals()
    Out[47]: True

def in_ipython():
     try:
         get_ipython()
         return True
     except NameError:
         return False


"""


GLOBAL_NAMESPACE_DICT = {}

MATH_OPERATORS = set(['-', '+', '/', '*'])

# Keep a copy of python's original help as we may remove it later
if 'help' in __builtins__:   
    ORIGINAL_PYTHON_HELP = __builtins__['help']


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


MATH_OPERATOR_USAGE_HELP = \
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

def tokenify(s):
    
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
    tokens = tokenify(s)
    for tok in tokens:
        if tok in MATH_OPERATORS:
            print MATH_OPERATOR_USAGE_HELP
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

def parse_line(f, global_namespace_dict=None):
    '''A decorator that parses a single string argument into a list of arguments
    and calls the wrapped function with these.
    '''
    if not global_namespace_dict:
        global_namespace_dict = GLOBAL_NAMESPACE_DICT
    @wraps(f)
    def wrapper(line):
        args = parse(line, global_namespace_dict)
        return f(*args)
    return wrapper



_DEFAULT_HELP = \
"""
For help with diffcalc's orientation phase try:
    
    >>> help ub
    
For help with moving in reciprocal lattice space try:

    >>> help hkl
    
For more detailed help try for example:

    >>> help newub
    
For help with driving axes or scanning:

    >>> help pos
    >>> help scan
    
For help with regular python try for example:

    >>> help list
    
For more detailed help with diffcalc go to:

    https://diffcalc.readthedocs.io
    
"""

def magic_commands(global_namespace_dict):
    """Magic commands left in global_namespace_dict by previous import from
    diffcalc.
    
    Also creates a help command. NOTE that calling this will
    remove the original commands from the global namespace as otherwise these
    would shadow the ipython magiced versions.
    
    Depends on hkl_commands_for_help & ub_commands_for_help list having been
    left in the global namespace and assumes there is pos and scan command.
    """
    gnd = global_namespace_dict
    global GLOBAL_NAMESPACE_DICT
    GLOBAL_NAMESPACE_DICT = gnd
    
    ### Magic commands in namespace ###
    commands = list(gnd['hkl_commands_for_help'])
    commands += gnd['ub_commands_for_help']
    commands.append(gnd['pos'])
    commands.append(gnd['scan'])       
    command_map = {}
    for f in commands:
        # Skip section headers like 'Motion'
        if not hasattr(f, '__call__'):
            continue
        # magic the function and remove from namespace (otherwise it would
        # shadow the magiced command)
        register_line_magic(parse_line(f, gnd.copy()))
        del gnd[f.__name__]
        command_map[f.__name__] = f

    ### Create help function ###
    #Expects python's original help to be named pythons_help and to be
    #available in the top-level global namespace (where non-diffcalc
    #objects may have help called from).        
    def help(s):  # @ReservedAssignment   
        """Diffcalc help for iPython
        """
        if s == '':
            print _DEFAULT_HELP
        elif s == 'hkl':
            # Use help injected into hkl object
            print Hkl.dynamic_docstring
        elif s == 'ub':
            # Use help injected into ub command
            print command_map['ub'].__doc__
        elif s in command_map:
            print "%s (diffcalc command):" %s
            print command_map[s].__doc__
        else:
            exec('pythons_help(%s)' %s, gnd)

      
    ### Setup help command ###
    gnd['pythons_help'] = ORIGINAL_PYTHON_HELP  
    register_line_magic(help)
    # Remove builtin help
    # (otherwise it would shadow magiced command
    if 'help' in __builtins__:   
        del __builtins__['help']
