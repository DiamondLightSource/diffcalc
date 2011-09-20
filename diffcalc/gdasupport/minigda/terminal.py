import sys
import os
from diffcalc.gdasupport.minigda.translator import Translator
from diffcalc.gdasupport.minigda.translator import TranslatorException
from diffcalc.gdasupport.minigda.translator import TranslatorAliasedCommandsOnly
from diffcalc.gdasupport.minigda.scannable.scannable import Scannable
import diffcalc.utils
print "WARNING: minigda.terminal is not well tested"


def stubAlias(method):
    raise Exception, "in diffcalc.gdasupport.minigda.Translator alias is not ready. First instantiate a Terminal."
alias = stubAlias

class Terminal(object):
    def __init__(self, mainNamepaceDict):
        self.mainNamepaceDict = mainNamepaceDict
        self.translator = Translator()
        self.recordFile = None
        global alias
        alias = self.translator.alias
        
    def alias(self, name):
        self.translator.alias(name)
        
    def start(self):
        print "Starting minigda terminal. Type exit or press ctrl-d to return to Python\n"
        while 1:
            try:
                cmd = raw_input('gda>>>')
            except EOFError:
                break
            if cmd in('quit','exit'):
                    print "42"
                    break
            if self.recordFile:
                self.recordFile.write(cmd+"\n")
            self.processInput(cmd)
    
    def startRecording(self, recordPath):
        self.recordFile = open(recordPath, 'w')
        diffcalc.utils.RECORDFILE = self.recordFile

    
    def evalInMain(self,cmd):
        return eval(cmd,self.mainNamepaceDict)
    
    def execInMain(self, cmd):
        try:
            exec cmd in self.mainNamepaceDict
#        except TranslatorException: #? needed ?
#            raise
        except:
            print self.generateErrorReport(sys.exc_info())
            print "## Translator sent: '%s' ##" % cmd
            return True
    
    def generateErrorReport(self,exc_info):
        try:
            # Works in jython from jython code
            result = exc_info[2].dumpStack() + str(exc_info[0]) + ': ' + str(exc_info[1])
        except:
            try:
                # Works in python
                import traceback
                ls = traceback.format_exception(exc_info[0],exc_info[1],exc_info[2])
                result = ""
                for st in ls:
                    result += st
            except:
                # works in Jython with java code:
                result = "Exception in Java code: %s" % exc_info[1].getMessage()
        return result

    def run(self, path=None):
        usage = "Usage 'run path', where path must be a quoted string"
        # Check input
        if type(path) is not str:
            print usage
            return
        # Open file
        try:
            f = open(path, 'r')
        except IOError:
                try:
                    path = os.getcwd() + os.path.sep + path
                    f = open(path, 'r')
                except IOError:
                    print "ERROR: No script with abosolute or relative path '%s' could be opened." % path
                    print "\n" + usage
                    return
        print "Running scipt '%s' ..."% path
        # Process file
        for n, line in enumerate(f):
            line = line.strip()
            print ">>>" + line
            res = self.processInput(line)
            if res is not None:
                print "\nERROR: processing line %d of file %s: '%s'" % (n,path, line)
                break
        f.close()
        
class TerminalAliasedCommandsOnly(Terminal):
    
    def __init__(self, mainNamepaceDict):
        self.mainNamepaceDict = mainNamepaceDict
        self.translator = TranslatorAliasedCommandsOnly()
        self.recordFile = None

    def processInput(self, cmd):
        # If this refers to a scannable, just print it.
        if self.mainNamepaceDict.has_key(cmd):
            obj = self.mainNamepaceDict[cmd]
            if isinstance(obj,Scannable):
                print str(obj)
                return
        
        try:
            cmd = self.translator.translate(cmd)
        except TranslatorException, e:
            print "Error: %s" % str(e)
            return True
##        print 'running translated command: ', cmd
        return self.execInMain(cmd)
            
