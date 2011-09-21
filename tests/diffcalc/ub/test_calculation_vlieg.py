from datetime import datetime
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.ub.calculation import UBCalculation, matrixTo3x3ListOfLists
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.utils import DiffcalcException
from tests.diffcalc import scenarios
import unittest
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

class MockMonitor(object):
    def getPhysicalAngleNames(self):
        return ('a', 'd', 'g', 'o', 'c', 'p')

class TestUBCalculationWithSixCircleGammaOnArm(unittest.TestCase):
    
    def setUp(self):    
        self.geometry = SixCircleGammaOnArmGeometry()
        self.hardware = MockMonitor()
        self.ubcalc = UBCalculation(self.hardware, self.geometry, UbCalculationNonPersister())
        self.time = datetime.now()

### State ###
    
    def testNewCalculation(self):
        # this was called in setUp
        self.ubcalc.newCalculation('testcalc')
        self.assertEqual(self.ubcalc.getName(), 'testcalc', "Name not set by newCalcualtion")
        self.assertRaises(DiffcalcException, self.ubcalc.getUMatrix) # check umatrix cleared
        self.assertRaises(DiffcalcException, self.ubcalc.getUBMatrix) # check ubmatrix cleared

### Lattice ###

    def testSetLattice(self):
        # Not much to test, just make sure no exceptions
        self.ubcalc.newCalculation('testcalc')
        self.ubcalc.setLattice('testlattice', 4.0004, 4.0004, 2.270000, 90, 90, 90)
    
### Calculations ###

    def testSetUManually(self):
        
        # Test the calculations with U=I
        U = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        for sess in scenarios.sessions():
            self.setUp()
            self.ubcalc.newCalculation('testcalc')
            self.ubcalc.setLattice(sess.name, *sess.lattice)
            self.ubcalc.setUManually(U)        
            # Check the U matrix
            self.assert_(self.ubcalc.getUMatrix().minus(Matrix(U)).norm1() <= .0001, "wrong U after manually setting U")
            
            # Check the UB matrix
            if sess.bmatrix == None:
                continue
            print "U: ", U
            print "actual ub: ", self.ubcalc.getUBMatrix().getArray()
            print " desired b: ", sess.bmatrix
            self.assert_(self.ubcalc.getUBMatrix().minus(Matrix(sess.bmatrix)).norm1() <= .0001, "wrong UB matrix after manually setting U")

    def testGetUMatrix(self):
        self.ubcalc.newCalculation('testcalc')
        # tested in testSetUManually
        self.assertRaises(DiffcalcException, self.ubcalc.getUMatrix) # no u calculated yet
    
    def testGetUBMatrix(self):
        self.ubcalc.newCalculation('testcalc')
        # tested in testSetUManually
        self.assertRaises(DiffcalcException, self.ubcalc.getUBMatrix) # no ub calculated yet
            
    
    def testCalculateU(self):
        
        for sess in scenarios.sessions():
            self.setUp()
            self.ubcalc.newCalculation('testcalc')
            # Skip this test case unless it contains a umatrix
            if sess.umatrix == None:
                continue
        
            self.ubcalc.setLattice(sess.name, *sess.lattice)
            self.ubcalc.addReflection(sess.ref1.h, sess.ref1.k, sess.ref1.l, sess.ref1.pos, sess.ref1.energy, sess.ref1.tag, sess.time)
            self.ubcalc.addReflection(sess.ref2.h, sess.ref2.k, sess.ref2.l, sess.ref2.pos, sess.ref2.energy, sess.ref2.tag, sess.time)
            self.ubcalc.calculateUB()
            returned = self.ubcalc.getUMatrix().getArray()
            print "*Required:"
            print sess.umatrix
            print "*Returned:"
            print returned
            self.assert_(self.ubcalc.getUMatrix().minus(Matrix(sess.umatrix)).norm1() < .0001, "wrong U calulated for sess.name=" + sess.name)

    def test__str__(self):
        sess = scenarios.sessions()[0]
        print "***"
        print self.ubcalc.__str__()
        
        print "***"
        self.ubcalc.newCalculation('test')
        print self.ubcalc.__str__()
        
        print "***"        
        self.ubcalc.setLattice(sess.name, *sess.lattice)
        print self.ubcalc.__str__()
        
        print "***"    
        self.ubcalc.addReflection(sess.ref1.h, sess.ref1.k, sess.ref1.l, sess.ref1.pos, sess.ref1.energy, sess.ref1.tag, sess.time)
        self.ubcalc.addReflection(sess.ref2.h, sess.ref2.k, sess.ref2.l, sess.ref2.pos, sess.ref2.energy, sess.ref2.tag, sess.time)
        print self.ubcalc.__str__()
        
        print "***"    
        self.ubcalc.calculateUB()
        print self.ubcalc.__str__()

    def getSess1State(self):
        sess = scenarios.sessions()[0]
        return {
                'tau': 0,
                'ub': None,
                'sigma': 0,
                'crystal': {'gamma': 90.0, 'alpha': 90.0, 'c': 5.43072, 'beta': 90.0, 'b': 3.8401, 'a': 3.8401, 'name': 'b16_270608'},
                'u': None,
                'reflist': {
                        'ref_1': {'position': (5.0, 22.79, 0.0, 4.575, 24.275, 101.32), 'tag': 'ref2', 'l': 1.0628, 'energy': 10.0, 'k': 1.0, 'h': 0.0, 'time': `sess.time`},
                        'ref_0': {'position': (5.0, 22.79, 0.0, 1.552, 22.4, 14.255), 'tag': 'ref1', 'l': 1.0628, 'energy': 10.0, 'k': 0.0, 'h': 1.0, 'time': `sess.time`}
                },
                'name': 'test'
        }

    def testGetState(self):
        sess = scenarios.sessions()[0]
        self.ubcalc.newCalculation('test')
        self.ubcalc.setLattice(sess.name, *sess.lattice)
        self.ubcalc.addReflection(sess.ref1.h, sess.ref1.k, sess.ref1.l, sess.ref1.pos, sess.ref1.energy, sess.ref1.tag, sess.time)
        self.ubcalc.addReflection(sess.ref2.h, sess.ref2.k, sess.ref2.l, sess.ref2.pos, sess.ref2.energy, sess.ref2.tag, sess.time)
        expectedState = self.getSess1State()
        self.assertEquals(expectedState, self.ubcalc.getState())

    def testRestoreState(self):
        state = self.getSess1State()
        self.ubcalc.newCalculation('unwanted one')
        self.ubcalc.restoreState(state)
        state = self.getSess1State()
        self.assertEquals(state, self.ubcalc.getState())

    def testGetStateWithManualU(self):
        sess = scenarios.sessions()[0]
        self.ubcalc.newCalculation('test')
        self.ubcalc.setLattice(sess.name, *sess.lattice)
        self.ubcalc.addReflection(sess.ref1.h, sess.ref1.k, sess.ref1.l, sess.ref1.pos, sess.ref1.energy, sess.ref1.tag, sess.time)
        self.ubcalc.addReflection(sess.ref2.h, sess.ref2.k, sess.ref2.l, sess.ref2.pos, sess.ref2.energy, sess.ref2.tag, sess.time)
        self.ubcalc.setUManually([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        state = self.ubcalc.getState()
        self.assertEqual(matrixTo3x3ListOfLists(self.ubcalc.getUMatrix()), state['u'])
        expectedState = self.getSess1State()
        expectedState['u'] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.assertEquals(expectedState, state)
        
    def testRestoreStateWithManualU(self):
        setState = self.getSess1State()
        setState['u'] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.ubcalc.newCalculation('unwanted one')
        self.ubcalc.restoreState(setState)
        
        self.assertEquals([[1, 2, 3], [4, 5, 6], [7, 8, 9]], matrixTo3x3ListOfLists(self.ubcalc.getUMatrix()))

        
    def testGetStateWithManualUB(self):
        sess = scenarios.sessions()[0]
        self.ubcalc.newCalculation('test')
        self.ubcalc.setLattice(sess.name, *sess.lattice)
        self.ubcalc.addReflection(sess.ref1.h, sess.ref1.k, sess.ref1.l, sess.ref1.pos, sess.ref1.energy, sess.ref1.tag, sess.time)
        self.ubcalc.addReflection(sess.ref2.h, sess.ref2.k, sess.ref2.l, sess.ref2.pos, sess.ref2.energy, sess.ref2.tag, sess.time)
        self.ubcalc.setUBManually([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        state = self.ubcalc.getState()
        self.assertEqual(matrixTo3x3ListOfLists(self.ubcalc.getUBMatrix()), state['ub'])
        expectedState = self.getSess1State()
        expectedState['ub'] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.assertEquals(expectedState, state)
        
    def testRestoreStateWithManualUB(self):
        setState = self.getSess1State()
        setState['ub'] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.ubcalc.newCalculation('unwanted one')
        self.ubcalc.restoreState(setState)
        self.assertEquals([[1, 2, 3], [4, 5, 6], [7, 8, 9]], matrixTo3x3ListOfLists(self.ubcalc.getUBMatrix()))
