from diffcalc.ub.persistence import UbCalculationNonPersister
import os
import shutil
import unittest
try:
    from gda.configuration.properties import LocalProperties
except ImportError:
    print "Could not import LocalProperties to configure database locations."


def prepareEmptyGdaVarFolder():
    vartest_dir = os.path.join(os.getcwd(), 'var_test')
    LocalProperties.set('gda.var', vartest_dir)
    if os.path.exists(vartest_dir):
        print "Removing existing gda.var: ", vartest_dir
        shutil.rmtree(vartest_dir)
    print "Creating gda.var: ", vartest_dir
    os.mkdir(vartest_dir)

class TestUBCalculationNonPersister(unittest.TestCase):
    
    def setUp(self):
        self.p = UbCalculationNonPersister()
        
    def testSaveAndLoad(self):
        self.p.save('string1', 'ub1')
        self.assertEqual(self.p.load('ub1'), 'string1')

#class TestUBCalculationPersister(unittest.TestCase):
#    
#    def setUp(self):
#        prepareEmptyGdaVarFolder()
#        self.p = UBCalculationPersister()
#        
#    def testSaveAndLoad(self):
#        self.p.save('string1', 'ub1')
#        self.assertEqual(self.p.load('ub1'), 'string1')
