#
# General utility functions to handle Diffcalc commands
#

from gda.jython.commands.GeneralCommands import alias

def alias_commands(global_namespace_dict):
    """Alias commands left in global_namespace_dict by previous import from
    diffcalc.

    This is the equivalent of diffcmd/ipython/magic_commands() for use
    when IPython is not available
    """
    gnd = global_namespace_dict
    global GLOBAL_NAMESPACE_DICT
    GLOBAL_NAMESPACE_DICT = gnd
    print "Aliasing commands"
    
    ### Alias commands in namespace ###
    commands = gnd['hkl_commands_for_help']
    commands += gnd['ub_commands_for_help']
    commands.append(gnd['pos'])
    commands.append(gnd['scan'])       
    aliased_names = []

    for f in commands:
        # Skip section headers like 'Motion'
        if not hasattr(f, '__call__'):
            continue
        
        alias(f.__name__)
        aliased_names.append(f.__name__)

    print "Aliased commands: " + ' '.join(aliased_names) 
