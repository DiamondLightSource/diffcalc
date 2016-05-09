


print "Ipython detected - magicing commands"
import diffcmd.ipython
diffcmd.ipython.GLOBAL_NAMESPACE_DICT = globals()
from IPython.core.magic import register_line_magic
from diffcmd.ipython import parse_line

commands = hkl_commands_for_help + ub_commands_for_help  # @UndefinedVariable
commands += [pos, scan]  # @UndefinedVariable


magiced_names = []
command_map = {}
for f in commands:
    # Skip section headers like 'Motion'
    if not hasattr(f, '__call__'):
        continue
    
    # magic the function and remove from namespace (otherwise it would
    # shadow the magiced command)
    register_line_magic(parse_line(f))
    del globals()[f.__name__]
    command_map[f.__name__] = f
    magiced_names.append(f.__name__)

print "Magiced commands: " + ' '.join(magiced_names) 

# because the functions have gone from namespace we need to override
pythons_help = __builtins__.help
del __builtins__.help

_DEFAULT_HELP = """
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
def help(s):
    """Diffcalc help for iPython
    """
    if s == '':
        print _DEFAULT_HELP
    elif s == 'hkl':
        # Use help injected into hkl object
        print hkl.__doc__
    elif s == 'ub':
        # Use help injected into ub command
        print command_map['ub'].__doc__
    elif s in command_map:
        print "%s (diffcalc command):" %s
        print command_map[s].__doc__
    else:
        exec('pythons_help(%s)' %s)
register_line_magic(help)
del help

