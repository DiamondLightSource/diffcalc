# NOTE: This file must be run, not imported, for the ipython magic to work!

import diffcmd.ipythonmagic

try:
    __IPYTHON__  # @UndefinedVariable
    IPYTHON = True
except NameError:
    IPYTHON = False
    
try:
    from gda.device.scannable.scannablegroup import ScannableGroup
    GDA = True
except ImportError:
    GDA = False
    
### If iPython then convert all commands to magic
if IPYTHON:
    print "Running in iPython --- magicing commands (iPython will remove"
    print "                       commands from top level namespace)"
    from diffcmd.ipython import magic_commands
    magic_commands(globals())
elif GDA:
    print "Running in GDA --- aliasing commands"
    from diffcmd.diffcmd_utils import alias_commands
    alias_commands(globals())
else:
    print "Running outside iPython or GDA --- running commands requires brackets and commas"