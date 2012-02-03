import types
from diffcalc.utils import DiffcalcException

RAISE_EXCEPTIONS_FOR_ALL_ERRORS = False
DEBUG = False

class HelpList:
    class Usage:
        def __init__(self, command, argstr, helpstr):
            self.command = command
            self.argstr = argstr
            self.helpstr = helpstr
    
    def __init__(self):
        self.usageList = []
        self.usageByCommand = {}
    
    def append(self, docLine):
        command, argstr, helpstr = splitDocLine(docLine)
        self.usageList.append(self.Usage(command, argstr, helpstr))
        if not self.usageByCommand.has_key(command):
            self.usageByCommand[command] = [len(self.usageList) - 1]
        else:
            self.usageByCommand[command].append(len(self.usageList) - 1)
        
    def _getUsageStringByIndex(self, index):
        usage = self.usageList[index]
        if usage.helpstr == '':
            return "\n" + usage.command.rjust(14) + "\n" + ("-"*len(usage.command)).rjust(14) + "\n"
        else:
            result = usage.command.rjust(14) + "  " + usage.argstr
            result = result.ljust(35) + "- "
            result += usage.helpstr + "\n"
            return result

    def getCommandUsageString(self, name):
        result = ""
        try:
            for index in self.usageByCommand[name]:
                result += self._getUsageStringByIndex(index) + '\n'
        except KeyError:
            raise IndexError("No help for command %s" % name)
        return result
    
    def getCommandUsageForDoc(self, name):
        result = ""
        try:
            for index in self.usageByCommand[name]:
                usage = self.usageList[index]
                if usage.argstr == '':
                    return None
                result += usage.command + " " + usage.argstr + " --- " + usage.helpstr + "\n"
            return result.strip()      
        except KeyError:
            return None
        
    def getCompleteCommandUsageList(self):
        result = ""
        for index in range(len(self.usageList)):
            result += self._getUsageStringByIndex(index)
        return result
    
def splitDocLine(docLine):
    name, _, right = docLine.partition(' ')
    args, _, description = right.partition('-- ')
    return name, args, description


class UsageHandler(object):
    """Annotation"""

    def __init__(self, command):
        self.command = command
        docLines = [s.strip() for s in self.command.__doc__.split('\n')]
        for line in docLines:
            if line:
                self.appendDocLine(line)

    def __call__(self, *args):
        if DEBUG:
            return self.command(*args)
        try:
            return self.command(*args)
        except TypeError, e:
            # NOTE: TypeErrors resulting from bugs in the core code will be erroneously caught here!
            if RAISE_EXCEPTIONS_FOR_ALL_ERRORS:
                print "-" * 80
                print self.command.__doc__
                print "-" * 80        
                raise e
            else:
                print 'TypeError : %s' % e.message
                print 'USAGE:'
                print self.command.__doc__
        except DiffcalcException, e:
            if RAISE_EXCEPTIONS_FOR_ALL_ERRORS:
                raise e
            else:
                print e.args[0]
            
    def __get__(self, obj, ownerClass=None):
        # ref: http://www.outofwhatbox.com/blog/2010/07/python-decorating-with-class/
        # Return a wrapper that binds self as a method of obj (!)
        return types.MethodType(self, obj)
