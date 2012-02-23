import sys
import os
import time

from diffcalc.gdasupport.minigda.terminal import TerminalAliasedCommandsOnly
from diffcalc.gdasupport.minigda.commands.scan import Scan
from diffcalc.gdasupport.minigda.commands.pos import Pos
from diffcalc.gdasupport.minigda.commands.scan import ScanDataPrinter

#TODO: Replace with ipython


def usage():
    print """
python minigda.py [path_to_script.py] [path_to_stdin_record]

Starts minigda and if specified runs a script. path_to_script may be absolute
or relative to the directory from which minigda is run."""


def main():
    global STARTUPSCRIPT
    global term, alias, pos, scan, run

    ### Parse command line arguments ###
    if len(sys.argv) > 3:  # too many
        usage()
        sys.exit(2)
    elif len(sys.argv) == 1:  # 0 explicit args
        STARTUPSCRIPT = None
        RECORDPATH = None
    elif sys.argv[1] in ('-h', '--help'):
        usage()
        sys.exit()
    elif len(sys.argv) == 3:
        STARTUPSCRIPT = sys.argv[1]
        RECORDPATH = sys.argv[2]
    else:  # len(sys.argv) ==2:
        STARTUPSCRIPT = sys.argv[1]
        RECORDPATH = None

    ### Print generic startup info ###
    print "=" * 80
    print "Starting minigda on %s at %s ..." % (sys.platform, time.asctime())
    print "=" * 80
    print "sys.version:\n", sys.version
#    print "\nsys.path:\n" ,sys.path
    print "\nos.getcwd():\n", os.getcwd()
#    print "\nsys.argv: ",sys.argv
    print "=" * 80

    ### Configure Minigda ###
    term = TerminalAliasedCommandsOnly(globals())
    alias = term.alias
    scan = Scan(ScanDataPrinter())
    alias('scan')
    pos = Pos(globals())
    alias('pos')
    run = term.run
    alias('run')

    ### Run startup script ###
    if STARTUPSCRIPT is not None:
        if os.path.exists(STARTUPSCRIPT):
            STARTUPSCRIPT = STARTUPSCRIPT
        elif os.path.exists(STARTUPSCRIPT + ".py"):
            STARTUPSCRIPT = STARTUPSCRIPT + ".py"
        elif os.path.exists(os.getcwd() + os.path.sep + STARTUPSCRIPT):
            STARTUPSCRIPT = os.getcwd() + os.path.sep + STARTUPSCRIPT
        elif os.path.exists(os.getcwd() + os.path.sep + STARTUPSCRIPT):
            STARTUPSCRIPT = os.getcwd() + os.path.sep + STARTUPSCRIPT + '.py'
        else:
            print ("ERROR: No startup script with abosolute or relative path "
                   "'%s' found." % sys.argv[1])
            usage()
            sys.exit(2)
        print "Running startup scipt '%s' ...\n" % STARTUPSCRIPT
        execfile(STARTUPSCRIPT, globals())
    else:
        print "WARNING: No startup script specified."

    ### Start recording user input ###
    if RECORDPATH is not None:
        term.startRecording(os.getcwd() + os.path.sep + RECORDPATH)
    ### Start the terminal ###
    term.start()

if __name__ == '__main__':
    main()
