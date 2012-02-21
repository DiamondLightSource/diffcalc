from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.hardware.dummy import DummyHardwareMonitorPlugin
from diffcalc.tools import assert_iterable_almost_equal, mneq_
from diffcalc.ub.commands import UbCommands
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.utils import DiffcalcException, MockRawInput, norm1
from tests.diffcalc import scenarios
import diffcalc.utils # @UnusedImport
import unittest
from diffcalc.ub.calculation import UBCalculation
from diffcalc.hkl.vlieg.ubcalcstrategy import VliegUbCalcStrategy

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

def prepareRawInput(listOfStrings):
    diffcalc.utils.raw_input = MockRawInput(listOfStrings)

prepareRawInput([])


class TestUbCommands(unittest.TestCase):
    
    def setUp(self):
        self.hardware = DummyHardwareMonitorPlugin(('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'))
        self.geometry = SixCircleGammaOnArmGeometry()
        self.ubcalc = UBCalculation(self.hardware, self.geometry, UbCalculationNonPersister(), VliegUbCalcStrategy())
        self.ubcommands = UbCommands(self.hardware, self.geometry, self.ubcalc)
        prepareRawInput([])
        diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True
        
    def testHelpub(self):
        self.assertRaises(TypeError, self.ubcommands.helpub, 'a', 'b')
        self.ubcommands.helpub()
        self.ubcommands.helpub('calcub')
        
    def testNewUb(self):
        self.ubcommands.newub('test1')
        self.assertEqual(self.ubcommands._ubcalc._name, 'test1')
        self.assertRaises(TypeError, self.ubcommands.newub, 1)

    def testNewUbInteractively(self):
        prepareRawInput(['ubcalcname', 'xtal', '1', '2', '3', '91', '92', '93'])
        self.ubcommands.newub()

    def testLoadub(self):
        self.assertRaises(TypeError, self.ubcommands.loadub, (1, 2))        
        
    def testSaveubcalcas(self):
        self.assertRaises(TypeError, self.ubcommands.saveubas, 1)
        self.assertRaises(TypeError, self.ubcommands.saveubas, (1, 2))        
        self.ubcommands.saveubas('blarghh')
    
    def testUb(self):
        self.assertRaises(TypeError, self.ubcommands.showref, (1))
        self.ubcommands.ub()
        self.ubcommands.newub('testubcalc')
        self.ubcommands.ub()        

    def testSetlat(self):
        self.assertRaises(DiffcalcException, self.ubcommands.setlat, 'HCl', 2)# "Exception should result if no UBCalculation started")
        
        self.ubcommands.newub('testing_setlat')
        self.assertRaises(TypeError, self.ubcommands.setlat, 1)
        self.assertRaises(TypeError, self.ubcommands.setlat, 1, 2)
        self.assertRaises(TypeError, self.ubcommands.setlat, 'HCl')        
        self.ubcommands.setlat('NaCl', 1.1)
        self.assertEqual(('NaCl', 1.1, 1.1, 1.1, 90, 90, 90), self.ubcommands._ubcalc._crystal.getLattice())
        self.ubcommands.setlat('NaCl', 1.1, 2.2)
        self.assertEqual(('NaCl', 1.1, 1.1, 2.2, 90, 90, 90), self.ubcommands._ubcalc._crystal.getLattice())
        self.ubcommands.setlat('NaCl', 1.1, 2.2, 3.3)
        self.assertEqual(('NaCl', 1.1, 2.2, 3.3, 90, 90, 90), self.ubcommands._ubcalc._crystal.getLattice())
        self.ubcommands.setlat('NaCl', 1.1, 2.2, 3.3, 91)
        self.assertEqual(('NaCl', 1.1, 2.2, 3.3, 90, 90, 91), self.ubcommands._ubcalc._crystal.getLattice())
        self.assertRaises(TypeError, self.ubcommands.setlat, ('NaCl', 1.1, 2.2, 3.3, 91, 92))
        self.ubcommands.setlat('NaCl', 1.1, 2.2, 3.3, 91, 92, 93)
        assert_iterable_almost_equal(('NaCl', 1.1, 2.2, 3.3, 91, 92, 92.99999999999999),
                                      self.ubcommands._ubcalc._crystal.getLattice())

    def testSetlatInteractive(self):
        self.ubcommands.newub('testing_setlatinteractive')
        prepareRawInput(['xtal', '1', '2', '3', '91', '92', '93'])
        self.ubcommands.setlat()
        getLattice = self.ubcommands._ubcalc._crystal.getLattice
        assert_iterable_almost_equal(getLattice(),
                         ('xtal', 1., 2., 3., 91, 92, 92.999999999999986))                
    
        #Defaults:
        prepareRawInput(['xtal', '', '', '', '', '', ''])
        self.ubcommands.setlat()        
        getLattice = self.ubcommands._ubcalc._crystal.getLattice
        self.assertEqual(getLattice(), ('xtal', 1., 1., 1., 90, 90, 90))                
        
    def testShowref(self):
        self.assertRaises(TypeError, self.ubcommands.showref, (1))
        self.assertEqual(self.ubcommands.showref(), None) # No UBCalculation loaded
        # will be tested, for exceptions at least, implicitely below
        self.ubcommands.newub('testing_showref')
        self.assertEqual(self.ubcommands.showref(), None)#No UBCalculation loaded"
        
    def testAddref(self):
#        self.assertRaises(TypeError, self.ubcommands.addref)
        self.assertRaises(TypeError, self.ubcommands.addref, 1)
        self.assertRaises(TypeError, self.ubcommands.addref, 1, 2)
        self.assertRaises(TypeError, self.ubcommands.addref, 1, 2, 'blarghh')
        self.assertRaises(DiffcalcException, self.ubcommands.addref, 1, 2, 3, (1, 2, 3, 4, 5, 6), 7)    
        # start new ubcalc
        self.ubcommands.newub('testing_addref')        
        reflist = self.ubcommands._ubcalc._reflist # for conveniance
        
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos3 = (3.1, 3.2, 3.3, 3.4, 3.5, 3.6)
        pos4 = (4.1, 4.2, 4.3, 4.4, 4.5 , 4.6)
        #
        self.hardware.setEnergy(1.10)
        self.hardware.setPosition(pos1)
        self.ubcommands.addref(1.1, 1.2, 1.3)
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(1); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([1.1, 1.2, 1.3], pos1, 1.10, None))
        
        self.hardware.setEnergy(2.10)
        self.hardware.setPosition(pos2)
        self.ubcommands.addref(2.1, 2.2, 2.3, 'atag')
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(2); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([2.1, 2.2, 2.3], pos2, 2.10, 'atag'))        
    
        self.ubcommands.addref(3.1, 3.2, 3.3, pos3, 3.10)
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(3); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([3.1, 3.2, 3.3], pos3, 3.10, None))        
                
        self.ubcommands.addref(4.1, 4.2, 4.3, pos4, 4.10, 'tag2')
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(4); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([4.1, 4.2, 4.3], pos4, 4.10, 'tag2'))
    
    def testAddrefInteractively(self):
        prepareRawInput([])
        # start new ubcalc
        self.ubcommands.newub('testing_addref')        
        reflist = self.ubcommands._ubcalc._reflist # for conveniance
        
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos3 = (3.1, 3.2, 3.3, 3.4, 3.5, 3.6)
        pos3s = ['3.1', '3.2', '3.3', '3.4', '3.5', '3.6']
        pos4 = (4.1, 4.2, 4.3, 4.4, 4.5 , 4.6)
        pos4s = ['4.1', '4.2', '4.3', '4.4', '4.5', '4.6']        
        #
        self.hardware.setEnergy(1.10)
        self.hardware.setPosition(pos1)
        prepareRawInput(['1.1', '1.2', '1.3', '', ''])
        self.ubcommands.addref()
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(1); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([1.1, 1.2, 1.3], pos1, 1.10, None))
        
        self.hardware.setEnergy(2.10)
        self.hardware.setPosition(pos2)
        prepareRawInput(['2.1', '2.2', '2.3', '', 'atag'])
        self.ubcommands.addref()
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(2); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([2.1, 2.2, 2.3], pos2, 2.10, 'atag'))        
    
    
#        self.ubcommands.addref(3.1, 3.2, 3.3, pos3, 3.10 )
        prepareRawInput(['3.1', '3.2', '3.3', 'n'] + pos3s + ['3.10', ''])
        self.ubcommands.addref()
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(3); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([3.1, 3.2, 3.3], pos3, 3.10, None))        
        
        
        prepareRawInput(['4.1', '4.2', '4.3', 'n'] + pos4s + ['4.10', 'tag2'])
        self.ubcommands.addref()                        
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(4); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([4.1, 4.2, 4.3], pos4, 4.10, 'tag2'))

    def testEditRefInteractivelyWithCurrentPosition(self):
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        self.ubcommands.newub('testing_editref')
        self.ubcommands.addref(1, 2, 3, pos1, 10, 'tag1')
        self.hardware.setEnergy(11)
        self.hardware.setPosition(pos2)
        prepareRawInput(['1.1', '', '3.1', 'y', ''])# h k l use_current [alpha delta .. energy] tag
        self.ubcommands.editref(1)
        
        reflist = self.ubcommands._ubcalc._reflist # for conveniance
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(1); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([1.1, 2, 3.1], pos2, 11, 'tag1'))

    def testEditRefInteractivelyWithEditedPosition(self):
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos2s = ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6']
        self.ubcommands.newub('testing_editref')
        self.ubcommands.addref(1, 2, 3, pos1, 10, 'tag1')
        prepareRawInput(['1.1', '', '3.1', 'n'] + pos2s + ['12', 'newtag']) # h k l use_current [alpha delta .. energy] tag
        self.ubcommands.editref(1)
        
        reflist = self.ubcommands._ubcalc._reflist # for conveniance
        ([h, k, l], pos, energy, tag, time) = reflist.getReflectionInExternalAngles(1); del time
        self.assertEqual(([h, k, l], pos, energy, tag), ([1.1, 2, 3.1], pos2, 12, 'newtag'))

    def testSwapref(self):
        self.assertRaises(TypeError, self.ubcommands.swapref, 1)
        self.assertRaises(TypeError, self.ubcommands.swapref, 1, 2, 3)
        self.assertRaises(TypeError, self.ubcommands.swapref, 1, 1.1)
        self.ubcommands.newub('testing_swapref')
        pos = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        self.ubcommands.addref(1, 2, 3, pos, 10, 'tag1')
        self.ubcommands.addref(1, 2, 3, pos, 10, 'tag2')
        self.ubcommands.addref(1, 2, 3, pos, 10, 'tag3')
        self.ubcommands.swapref(1, 3)
        self.ubcommands.swapref(1, 3)
        self.ubcommands.swapref(3, 1) # end flipped
        reflist = self.ubcommands._ubcalc._reflist # for conveniance
        ([h, k, l], pos, energy, tag1, time) = reflist.getReflectionInExternalAngles(1); del h, k, l, pos, energy, time
        ([h, k, l], pos, energy, tag2, time) = reflist.getReflectionInExternalAngles(2); del h, k, l, pos, energy, time
        ([h, k, l], pos, energy, tag3, time) = reflist.getReflectionInExternalAngles(3); del h, k, l, pos, energy, time
        self.assertEqual(tag1, 'tag3')
        self.assertEqual(tag2, 'tag2')
        self.assertEqual(tag3, 'tag1')
        self.ubcommands.swapref()
        ([h, k, l], pos, energy, tag1, time) = reflist.getReflectionInExternalAngles(1); del h, k, l, pos, energy, time
        ([h, k, l], pos, energy, tag2, time) = reflist.getReflectionInExternalAngles(2); del h, k, l, pos, energy, time
        self.assertEqual(tag1, 'tag2')
        self.assertEqual(tag2, 'tag3')

    def testDelref(self):
        self.ubcommands.newub('testing_swapref')
        pos = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        self.ubcommands.addref(1, 2, 3, pos, 10, 'tag1')
        reflist = self.ubcommands._ubcalc._reflist
        reflist.getReflectionInExternalAngles(1) # should not raise error
        self.ubcommands.delref(1)
        self.assertRaises(IndexError, reflist.getReflectionInExternalAngles, 1)

    def testSetu(self):
        # just test calling this method
        #self.ubcommands.setu([[1,2,3],[1,2,3],[1,2,3]])
        self.ubcommands.newub('testsetu')
        self.assertRaises(TypeError, self.ubcommands.setu, 1, 2)
        self.assertRaises(TypeError, self.ubcommands.setu, 1)    
        self.assertRaises(TypeError, self.ubcommands.setu, 'a')            
        self.assertRaises(TypeError, self.ubcommands.setu, [1, 2, 3])        
        self.assertRaises(TypeError, self.ubcommands.setu, [[1, 2, 3], [1, 2, 3], [1, 2]])
        self.assertRaises(DiffcalcException, self.ubcommands.setu, [[1, 2, 3], [1, 2, 3], [1, 2, 3]]) # diffCalcException expected if no lattice set yet
        self.ubcommands.setlat('NaCl', 1.1)
        self.ubcommands.setu([[1, 2, 3], [1, 2, 3], [1, 2, 3]]) # check no exceptions only        
        self.ubcommands.setu(((1, 2, 3), (1, 2, 3), (1, 2, 3))) # check no exceptions only
        
    def testSetuInteractive(self):
        self.ubcommands.newub('testsetu')
        self.ubcommands.setlat('NaCl', 1.1)        
        
        prepareRawInput(['1 2 3', '4 5 6', '7 8 9'])
        self.ubcommands.setu()
        a = self.ubcalc.getUMatrix().tolist()
        self.assertEquals([ list(a[0]), list(a[1]), list(a[2])], [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        
        prepareRawInput(['', ' 9 9.9 99', ''])
        self.ubcommands.setu()
        
        a = self.ubcalc.getUMatrix().tolist()
        self.assertEquals([ list(a[0]), list(a[1]), list(a[2])], [[1, 0, 0], [9, 9.9, 99], [0, 0, 1]])
        
    def testSetub(self):
        # just test calling this method
        #self.ubcommands.setub([[1,2,3],[1,2,3],[1,2,3]])
        self.ubcommands.newub('testsetub')    
        self.assertRaises(TypeError, self.ubcommands.setub, 1, 2)
        self.assertRaises(TypeError, self.ubcommands.setub, 1)    
        self.assertRaises(TypeError, self.ubcommands.setub, 'a')            
        self.assertRaises(TypeError, self.ubcommands.setub, [1, 2, 3])        
        self.assertRaises(TypeError, self.ubcommands.setub, [[1, 2, 3], [1, 2, 3], [1, 2]])
        self.ubcommands.setub([[1, 2, 3], [1, 2, 3], [1, 2, 3]]) # check no exceptions only
        self.ubcommands.setub(((1, 2, 3), (1, 2, 3), (1, 2, 3))) # check no exceptions only            

    def testSetUbInteractive(self):
        self.ubcommands.newub('testsetu')
        self.ubcommands.setlat('NaCl', 1.1)        
        
        prepareRawInput(['1 2 3', '4 5 6', '7 8 9'])
        self.ubcommands.setub()
        a = self.ubcalc.getUBMatrix().tolist()
        self.assertEquals([ list(a[0]), list(a[1]), list(a[2])], [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        
        prepareRawInput(['', ' 9 9.9 99', ''])
        self.ubcommands.setub()
        a = self.ubcalc.getUBMatrix().tolist()
        self.assertEquals([ list(a[0]), list(a[1]), list(a[2])], [[1, 0, 0], [9, 9.9, 99], [0, 0, 1]])
    
    def testCalcub(self):        
        self.assertRaises(TypeError, self.ubcommands.calcub, 1) # wrong input
        self.assertRaises(DiffcalcException, self.ubcommands.calcub) # no ubcalc started
        self.ubcommands.newub('testcalcub')

        self.assertRaises(DiffcalcException, self.ubcommands.calcub) # not enougth reflections
        
        s = scenarios.sessions()[0]
        self.ubcommands.setlat(s.name, *s.lattice)
        r = s.ref1; self.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r = s.ref2; self.ubcommands.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.ubcommands.calcub()
        mneq_(self.ubcalc.getUBMatrix(), matrix(s.umatrix) * matrix(s.bmatrix), 4, note="wrong UB matrix after calculating U")    

    def testC2th(self):
        self.ubcommands.newub('testcalcub')
        self.ubcommands.setlat('cube', 1, 1, 1, 90, 90, 90)
        self.assertAlmostEquals(self.ubcommands.c2th((0, 0, 1)), 60)
        
    def testSigtau(self):
        # sigtau [sig tau]
        self.assertRaises(TypeError, self.ubcommands.sigtau, 1)
        self.assertRaises(ValueError, self.ubcommands.sigtau, 1, 'a')
        self.ubcommands.sigtau(1, 2)
        self.ubcommands.sigtau(1, 2.0)
        self.assertEqual(self.ubcalc.getSigma(), 1)
        self.assertEqual(self.ubcalc.getTau(), 2.0)        

    def testSigtauInteractive(self):
        prepareRawInput(['1', '2.'])
        self.ubcommands.sigtau()
        self.assertEqual(self.ubcalc.getSigma(), 1)
        self.assertEqual(self.ubcalc.getTau(), 2.0)
        #Defaults:
        prepareRawInput(['', ''])
        self.hardware.setPosition([None, None, None, None, 3, 4.])
        self.ubcommands.sigtau()
        self.assertEqual(self.ubcalc.getSigma(), -3.)
        self.assertEqual(self.ubcalc.getTau(), -4.)
        
    def testSetWithString(self):
        self.assertRaises(TypeError, self.ubcommands.setlat, 'alpha', 'a')
        self.assertRaises(TypeError, self.ubcommands.setlat, 'alpha', 1, 'a')
