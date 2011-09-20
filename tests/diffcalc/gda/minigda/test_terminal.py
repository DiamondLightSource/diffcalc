from diffcalc.gdasupport.minigda.terminal import Terminal,\
    TerminalAliasedCommandsOnly
import unittest

aGlobalString = 'a'

def aGlobalFunction(s):
    return s

class TestTerminal(unittest.TestCase):
    
    def setUp(self):
        self.generateMockMainNameSpaceDict()
        self.term = TerminalAliasedCommandsOnly(self.mockMainNameSpaceDict)
    
    def generateMockMainNameSpaceDict(self):
        self.mockMainNameSpaceDict ={}
        self.mockMainNameSpaceDict #for conveniance
        
        # General testing principle:
        def bFunction(s):
            return s
        self.mockMainNameSpaceDict['bFunction'] = bFunction
        self.mockMainNameSpaceDict['bString'] = 'b'
        
        def appendFunction(a ,b):
            # make sure a is mutable
            a.append(b)
        self.mockMainNameSpaceDict['appendFunction'] = appendFunction
        self.mockMainNameSpaceDict['aa'] = [1]
    
    def testEvalInMainGlobalMechanism(self):
        term = TerminalAliasedCommandsOnly(globals())
        self.assertEqual(term.evalInMain("aGlobalFunction(aGlobalString)"), 'a' )
    
    def testEvalInMainTestingPrinciple(self):
        self.assertEqual(self.term.evalInMain('bFunction(bString)') , 'b')    

    def testExecInMainTestingPrinciple(self):
        self.term.execInMain("two = 1 + 1")
        self.assertEqual(self.term.evalInMain('two'), 2)
        
#    def testTranslateAndExecInMainNonAliased(self):
#        self.term.translateAndExecInMain("appendFunction(aa, [2.1,'r'])")
#        self.assertEqual( self.term.evalInMain("aa"), [1,[2.1,'r']])
#        
#    def testTranslateAndExecInMainAliased(self):
#        self.term.alias('appendFunction')
#        self.term.translateAndExecInMain("appendFunction aa [2.1,'r']")
#        self.assertEqual( self.term.evalInMain("aa"), [1,[2.1,'r']])    

class TestTerminalAliasedCommandsOnly(TestTerminal):
    def setUp(self):
        self.generateMockMainNameSpaceDict()
        self.term = TerminalAliasedCommandsOnly(self.mockMainNameSpaceDict)
        
    def testProcessInputWithAliasedCommands(self):
        def pos(d='default should be printed'):
            print d
        def scan(*args):
            for arg in args:
                print arg
        self.mockMainNameSpaceDict['pos'] = pos
        self.mockMainNameSpaceDict['scan']= scan
        self.term.alias('pos')
        self.term.alias('scan')
        # Not very good tests:
        self.term.processInput("pos")        
        self.term.processInput("pos 'should be printed'")
        self.term.processInput("scan 'should' 'be' 'printed'")
    
    def testExceptionCapture(self):
        def good():
            print "okay"
        def bad():
            print 1/0
        self.mockMainNameSpaceDict['good'] = good
        self.mockMainNameSpaceDict['bad']= bad
        self.term.alias('good')
        self.term.alias('bad')
        self.term.processInput("good")
        self.term.processInput("bad")
        #TODO: Check with java code too (if Jama can be imported)
    
    def testProcessInputWithInvalidCommands(self):
        self.term.processInput("not a command")
