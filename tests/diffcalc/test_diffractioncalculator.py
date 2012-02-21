from diffcalc.diffractioncalculator import Diffcalc, create_diffcalc_vlieg
from diffcalc.gdasupport.scannable.base import ScannableGroup
from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc.gdasupport.scannable.parameter import \
    DiffractionCalculatorParameter
from diffcalc.gdasupport.scannable.slave_driver import NuDriverForSixCirclePlugin
from diffcalc.geometry.fivec import fivec
from diffcalc.geometry.fourc import fourc
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry, \
    SixCircleGeometry
from diffcalc.hardware.dummy import DummyHardwareMonitorPlugin
from diffcalc.hardware.scannable import ScannableHardwareMonitorPlugin
from diffcalc.tools import assert_array_almost_equal
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.utils import DiffcalcException, MockRawInput, norm1
from tests.diffcalc import scenarios
import diffcalc.utils # @UnusedImport to overide raw_input
import unittest

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix
try:
    from gdascripts.pd.dummy_pds import DummyPD #@UnusedImport
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.dummy import DummyPD


def prepareRawInput(listOfStrings):
    diffcalc.utils.raw_input = MockRawInput(listOfStrings)

prepareRawInput([])

def createDummyAxes(names):
    result = []
    for name in names:
        result.append(DummyPD(name))
    return result

                          
class BaseTestDiffractionCalculatorWithData():
    
    def setSessionAndCalculation(self):
        raise Exception("Abstract")

    def setUp(self):
        self.geometry = SixCircleGammaOnArmGeometry()
        self.hardware = DummyHardwareMonitorPlugin(('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'))
        self.d = create_diffcalc_vlieg(self.geometry, self.hardware, True, UbCalculationNonPersister())

        self.d.raiseExceptionsForAllErrors = True
        #self.scenarios = scenarios.sessions()
        self.setSessionAndCalculation()
        prepareRawInput([])
    
    def setDataAndReturnObject(self, sessionScenario, calculationScenario):
        self.sess = sessionScenario
        self.calc = calculationScenario
        return self
    
    def test_anglesToHkl(self):
        
        self.assertRaises(DiffcalcException, self.d._anglesToHkl , (1, 2, 3, 4, 5, 6)) # because no energy has been set yet
        self.d._hardware.setEnergy(10)
        self.assertRaises(DiffcalcException, self.d._anglesToHkl , (1, 2, 3, 4, 5, 6)) # because no ub matrix has been calculated yet
        s = self.sess
        c = self.calc
        
        # setup session info
        self.d.ubcommands.newub(s.name)
        self.d.ubcommands.setlat(s.name, *s.lattice)
        r = s.ref1; self.d.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r = s.ref2; self.d.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.d.ubcommands.calcub()
        
        # check the ubcalculation is okay before continuing (useful to check for typos!)        
        self.assert_(norm1(self.d._ubcalc.getUBMatrix() - (matrix(s.umatrix) * (matrix(s.bmatrix)))) <= .0001, \
                                                         "wrong UB matrix after calculating U")
        # Test each hkl/position pair
        for idx in range(len(c.hklList)):
            hkl = c.hklList[idx]
            pos = c.posList[idx]
            # 1) specifying energy explicitely
            ((h, k, l), params) = self.d._anglesToHkl(pos.totuple(), c.energy)
            self.assert_((abs(h - hkl[0]) < .001) & (abs(k - hkl[1]) < .001) & (abs(l - hkl[2]) < .001), "wrong hkl calcualted for TestScenario=%s, AngleTestScenario=%s, pos=%s):\n  expected hkl=%f %f %f\n  returned hkl=%f %f %f "\
                        % (s.name, c.tag, str(pos), hkl[0], hkl[1], hkl[2], h, k, l))
            # 2) specifying energy via hardware
            self.d._hardware.setEnergy(c.energy)
            ((h, k, l), params) = self.d._anglesToHkl(pos.totuple())
            self.assert_((abs(h - hkl[0]) < .001) & (abs(k - hkl[1]) < .001) & (abs(l - hkl[2]) < .001), "wrong hkl calcualted for TestScenario=%s, AngleTestScenario=%s, pos=%s):\n  expected hkl=%f %f %f\n  returned hkl=%f %f %f "\
                        % (s.name, c.tag, str(pos), hkl[0], hkl[1], hkl[2], h, k, l))
            del params
        
    def test_hklToAngles(self):
        s = self.sess
        c = self.calc
        
        ## setup session info
        self.d.ubcommands.newub(s.name)
        self.d.ubcommands.setlat(s.name, *s.lattice)
        r = s.ref1; self.d.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r = s.ref2; self.d.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.d.ubcommands.calcub()
        # check the ubcalculation is okay before continuing (useful to check for typos!)        
        self.assert_(norm1(self.d._ubcalc.getUBMatrix() - (matrix(s.umatrix) * (matrix(s.bmatrix)))) <= .0001, \
                                                         "wrong UB matrix after calculating U")
    
        ## setup calculation info
        self.d.hklcommands.hklmode(c.modeNumber)
        # Set fixed parameters
        if c.alpha != None:
            self.d.hklcommands.setpar('alpha', c.alpha)        
        if c.gamma != None:
            self.d.hklcommands.setpar('gamma', c.alpha)                    
    
        # Test each hkl/position pair
        for idx in range(len(c.hklList)):
            (h, k, l) = c.hklList[idx]
            
            expectedangles = self.geometry.internalPositionToPhysicalAngles(c.posList[idx])
            (angles, params) = self.d._hklToAngles(h, k, l, c.energy)
            expectedAnglesString = ("%f " * len(expectedangles)) % expectedangles
            anglesString = ("%f " * len(angles)) % angles    
            namesString = ("%s " * len(self.hardware.getPhysicalAngleNames())) % self.hardware.getPhysicalAngleNames()
            self.assert_(norm1(matrix([list(expectedangles)]) - (matrix([list(angles)]))) <= .03, \
                        "wrong position calcualted for TestScenario=%s, AngleTestScenario=%s, hkl=%f %f %f:\n                       { %s }\n  expected pos=%s\n  returned pos=%s "\
                        % (s.name, c.tag, h, k, l, namesString, expectedAnglesString, anglesString))
            del params
    
    def testSimWithHklAndSixc(self):
        dummySixcScannableGroup = ScannableGroup('sixcgrp', createDummyAxes(['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi']))
        sixcdevice = DiffractometerScannableGroup('SixCircleGammaOnArmGeometry', self.d, dummySixcScannableGroup)
        hkldevice = Hkl('hkl', sixcdevice, self.d)    
            
        self.assertRaises(TypeError, self.d.hklcommands.sim)
        self.assertRaises(TypeError, self.d.hklcommands.sim, hkldevice)
        self.assertRaises(TypeError, self.d.hklcommands.sim, hkldevice, 1, 2, 3)        
        self.assertRaises(TypeError, self.d.hklcommands.sim, 'not a proper scannable', 1)
        self.assertRaises(TypeError, self.d.hklcommands.sim, hkldevice, (1, 2, 'not a number'))

        self.assertRaises(TypeError, self.d.hklcommands.sim, hkldevice, 1) #wrong length for hkl
        self.assertRaises(ValueError, self.d.hklcommands.sim, hkldevice, (1, 2, 3, 4))#wrong length for hkl
        
        s = self.sess
        c = self.calc
        # setup session info
        self.d.ubcommands.newub(s.name)
        self.d.ubcommands.setlat(s.name, *s.lattice)
        r = s.ref1; self.d.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r = s.ref2; self.d.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.d.ubcommands.calcub()
        
        # check the ubcalculation is okay before continuing (useful to check for typos!)        
        self.assert_(norm1(self.d._ubcalc.getUBMatrix() - (matrix(s.umatrix) * (matrix(s.bmatrix)))) <= .0001, \
                                                         "wrong UB matrix after calculating U")
        self.hardware.setEnergy(c.energy)
        # Test each hkl/position pair
        for idx in range(len(c.hklList)):
            hkl = c.hklList[idx]
            pos = c.posList[idx].totuple()
            self.d.hklcommands.sim(sixcdevice, pos)
            self.d.hklcommands.sim(hkldevice, hkl)
    
    def testCheckub(self):
        ## setup session info
        s = self.sess
        self.d.ubcommands.newub(s.name)
        self.d.ubcommands.setlat(s.name, *s.lattice)
        r = s.ref1; self.d.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r = s.ref2; self.d.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.d.ubcommands.calcub()
        print "*** checkub ***"
        print self.d.checkub()
        print "***************"
    
    
class TestDiffractionCalculatorHklWithDataSess2Calc0(BaseTestDiffractionCalculatorWithData, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session2
        self.calc = scenarios.session2.calculations[0]


class TestDiffractionCalculatorHklWithDataSess3Calc0(BaseTestDiffractionCalculatorWithData, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session3
        self.calc = scenarios.session3.calculations[0]
    
    
class TestSixcBase(unittest.TestCase):
    
    def createDiffcalcAndScannables(self, geometryClass):
        self.en = DummyPD('en')
        group = ScannableGroup('sixcgrp', createDummyAxes(['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi']))    
        self.sixc = DiffractometerScannableGroup('sixc', None, group)
        self.d = create_diffcalc_vlieg(geometryClass(), ScannableHardwareMonitorPlugin(self.sixc, self.en), True, UbCalculationNonPersister())

        self.sixc.setDiffcalcObject(self.d)
        self.hkl = Hkl('hkl', self.sixc, self.d)
        self.d.raiseExceptionsForAllErrors = True


class TestFourcBase(unittest.TestCase):
    
    def createDiffcalcAndScannables(self):
        self.en = DummyPD('en')
        scannableGroup = ScannableGroup('fourcgrp', createDummyAxes(['delta', 'omega', 'chi', 'phi']))    
        self.fourc = DiffractometerScannableGroup('fourc', None, scannableGroup)
        hwmp = ScannableHardwareMonitorPlugin(self.fourc, self.en)
        self.d = create_diffcalc_vlieg(fourc(), hwmp, True, UbCalculationNonPersister())
        self.fourc.setDiffcalcObject(self.d)
        self.hkl = Hkl('hkl', self.fourc, self.d)
        self.d.raiseExceptionsForAllErrors = True


class SixCircleGammaOnArmTest(TestSixcBase):

    def setUp(self):
        TestSixcBase.createDiffcalcAndScannables(self, SixCircleGammaOnArmGeometry) 
        self.hklverbose = Hkl('hkl', self.sixc, self.d, ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.d._hardware.setCut('phi', -180) # cut phi at -180 to match dif
        self.orient()

    def orient(self):
        self.d.ubcommands.newub('b16_270608')
        self.d.ubcommands.setlat('xtal', 3.8401, 3.8401, 5.43072)
        self.en(12.39842 / 1.24)
        self.sixc([5.000, 22.790, 0.000, 1.552, 22.400, 14.255])
        self.d.ubcommands.addref(1, 0, 1.0628)
        self.sixc([5.000, 22.790, 0.000, 4.575, 24.275, 101.320])
        self.d.ubcommands.addref(0, 1, 1.0628)
        self.d.checkub()

    def testDiffractionCalculatorScannableIntegration(self):
        betain = DiffractionCalculatorParameter('betain', 'betain', self.d)
        betain.asynchronousMoveTo(12.34)
        self.assertEqual(betain.getPosition(), 12.34)

    def mode(self, mode, alpha=0, gamma=0, betain=0, betaout=0, phi=0, sig=0, tau=0):
        self.d.hklcommands.hklmode(mode)
        self.d.hklcommands.setpar('alpha', alpha)
        self.d.hklcommands.setpar('gamma', gamma)
        self.d.hklcommands.setpar('betain', betain)   
        self.d.hklcommands.setpar('betaout', betaout)   
        self.d.hklcommands.setpar('phi', phi)   
        self.d.ubcommands.sigtau(sig, tau)

    def test1(self):
        self.mode(1)
        self.hkl([.7, .9, 1.3])
        assert_array_almost_equal((0.0000, 27.3557, 0.0000, 13.6779, 37.7746, 53.9654), self.sixc(), 4)
        print self.hkl
        print self.hklverbose
        
    def test2(self):
        self.mode(1, alpha=5, gamma=0)
        self.hkl([.7, .9, 1.3])
        assert_array_almost_equal((5.0000, 26.9296, 0.0000, 8.4916, 27.2563, 59.5855), self.sixc(), 4)
        
    def test3(self):
        self.mode(1, alpha=5, gamma=10)
        self.hkl([.7, .9, 1.3])
        assert_array_almost_equal((5.0000, 22.9649, 10.0000, 42.2204, 4.9721, 23.0655), self.sixc(), 4)
        
    def test4(self):
        self.mode(2, alpha=5, gamma=10, betain=4) # Fix Bin
        
        self.hkl([.7, .9, 1.3])
        assert_array_almost_equal((5, 22.9649, 10.0000, -11.8850, 4.7799, 80.4416),
                                   self.sixc(), 4, note="[alpha, delta, gamma, omega, chi, phi") 
        
    def test5(self):
        self.mode(1, alpha=5, gamma=10, sig= -1.3500, tau= -106)
        self.hkl([.7, .9, 1.3])        
        assert_array_almost_equal((5.0000, 22.9649, 10.0000, 30.6586, 4.5295, 35.4036), self.sixc(), 4)
        
    def test6(self):
        self.mode(2, alpha=5, gamma=10, sig= -1.3500, tau= -106, betain=6) # Fix Bin
        self.hkl([.7, .9, 1.3])    
        assert_array_almost_equal((5.0000, 22.9649, 10.0000, 2.2388, 4.3898, 65.4395), self.sixc(), 4)
        
    def test7(self):
        self.mode(3, alpha=5, gamma=10, sig= -1.3500, tau= -106, betaout=7) # Fix Bin
        self.hkl([.7, .9, 1.3])    
        assert_array_almost_equal((5.0000, 22.9649, 10.0000, 43.4628, 5.0387, 21.7292), self.sixc(), 4)
        
    def test7a(self):
        self.mode(5, phi=10) #Fix phi
        self.hkl([.7, .9, 1.3])
        
    def test8(self):
        #8
        self.mode(10, gamma=10, sig= -1.35, tau= -106) #5cgBeq
        self.hkl([.7, .9, 1.3])        
        assert_array_almost_equal((6.1937, 22.1343, 10.0000, 46.9523, 1.5102, 18.8112), self.sixc(), 3)

    def test9(self):
        self.mode(13, alpha=5, gamma=10, sig= -1.35, tau= -106) #5cgBeq
        self.hkl([.7, .9, 1.3])        
        assert_array_almost_equal((5.0000, 22.2183, 11.1054, 65.8276, 2.5180, -0.0749), self.sixc(), 4)

    def test10(self):
        self.mode(20, sig= -1.35, tau= -106) #6czBeq
        self.hkl([.7, .9, 1.3])        
        assert_array_almost_equal((8.1693, 22.0156, 8.1693, -40.2188, 1.3500, 106.0000), self.sixc(), 4)
                
    def test11(self):
        self.mode(21, betain=8, sig= -1.35, tau= -106) #6czBin
        self.hkl([.7, .9, 1.3])        
        assert_array_almost_equal((8.0000, 22.0156, 8.3386, -40.0939, 1.3500, 106.0000), self.sixc(), 4)
        
    def test12(self):
        self.mode(22, betaout=1, sig= -1.35, tau= -106) #6czBin
        self.hkl([.7, .9, 1.3])        
        assert_array_almost_equal((15.4706, 22.0994, 1.0000, -45.5521, 1.3500, 106.0000), self.sixc(), 4)
    

class ZAxisGammaOnBaseTest(TestSixcBase):

    def setUp(self):
        TestSixcBase.createDiffcalcAndScannables(self, SixCircleGeometry)
        self.hklverbose = Hkl('hkl', self.sixc, self.d, ('Bout'))
        self.orient()
    
    def orient(self):    
        self.d.ubcommands.newub('From DDIF')
        self.d.ubcommands.setlat('cubic', 1, 1, 1)
        self.en(12.39842 / 1)
        self.d.ubcommands.setu([[1, 0, 0], [0, 1, 0], [0, 0, 1]])    
        self.d.hklcommands.hklmode(20) # zaxis, bisecting
        self.d.ubcommands.sigtau(0, 0)
    
    def checkHKL(self, hkl, adgocp=None, betaout=None, nu=None): 
        self.hklverbose.asynchronousMoveTo(hkl)
        assert_array_almost_equal(self.sixc(), list(adgocp), 3)
        assert_array_almost_equal(self.hklverbose(), (hkl[0], hkl[1], hkl[2], betaout), 3)
        
    def testHKL_001(self):
        self.checkHKL([0, 0, 1], adgocp=[30, 0, 60, 90, 0, 0], betaout=30, nu=0)

    def testHKL_010(self):
        self.checkHKL([0, 1, 0], adgocp=[0, 60, 0, 120, 0, 0], betaout=0, nu=0)

    def testHKL_011(self):
        self.checkHKL([0, 1, 1], adgocp=[30, 54.7356, 90, 125.2644 , 0, 0], betaout=30, nu= -54.7356)

    def testHKL_100(self):
        self.checkHKL([1, 0, 0], adgocp=[0, 60, 0, 30, 0, 0], betaout=0, nu=0)
        
    def testHKL_101(self):
        self.checkHKL([1, 0, 1], adgocp=[30, 54.7356, 90, 35.2644, 0, 0], betaout=30, nu= -54.7356)
        
    def testHKL_110(self):
        #TODO: Modify test to ask that in this case gamma is left unmoved
        self.checkHKL([1, 1, 0], adgocp=[0, 90, 0, 90, 0, 0], betaout=0, nu=0)

    def testHKL_1_1_0001(self):
        self.checkHKL([1, 1, .0001], adgocp=[0.0029, 89.9971, 90.0058, 90.0000, 0, 0], betaout=0.0029, nu=89.9971)

    def testHKL_111(self):
        self.checkHKL([1, 1, 1], adgocp=[30, 54.7356, 150, 99.7356, 0, 0], betaout=30, nu=54.7356)
        
    def testHKL_11_0_0(self):
        self.checkHKL([1.1, 0 , 0], adgocp=[0, 66.7340, 0.0000, 33.3670, 0, 0], betaout=0, nu=0)

    def testHKL_09_0_0(self):
        self.checkHKL([.9, 0, 0], adgocp=[0, 53.4874, 0, 26.7437, 0, 0], betaout=0, nu=0)
        
    def testHKL_07_08_08(self):
        self.checkHKL([.7, .8, .8], adgocp=[23.5782, 59.9980, 76.7037, 84.2591, 0, 0], betaout=23.5782, nu= -49.1014)

    def testHKL_07_08_09(self):
        self.checkHKL([.7, .8, .9], adgocp=[26.74368, 58.6754, 86.6919, 85.3391, 0, 0], betaout=26.7437, nu= -55.8910)

    def testHKL_07_08_1(self):
        self.checkHKL([.7, .8, 1], adgocp=[30, 57.0626, 96.8659, 86.6739, 0, 0], betaout=30, nu= -63.0210)


class ZAxisGammaOnBaseIncludingNuRotationTest(ZAxisGammaOnBaseTest):

    def setUp(self):
        ZAxisGammaOnBaseTest.setUp(self)
        self.nu = DummyPD('nu')
        self.sixc.slaveScannableDriver = NuDriverForSixCirclePlugin(self.nu)


class SixcGammaOnBaseTest(TestSixcBase):

    def setUp(self):
        TestSixcBase.createDiffcalcAndScannables(self, SixCircleGeometry)
        self.hklverbose = Hkl('hkl', self.sixc, self.d, ('Bout'))
        self.orient()

    def orient(self):        
        self.d.ubcommands.newub('From DDIF')
        self.d.ubcommands.setlat('cubic', 1, 1, 1)
        self.en(12.39842 / 1)
        self.d.ubcommands.setu([[1, 0, 0], [0, 1, 0], [0, 0, 1]])    
        self.d.ubcommands.sigtau(0, 0)
    
    def testToFigureOut101and011(self):
        self.hkl([1, 0, 1])
        print "101: ", self.sixc()
        self.hkl([0, 1, 1])
        print "011: ", self.sixc()
        print "**"
    
    def testOrientation(self):
        self.d.ubcommands.newub('cubic')
        self.d.ubcommands.setlat('cubic', 1, 1, 1)
        self.en(39842 / 1)        
        self.d.ubcommands.sigtau(0, 0)
        self.sixc([0, 90, 0, 45, 45, 0])
        self.d.ubcommands.addref(1, 0, 1)
        self.sixc([0, 90, 0, 45, 45, 90])
        self.d.ubcommands.addref(0, 1, 1)
        self.d.checkub()
        res = self.d._ubcalc.getUMatrix()
        des = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.assert_(norm1(res - des) <= .0001)
        print "***"
        self.d.ubcommands.ub()
        print "***"
        self.d.ubcommands.showref()
        print "***"
        self.d.hklcommands.hklmode()
        print "***"


class FiveCircleTest(unittest.TestCase):
    
    def setUp(self):
        self.en = DummyPD('en') 
        group = ScannableGroup('fivecgrp', createDummyAxes(['alpha', 'delta', 'omega', 'chi', 'phi']))    
        self.fivec = DiffractometerScannableGroup('fivec', None, group)
        self.d = create_diffcalc_vlieg(fivec(),
                     ScannableHardwareMonitorPlugin(self.fivec, self.en),
                     True, UbCalculationNonPersister())
        #self.d = Diffcalc(, , True, True, UbCalculationNonPersister())
        self.d.raiseExceptionsForAllErrors = True
        self.fivec.setDiffcalcObject(self.d)
        self.hkl = Hkl('hkl', self.fivec, self.d)
        self.hklverbose = Hkl('hkl', self.fivec, self.d, ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()

    def orient(self):
        self.d.ubcommands.newub('b16_270608')
        self.d.ubcommands.setlat('xtal', 3.8401, 3.8401, 5.43072)
        self.en(12.39842 / 1.24)
        self.fivec([5.000, 22.790, 1.552, 22.400, 14.255])
        self.d.ubcommands.addref(1, 0, 1.0628)
        self.fivec([5.000, 22.790, 4.575, 24.275, 101.320])
        self.d.ubcommands.addref(0, 1, 1.0628)
        self.d.checkub()

    def testSetGammaFails(self):
        self.assertRaises(DiffcalcException, self.d.hklcommands.setpar, 'gamma', 9999)

    def test1(self):
        self.d.hklcommands.hklmode(1)
        self.d.hklcommands.setpar('alpha', 0)
        self.hkl([.7, .9, 1.3])
        assert_array_almost_equal((0.0000, 27.3557, 13.6779, 37.7746, 53.9654), self.fivec(), 4)
        
    def test2(self):
        self.d.hklcommands.hklmode(1)
        self.d.hklcommands.setpar('alpha', 5)
        self.hkl([.7, .9, 1.3])
        assert_array_almost_equal((5.0000, 26.9296, 8.4916, 27.2563, 59.5855), self.fivec(), 4)
       
        
class FourCircleTest(TestFourcBase):
    
    def setUp(self):
        TestFourcBase.createDiffcalcAndScannables(self)
        self.hklverbose = Hkl('hkl', self.fourc, self.d, ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()
    
    def orient(self):
        self.d.ubcommands.newub('fromDiffcalcItself')   # This dataset generated by diffcalc code itself (not a proper test of code guts)
        self.d.ubcommands.setlat('xtal', 3.8401, 3.8401, 5.43072)
        self.en(12.39842 / 1.24)
        self.fourc([22.790, 1.552, 22.400, 14.255])
        self.d.ubcommands.addref(1, 0, 1.0628)
        self.fourc([22.790, 4.575, 24.275, 101.320])
        self.d.ubcommands.addref(0, 1, 1.0628)
        self.d.checkub()
    
    def testSetGammaFails(self):
        self.assertRaises(DiffcalcException, self.d.hklcommands.setpar, 'gamma', 9999)

    def test1(self):
        self.d.hklcommands.hklmode(1)
        self.hkl([.7, .9, 1.3])
        assert_array_almost_equal((27.3557325339904, 13.67786626699521, 23.481729970652825, 47.81491152277463), self.fourc(), 4)


class FourCircleWithcubic(TestFourcBase):
    
    def setUp(self):
        TestFourcBase.createDiffcalcAndScannables(self)
        self.hklverbose = Hkl('hkl', self.fourc, self.d, ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()
    
    def setUp3(self):
        TestFourcBase.createDiffcalcAndScannables(self)
        self.hklverbose = Hkl('hkl', self.fourc, self.d, ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()
        
    def orient(self):
        self.d.ubcommands.newub('cubic')   # This dataset generated by diffcalc code itself (not a proper test of code guts)
        self.d.ubcommands.setlat('cube', 1, 1, 1, 90, 90, 90)
        self.en(12.39842)
        self.fourc([60, 30, 0, 0])
        self.d.ubcommands.addref(1, 0, 0)
        self.fourc([60, 30, 90, 0])
        self.d.ubcommands.addref(0, 0, 1)
        self.d.checkub()

    def testHkl100(self):
        self.d.hklcommands.hklmode(1)
        self.d.ubcommands.sigtau(0, 0)
        self.hkl([1, 0, 0])
        assert_array_almost_equal(self.fourc(), (60, -60, 0, 90), 4)
        #dif gives
        #h       k       l       alpha    delta    gamma    omega      chi      phi
        #1.000   0.000   0.000   0.0000  60.0000   0.0000 -60.0000   0.0000  90.0000
        #beta_in beta_out      rho      eta twotheta
        #-0.0000   0.0000   0.0000   0.0000  60.0000

    def testHkl001(self):
        self.d.hklcommands.hklmode(1)
        self.d.ubcommands.sigtau(0, 0)
        self.hkl([0, 0, 1])
        assert_array_almost_equal(self.fourc()[0:3], (60, 30, 90), 4) #(phi is undetermined here)        
        #h       k       l        alpha    delta    gamma    omega      chi      phi
        #0.000   0.000   1.000   0.0000  60.0000   0.0000  30.0000  90.0000  45.0000
        #                          beta_in beta_out      rho      eta twotheta
        #                          30.0000  30.0000  60.0000   0.5236  60.0000

    def testHkl110(self):
        self.d.hklcommands.hklmode(1)
        self.d.ubcommands.sigtau(0, 0)
        self.hkl([1, 1, 0])
        # TODO: No check here!
        #    h       k       l    alpha    delta    gamma    omega   chi      phi
        #1.000   1.000   0.000   0.0000  90.0000   0.0000 135.0000   0.0000 -45.0000
        #                          beta_in beta_out      rho      eta twotheta
        #                           0.0000  -0.0000  -0.0000   0.0000  90.0000
        
        
class FourCircleForI06Experiment(TestFourcBase):
    
    def setUp(self):
        TestFourcBase.createDiffcalcAndScannables(self)
        self.hklverbose = Hkl('hkl', self.fourc, self.d, ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()
        
    def orient(self):
        self.en(1.650)
        self.d.ubcommands.newub('cubic')
        self.d.ubcommands.setlat('xtal', 5.34, 5.34, 13.2, 90, 90, 90)
        self.d.ubcommands.setu([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.d.hklcommands.hklmode(5)
        self.d.hklcommands.setpar('phi', -90)
        self.d.mappercommands.setcut('phi', -180)

    def testHkl001(self):
        self.hkl([0, 0, 1])
        assert_array_almost_equal(self.fourc(), [33.07329403295449, 16.536647016477247, 90.0, -90.0], note="[delta, omega, chi, phi]")
   
#    def testHkl100(self):
#        self.pos_hkl(1, 0, 0)
#        assert_array_almost_equal(self.pos_fourc(), [89.42926563609406, 134.71463281804702, 90.0, -90.0], note="[delta, omega, chi, phi]")
   
    def testHkl101(self):
        self.hkl([1, 0, 1])
        assert_array_almost_equal(self.fourc(), [98.74666191021282, 117.347760720783, 90.0, -90.0], note="[delta, omega, chi, phi]")
