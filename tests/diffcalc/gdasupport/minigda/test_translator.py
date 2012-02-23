import unittest

from diffcalc.gdasupport.minigda.translator import TranslatorException, \
    TranslatorAliasedCommandsOnly


class TestTranslator(unittest.TestCase):
    def setUp(self):
        self.tran = TranslatorAliasedCommandsOnly()
        self.tran.alias('pos')
        self.tran.alias('scan')

    def testCommented(self):
        tran = self.tran.translate
        probe = '# a comment with cmda # \t cmd2 in it'
        self.assertEqual(tran(probe), probe)

    def testWithNoLeadingAliasesedCommand(self):
        tran = self.tran.translate
        self.assertRaises(TranslatorException, tran, "r=func(1,2,3)")
        self.assertRaises(TranslatorException, tran, "posy y 1")
#        self.assertRaises(TranslatorException, tran, "\tscan y 1 2 3")
#        self.assertRaises(TranslatorException, tran, " scan y 1 2 3")

    def testWithAlias(self):
        tran = self.tran.translate
        self.assertEqual(tran("scan a 1 2 3"), "scan(a,1,2,3)")
        self.assertEqual(tran("scan a 1 2 3 # 123"), "scan(a,1,2,3)# 123")
        self.assertEqual(tran("pos"), "pos()")

    def testWithAliasAndNegativeArgs(self):
        tran = self.tran.translate
        print ">>>>"
        self.assertEqual(tran("scan a -1 2 -3"), "scan(a,-1,2,-3)")
        self.assertEqual(tran("scan a 1 -2 3 # -123"), "scan(a,1,-2,3)# -123")
        print "<<<<"

    def testWithAliasAndVectorArguements(self):
        tran = self.tran.translate
        self.assertEqual(tran("scan a 1 2 3 b [2.1 , 2.2] c"),
                         "scan(a,1,2,3,b,[2.1,2.2],c)")

    def testWithNonAliasedCallOfAliasedFunction(self):
        tran = self.tran.translate
        self.assertRaises(TranslatorException, tran, "pos(a)")

    def testWithMath(self):
        tran = self.tran.translate
        self.assertEqual(tran("pos en 12.39842/1.24"), "pos(en,12.39842/1.24)")
        