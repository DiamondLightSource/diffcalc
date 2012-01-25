from datetime import datetime
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.hkl.vlieg.position import VliegPosition
from diffcalc.tools import matrixeq_
from diffcalc.ub.calculation import UBCalculation, matrixTo3x3ListOfLists
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.utils import DiffcalcException
from math import cos, sin, pi
from mock import Mock
from tests.diffcalc import scenarios
import unittest
from diffcalc.hkl.vlieg.ubcalcstrategy import VliegUbCalcStrategy
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

I = Matrix(((1, 0, 0), (0, 1, 0), (0, 0, 1)))
TORAD = pi / 180

class MockMonitor(object):
    def getPhysicalAngleNames(self):
        return ('a', 'd', 'g', 'o', 'c', 'p')

class TestUBCalculationWithSixCircleGammaOnArm(unittest.TestCase):
    
    def setUp(self):    
        self.geometry = SixCircleGammaOnArmGeometry()
        self.hardware = MockMonitor()
        self.ubcalc = UBCalculation(self.hardware, self.geometry, UbCalculationNonPersister(), VliegUbCalcStrategy())
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

     

#TODO: hkl calculation oddity: (CUBIC, 1, 0, 0, CUBIC_EN) --> ({alpha: 0.0 delta: 60.00000000000001 gamma: 0.0 omega: -59.99999999999999 chi: 7.016709298534875e-15  phi: 90.0}, {'Bin': -6.07664850350169e-15, 'Bout': 6.07664850350169e-15, '2theta': 60.00000000000001, 'azimuth': 7.0167092985348775e-15})
#    def calculateIdealBisectingPosition(self, lattice_args, h, k, l, energy):
#        ubcalc = UBCalculation(self.hardware, self.geometry, UbCalculationNonPersister())
#        ubcalc.newCalculation('xtalubcalc')
#        ubcalc.setLattice("xtal", *lattice_args)
#        ubcalc.setUManually(I)
#        ac = VliegHklCalculator(ubcalc, self.geometry, self.hardware, True)
#        ac.mode_selector.setModeByIndex(1)
#        return ac.hklToAngles(h, k, l, energy)
#    
#    def testCalculateIdealBisectingPosition(self):
#        # this is part of the harness
#        print "test"
#        print self.calculateIdealBisectingPosition(CUBIC, 1, 0, 0, CUBIC_EN)

def x_rotation(mu_or_alpha):
    mu_or_alpha *= TORAD
    return Matrix(((1, 0, 0), (0, cos(mu_or_alpha), -sin(mu_or_alpha)), (0, sin(mu_or_alpha), cos(mu_or_alpha))))

def y_rotation(chi):
    chi *= TORAD
    return Matrix(((cos(chi), 0, sin(chi)), (0, 1, 0), (-sin(chi), 0, cos(chi))))

def z_rotation(th):
    eta = -th * TORAD
    return Matrix(((cos(eta), sin(eta), 0), (-sin(eta), cos(eta), 0), (0, 0, 1)))

CUBIC_EN = 12.39842
CUBIC = (1, 1, 1, 90, 90, 90)
ROT = 29

class TestUBCalcWithCubic():
    
    def setUp(self):    
        hardware = Mock()
        hardware.getPhysicalAngleNames.return_value = ('a', 'd', 'g', 'o', 'c', 'p')
        self.ubcalc = UBCalculation(hardware, SixCircleGammaOnArmGeometry(), UbCalculationNonPersister(), VliegUbCalcStrategy())
        self.ubcalc.newCalculation('xtalubcalc')
        self.ubcalc.setLattice("xtal", *CUBIC)
        self.energy = CUBIC_EN
        
    def addref(self, hklref):
        hkl, position = hklref
        self.ubcalc.addReflection(hkl[0], hkl[1], hkl[2], position, self.energy, "ref", datetime.now())


class TestUBCalcWithCubicTwoRef(TestUBCalcWithCubic):

    def check(self, testname, hklref1, hklref2, expectedUMatrix):
        self.addref(hklref1)
        self.addref(hklref2)
        matrixeq_(expectedUMatrix, self.ubcalc.getUMatrix())

    def test_with_squarely_mounted(self):
        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0))
        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=90, phi=0))
        pairs = (("hl", href, lref, I),
                 ("lh", lref, href, I))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u

    def test_with_x_mismount(self):
        U = x_rotation(ROT)
        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0))
        kref = ((0, 1, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30-ROT+90, chi=90, phi=0))
        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30-ROT, chi=90, phi=0))
        pairs = (("hk", href, kref, U),
                 ("hl", href, lref, U),
                 ("kh", kref, href, U),
                 ("kl", kref, lref, U),
                 ("lk", lref, kref, U),
                 ("lh", lref, href, U))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u
            
    def test_with_y_mismount(self):
        U = y_rotation(ROT)
        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0-ROT, phi=0))
        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=90-ROT, phi=0))
        pairs = (("hl", href, lref, U),
                 ("lh", lref, href, U))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u
            
    def test_with_z_mismount(self):
        U = z_rotation(ROT)
        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0+ROT))
        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=90, phi=67)) # phi degenerate
        pairs = (("hl", href, lref, U),
                 ("lh", lref, href, U))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u
            
    def test_with_zy_mismount(self):
        U = z_rotation(ROT).times(y_rotation(ROT))
        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0-ROT, phi=0+ROT))
        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=90-ROT, phi=ROT)) # chi degenerate
        pairs = (("hl", href, lref, U),
                 ("lh", lref, href, U))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u
            
            
            
            
class TestUBCalcWithcubicOneRef(TestUBCalcWithCubic):
    
    def check(self, testname, hklref, expectedUMatrix):
        print testname
        self.addref(hklref)
        self.ubcalc.calculateUBFromPrimaryOnly()
        matrixeq_(expectedUMatrix, self.ubcalc.getUMatrix())

    def test_with_squarely_mounted(self):
        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0))
        href_b = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30+90, chi=90, phi=-90))
        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=90, phi=67)) # degenerate in phi
        pairs = (("h", href, I),
                 ("hb", href_b, I),
                 ("l", lref, I))
        for testname, ref, u in pairs:
            yield self.check, testname, ref, u
            
    def test_with_x_mismount(self):
        U = x_rotation(ROT)
        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0))
        kref = ((0, 1, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30-ROT+90, chi=90, phi=0))
        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30-ROT, chi=90, phi=0))
        pairs = (("h", href, I), # TODO: can't pass, no information - word instructions
                 ("k", kref, U),
                 ("l", lref, U))
        for testname, ref, u in pairs:
            yield self.check, testname, ref, u
            
    def test_with_y_mismount(self):
        U = y_rotation(ROT)
        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0-ROT, phi=0))
        kref = ((0, 1, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30+90, chi=90, phi=0))
        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=90-ROT, phi=0))
        pairs = (("h", href, U),
                 ("k", kref, I),# TODO: can't pass, no information - word instructions
                 ("l", lref, U))
        for testname, ref, u in pairs:
            yield self.check, testname, ref, u
            
    def test_with_z_mismount(self):
        U = z_rotation(ROT)

        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0+ROT))
        kref = ((0, 1, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30+90, chi=0, phi=0+ROT))
        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=90, phi=67)) # phi degenerate
        pairs = (("h", href, U),
                 ("k", kref, U),
                 ("l", lref, I)) # TODO: can't pass, no information - word instructions
        for testname, ref, u in pairs:
            yield self.check, testname, ref, u
            
# Probably lost cause, conclusion is be careful and return the angle and direction of resulting u matrix
#    def test_with_zy_mismount(self):
#        U = z_rotation(ROT).times(y_rotation(ROT))
#        href = ((1, 0, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=0-ROT, phi=0+ROT))
#        kref = ((0, 1, 0), VliegPosition(alpha=0, delta=60, gamma=0, omega=30+90, chi=90-ROT, phi=0+ROT))
#        lref = ((0, 0, 1), VliegPosition(alpha=0, delta=60, gamma=0, omega=30, chi=90-ROT, phi=ROT)) # chi degenerate
#        pairs = (("h", href, U),
#                 ("k", kref, U),
#                 ("l", lref, U))
#        for testname, ref, u in pairs:
#            yield self.check, testname, ref, u
            
            
            