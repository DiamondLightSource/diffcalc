from diffcalc.diffractioncalculator import Diffcalc
from diffcalc.utils import DiffcalcException
from tests.diffcalc import scenarios
from diffcalc.geometry.fivec import fivec
from diffcalc.geometry.fourc import fourc
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.geometry.sixc import SixCircleGeometry
from diffcalc.gdasupport.scannable.parameter import    DiffractionCalculatorParameter
from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc.gdasupport.scannable.base import ScannableGroup
from diffcalc.hardware.dummy import DummyHardwareMonitorPlugin
from diffcalc.hardware.scannable import ScannableHardwareMonitorPlugin
from diffcalc.utils import MockRawInput
import diffcalc.utils # To overide raw_input method 

import unittest
from diffcalc.gdasupport.scannable.slave.NuDriverForSixCirclePlugin import NuDriverForSixCirclePlugin
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.tools import assert_iterable_almost_equal
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix
try:
    from gdascripts.pd.dummy_pds import DummyPD #@UnresolvedImport
except:
    from diffcalc.gdasupport.minigda.scannable.dummy import DummyPD

def prepareRawInput(listOfStrings):
    diffcalc.utils.raw_input = MockRawInput(listOfStrings)

def revertRawInput():
    try:
        del diffcalc.utils.raw_input
    except AttributeError:
        pass    
prepareRawInput([])

def createDummyAxes(names):
    result = []
    for name in names:
        result.append(DummyPD(name))
    return result


class TestDiffractionCalculatorUb(unittest.TestCase):
    
    def setUp(self):
        self.geometry = SixCircleGammaOnArmGeometry()
        self.hardware = DummyHardwareMonitorPlugin(('alpha','delta','gamma','omega','chi','phi'))
        self.d = Diffcalc(self.geometry, self.hardware, True, True, UbCalculationNonPersister() )
        self.d.raiseExceptionsForAllErrors = True
        self.scenarios = scenarios.sessions()
        prepareRawInput([])
        
    def testHelpub(self):
        self.assertRaises(TypeError, self.d.helpub,'a','b')
        self.d.helpub()
        self.d.helpub('calcub')
        
    def testNewUb(self):
        self.d.newub('test1')
        self.assertEqual(self.d._ubcommands._ubcalc._name,'test1')
        self.assertRaises(TypeError, self.d.newub, 1)

    def testNewUbInteractively(self):
        prepareRawInput(['ubcalcname','xtal','1','2','3','91','92','93'])
        self.d.newub()

    def testLoadub(self):
        self.assertRaises(TypeError, self.d.loadub, (1,2))        
        
    def testSaveubcalcas(self):
        self.assertRaises(TypeError, self.d.saveubas,1)
        self.assertRaises(TypeError, self.d.saveubas, (1,2))        
        self.d.saveubas('blarghh')
    
    def testUb(self):
        self.assertRaises(TypeError, self.d.showref, (1))
        self.d.ub()
        self.d.newub('testubcalc')
        self.d.ub()        

    def testSetlat(self):
        self.assertRaises(DiffcalcException, self.d.setlat, 'HCl', 2)# "Exception should result if no UBCalculation started")
        
        self.d.newub('testing_setlat')
        self.assertRaises(TypeError, self.d.setlat, 1)
        self.assertRaises(TypeError, self.d.setlat, 1, 2)
        self.assertRaises(TypeError, self.d.setlat, 'HCl')        
        self.d.setlat('NaCl', 1.1)
        self.assertEqual(('NaCl', 1.1, 1.1, 1.1, 90, 90, 90), self.d._ubcommands._ubcalc._crystal.getLattice())
        self.d.setlat('NaCl', 1.1, 2.2)
        self.assertEqual(('NaCl', 1.1, 1.1, 2.2, 90, 90, 90), self.d._ubcommands._ubcalc._crystal.getLattice())
        self.d.setlat('NaCl', 1.1, 2.2, 3.3)
        self.assertEqual(('NaCl', 1.1, 2.2, 3.3, 90, 90, 90), self.d._ubcommands._ubcalc._crystal.getLattice())
        self.d.setlat('NaCl', 1.1, 2.2, 3.3, 91)
        self.assertEqual(('NaCl', 1.1, 2.2, 3.3, 90, 90, 91), self.d._ubcommands._ubcalc._crystal.getLattice())
        self.assertRaises(TypeError, self.d.setlat, ('NaCl', 1.1, 2.2, 3.3, 91, 92))
        self.d.setlat('NaCl', 1.1, 2.2, 3.3, 91, 92, 93)
        assert_iterable_almost_equal(('NaCl', 1.1, 2.2, 3.3, 91, 92, 92.99999999999999),
                                      self.d._ubcommands._ubcalc._crystal.getLattice())

    def testSetlatInteractive(self):
        self.d.newub('testing_setlatinteractive')
        prepareRawInput(['xtal','1','2','3','91','92','93'])
        self.d.setlat()
        getLattice = self.d._ubcommands._ubcalc._crystal.getLattice
        assert_iterable_almost_equal(getLattice(),
                         ('xtal', 1., 2., 3., 91, 92, 92.999999999999986))                
    
        #Defaults:
        prepareRawInput(['xtal','','','','','',''])
        self.d.setlat()        
        getLattice = self.d._ubcommands._ubcalc._crystal.getLattice
        self.assertEqual( getLattice(), ('xtal', 1., 1., 1., 90, 90, 90))                
        
    def testShowref(self):
        self.assertRaises(TypeError, self.d.showref, (1))
        self.assertEqual(self.d.showref(), None) # No UBCalculation loaded
        # will be tested, for exceptions at least, implicitely below
        self.d.newub('testing_showref')
        self.assertEqual(self.d.showref(), None)#No UBCalculation loaded"
        
    def testAddref(self):
#        self.assertRaises(TypeError, self.d.addref)
        self.assertRaises(TypeError, self.d.addref,1)
        self.assertRaises(TypeError, self.d.addref,1,2)
        self.assertRaises(TypeError, self.d.addref,1,2,'blarghh')
        self.assertRaises(DiffcalcException, self.d.addref,1,2,3,(1,2,3,4,5,6),7)    
        # start new ubcalc
        self.d.newub('testing_addref')        
        reflist = self.d._ubcommands._ubcalc._reflist # for conveniance
        
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos3 = (3.1, 3.2, 3.3, 3.4, 3.5, 3.6)
        pos4 = (4.1, 4.2, 4.3, 4.4, 4.5 ,4.6)
        #
        self.hardware.setEnergy(1.10)
        self.hardware.setPosition(pos1)
        self.d.addref(1.1, 1.2, 1.3)
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(1); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([1.1,1.2,1.3], pos1, 1.10, None))
        
        self.hardware.setEnergy(2.10)
        self.hardware.setPosition(pos2)
        self.d.addref(2.1, 2.2, 2.3, 'atag')
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(2); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([2.1,2.2,2.3], pos2, 2.10, 'atag'))        
    
        self.d.addref(3.1, 3.2, 3.3, pos3, 3.10 )
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(3); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([3.1,3.2,3.3], pos3, 3.10, None))        
                
        self.d.addref(4.1, 4.2, 4.3, pos4, 4.10, 'tag2' )
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(4); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([4.1,4.2,4.3], pos4, 4.10, 'tag2'))
    
    def testAddrefInteractively(self):
        prepareRawInput([])
        # start new ubcalc
        self.d.newub('testing_addref')        
        reflist = self.d._ubcommands._ubcalc._reflist # for conveniance
        
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos3 = (3.1, 3.2, 3.3, 3.4, 3.5, 3.6)
        pos3s= ['3.1', '3.2', '3.3', '3.4', '3.5', '3.6']
        pos4 = (4.1, 4.2, 4.3, 4.4, 4.5 ,4.6)
        pos4s= ['4.1', '4.2', '4.3', '4.4', '4.5', '4.6']        
        #
        self.hardware.setEnergy(1.10)
        self.hardware.setPosition(pos1)
        prepareRawInput(['1.1','1.2','1.3','',''])
        self.d.addref()
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(1); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([1.1,1.2,1.3], pos1, 1.10, None))
        
        self.hardware.setEnergy(2.10)
        self.hardware.setPosition(pos2)
        prepareRawInput(['2.1','2.2','2.3','','atag'])
        self.d.addref()
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(2); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([2.1,2.2,2.3], pos2, 2.10, 'atag'))        
    
    
#        self.d.addref(3.1, 3.2, 3.3, pos3, 3.10 )
        prepareRawInput(['3.1','3.2','3.3','n']+pos3s+['3.10', ''])
        self.d.addref()
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(3); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([3.1,3.2,3.3], pos3, 3.10, None))        
        
        
        prepareRawInput(['4.1','4.2','4.3','n']+pos4s+['4.10', 'tag2'])
        self.d.addref()                        
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(4); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([4.1,4.2,4.3], pos4, 4.10, 'tag2'))

    def testEditRefInteractivelyWithCurrentPosition(self):
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        self.d.newub('testing_editref')
        self.d.addref(1, 2, 3, pos1, 10, 'tag1' )
        self.hardware.setEnergy(11)
        self.hardware.setPosition(pos2)
        prepareRawInput(['1.1','','3.1','y',''])# h k l use_current [alpha delta .. energy] tag
        self.d.editref(1)
        
        reflist = self.d._ubcommands._ubcalc._reflist # for conveniance
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(1); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([1.1,2, 3.1], pos2, 11, 'tag1'))

    def testEditRefInteractivelyWithEditedPosition(self):
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos2s= ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6']
        self.d.newub('testing_editref')
        self.d.addref(1, 2, 3, pos1, 10, 'tag1' )
        prepareRawInput(['1.1','','3.1','n']+pos2s+['12', 'newtag']) # h k l use_current [alpha delta .. energy] tag
        self.d.editref(1)
        
        reflist = self.d._ubcommands._ubcalc._reflist # for conveniance
        ( [h, k, l], pos, energy, tag, time ) = reflist.getReflectionInExternalAngles(1); del time
        self.assertEqual(( [h, k, l], pos, energy, tag), ([1.1,2, 3.1], pos2, 12, 'newtag'))



    def testSwapref(self):
        self.assertRaises(TypeError, self.d.swapref,1)
        self.assertRaises(TypeError, self.d.swapref,1,2,3)
        self.assertRaises(TypeError, self.d.swapref,1,1.1)
        self.d.newub('testing_swapref')
        pos = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        self.d.addref(1, 2, 3, pos, 10, 'tag1')
        self.d.addref(1, 2, 3, pos, 10, 'tag2')
        self.d.addref(1, 2, 3, pos, 10, 'tag3')
        self.d.swapref(1,3)
        self.d.swapref(1,3)
        self.d.swapref(3,1) # end flipped
        reflist = self.d._ubcommands._ubcalc._reflist # for conveniance
        ( [h, k, l], pos, energy, tag1, time ) = reflist.getReflectionInExternalAngles(1); del h,k,l,pos,energy,time
        ( [h, k, l], pos, energy, tag2, time ) = reflist.getReflectionInExternalAngles(2); del h,k,l,pos,energy,time
        ( [h, k, l], pos, energy, tag3, time ) = reflist.getReflectionInExternalAngles(3); del h,k,l,pos,energy,time
        self.assertEqual(tag1,'tag3')
        self.assertEqual(tag2,'tag2')
        self.assertEqual(tag3,'tag1')
        self.d.swapref()
        ( [h, k, l], pos, energy, tag1, time ) = reflist.getReflectionInExternalAngles(1); del h,k,l,pos,energy,time
        ( [h, k, l], pos, energy, tag2, time ) = reflist.getReflectionInExternalAngles(2); del h,k,l,pos,energy,time
        self.assertEqual(tag1,'tag2')
        self.assertEqual(tag2,'tag3')

    def testDelref(self):
        self.d.newub('testing_swapref')
        pos = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        self.d.addref(1, 2, 3, pos, 10, 'tag1')
        reflist = self.d._ubcommands._ubcalc._reflist
        reflist.getReflectionInExternalAngles(1) # should not raise error
        self.d.delref(1)
        self.assertRaises(IndexError, reflist.getReflectionInExternalAngles, 1)

    def testSetu(self):
        # just test calling this method
        #self.d.setu([[1,2,3],[1,2,3],[1,2,3]])
        self.d.newub('testsetu')
        self.assertRaises(TypeError, self.d.setu,1,2)
        self.assertRaises(TypeError, self.d.setu,1)    
        self.assertRaises(TypeError, self.d.setu,'a')            
        self.assertRaises(TypeError, self.d.setu,[1,2,3])        
        self.assertRaises(TypeError, self.d.setu,[[1,2,3],[1,2,3],[1,2]])
        self.assertRaises(DiffcalcException, self.d.setu, [[1,2,3],[1,2,3],[1,2,3]]) # diffCalcException expected if no lattice set yet
        self.d.setlat('NaCl', 1.1)
        self.d.setu([[1,2,3],[1,2,3],[1,2,3]]) # check no exceptions only        
        self.d.setu(((1,2,3),(1,2,3),(1,2,3))) # check no exceptions only
        
    def testSetuInteractive(self):
        self.d.newub('testsetu')
        self.d.setlat('NaCl', 1.1)        
        
        prepareRawInput(['1 2 3','4 5 6','7 8 9'])
        self.d.setu()
        a = self.d._ubcommands.getUMatrix().getArray()
        self.assertEquals([ list(a[0]),list(a[1]), list(a[2])], [[1,2,3],[4,5,6],[7,8,9]])
        
        prepareRawInput(['',' 9 9.9 99',''])
        self.d.setu()
        
        a = self.d._ubcommands.getUMatrix().getArray()
        self.assertEquals([ list(a[0]),list(a[1]), list(a[2])],  [[1,0,0],[9,9.9,99],[0,0,1]])
        
        
    def testSetub(self):
        # just test calling this method
        #self.d.setub([[1,2,3],[1,2,3],[1,2,3]])
        self.d.newub('testsetub')    
        self.assertRaises(TypeError, self.d.setub,1,2)
        self.assertRaises(TypeError, self.d.setub,1)    
        self.assertRaises(TypeError, self.d.setub,'a')            
        self.assertRaises(TypeError, self.d.setub,[1,2,3])        
        self.assertRaises(TypeError, self.d.setub,[[1,2,3],[1,2,3],[1,2]])
        self.d.setub([[1,2,3],[1,2,3],[1,2,3]]) # check no exceptions only
        self.d.setub(((1,2,3),(1,2,3),(1,2,3))) # check no exceptions only            

    def testSetUbInteractive(self):
        self.d.newub('testsetu')
        self.d.setlat('NaCl', 1.1)        
        
        prepareRawInput(['1 2 3','4 5 6','7 8 9'])
        self.d.setub()
        a = self.d._ubcommands.getUBMatrix().getArray()
        self.assertEquals([ list(a[0]),list(a[1]), list(a[2])],  [[1,2,3],[4,5,6],[7,8,9]])
        
        prepareRawInput(['',' 9 9.9 99',''])
        self.d.setub()
        a = self.d._ubcommands.getUBMatrix().getArray()
        self.assertEquals([ list(a[0]),list(a[1]), list(a[2])],  [[1,0,0],[9,9.9,99],[0,0,1]])
    

    def testCalcub(self):        
        self.assertRaises(TypeError,self.d.calcub,1) # wrong input
        self.assertRaises(DiffcalcException, self.d.calcub) # no ubcalc started
        self.d.newub('testcalcub')

        self.assertRaises(DiffcalcException, self.d.calcub) # not enougth reflections
        
        s = self.scenarios[0]
        self.d.setlat(s.name, *s.lattice)
        r=s.ref1; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r=s.ref2; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.d.calcub()
        self.assert_(self.d._ubcommands.getUBMatrix().minus(Matrix(s.umatrix).times(Matrix(s.bmatrix))).norm1()<=.0001,\
                                                         "wrong UB matrix after calculating U")    
    def testCheckub(self, *args):
        self.assertRaises(TypeError,self.d.checkub,1) # wrong input
        print self.d.checkub()
        
    def testC2th(self):
        self.d.newub('testcalcub')
        self.d.setlat('cube', 1,1,1,90,90,90)
        self.assertAlmostEquals(self.d.c2th((0,0,1)), 60)

    
class TestDiffractionCalculatorHkl(unittest.TestCase):
    
#    def setDataAndReturnObject(self, sessionScenario, calculationScenario):
#        self.sess = sessionScenario
#        self.calc = calculationScenario
#        return self
        
    def setUp(self):
        self.geometry = SixCircleGammaOnArmGeometry()
        self.hardware = DummyHardwareMonitorPlugin(('alpha','delta','gamma','omega','chi','phi'))
        self.d = Diffcalc(self.geometry, self.hardware, True, True, UbCalculationNonPersister() )
        self.d.raiseExceptionsForAllErrors = True
        self.scenarios = scenarios.sessions()
        prepareRawInput([])

    def testhelphkl(self):
        self.assertRaises(IndexError, self.d.helphkl,1)
        self.assertRaises(TypeError, self.d.helphkl,'a','b')
        self.assertRaises(IndexError, self.d.helphkl,'not_a_command')        
        self.d.helphkl()
        self.d.helphkl('helphkl')
        
    def testHklmode(self):
        # hklmode [num]
        self.assertRaises(TypeError, self.d.hklmode,1,2)
        self.assertRaises(ValueError, self.d.hklmode,'unwanted_string')
        print self.d.hklmode()
        print self.d.hklmode(1)
        
    def testSigtau(self):
        # sigtau [sig tau]
        self.assertRaises(TypeError, self.d.sigtau,1)
        self.assertRaises(ValueError, self.d.sigtau,1,'a')
        self.d.sigtau(1,2)
        self.d.sigtau(1,2.0)
        self.assertEqual(self.d._ubcommands.getSigma(),1)
        self.assertEqual(self.d._ubcommands.getTau(),2.0)        

    def testSigtauInteractive(self):
        prepareRawInput(['1','2.'])
        self.d.sigtau()
        self.assertEqual(self.d._ubcommands.getSigma(),1)
        self.assertEqual(self.d._ubcommands.getTau(),2.0)
        #Defaults:
        prepareRawInput(['',''])
        self.hardware.setPosition([None,None,None,None, 3, 4.])
        self.d.sigtau()
        self.assertEqual(self.d._ubcommands.getSigma(),-3.)
        self.assertEqual(self.d._ubcommands.getTau(),-4.)

    def testSetWithString(self):
        # 
        self.assertRaises(TypeError, self.d.setlat, 'alpha','a')
        self.assertRaises(TypeError, self.d.setlat, 'alpha',1,'a')
        self.d.setpar()
        self.d.setpar('alpha')
        self.d.setpar('alpha',1)
        self.d.setpar('alpha', 1.1)
        self.assertEqual(self.d._hklcommands._hklcalc.parameter_manager.getParameter('alpha'),1.1)
        
    def testSetWithScannable(self):
        alpha = DummyPD('alpha')
        self.d.setpar(alpha, 1.1)
        self.assertEqual(self.d._hklcommands._hklcalc.parameter_manager.getParameter('alpha'),1.1)
        
    def test_reprSectorLimits(self):
#        self.assertEqual(self.d._reprSectorLimits('alpha'), 'alpha')
#        self.d.setmin('alpha', -10)
#        self.assertEqual(self.d._reprSectorLimits('alpha'), '-10.000000 <= alpha')
#        self.d.setmin('alpha', None)
#        self.assertEqual(self.d._reprSectorLimits('alpha'), 'alpha')
#        self.d.setmax('alpha', 10)
#        self.assertEqual(self.d._reprSectorLimits('alpha'), 'alpha <= 10.000000')
#        self.d.setmin('alpha', -10)
#        self.assertEqual(self.d._reprSectorLimits('alpha'), '-10.000000 <= alpha <= 10.000000')
        
        self.d.setmin('phi', -1)
        print "*******"
        self.d.setmin()
        print "*******"
        self.d.setmax()
        print "*******"

    def testMapper(self):
        # mapper
        self.d.mapper() # should print its state
        self.assertRaises(TypeError, self.d.mapper, 1)
        self.assertRaises(TypeError, self.d.mapper, 'a', 1)

    def testTransformsOnOff(self):
        # transforma [on/off/auto/manual]
        ss=self.d._mapper._sectorSelector
        self.d.transforma() # should print mapper state
        self.assertEquals(ss.transforms, [], "test assumes transforms are off to start")
        self.d.transforma('on')
        self.assertEquals(ss.transforms, ['a'])
        self.d.transformb('on')
        self.assertEquals(ss.transforms, ['a','b'])
        self.d.transformc('off')
        self.assertEquals(ss.transforms, ['a','b'])
        self.d.transformb('off')
        self.assertEquals(ss.transforms, ['a'])

    def testTransformsAuto(self):
        ss=self.d._mapper._sectorSelector
        self.assertEquals(ss.autotransforms, [], "test assumes transforms are off to start")
        self.d.transforma('auto')
        self.assertEquals(ss.autotransforms, ['a'])
        self.d.transformb('auto')
        self.assertEquals(ss.autotransforms, ['a','b'])
        self.d.transformc('manual')
        self.assertEquals(ss.autotransforms, ['a','b'])
        self.d.transformb('manual')
        self.assertEquals(ss.autotransforms, ['a'])
    
    def testTransformsBadInput(self):
        self.assertRaises(TypeError, self.d.transforma, 1)
        self.assertRaises(TypeError, self.d.transforma, 'not_valid')
        self.assertRaises(TypeError, self.d.transforma, 'auto', 1)

    def testSector(self):
        #sector [0-7]
        ss=self.d._mapper._sectorSelector
        self.d.sector() # should print mapper state
        self.assertEquals(ss.sector, 0, "test assumes sector is 0 to start")
        self.d.sector(1)
        self.assertEquals(ss.sector, 1)
        self.assertRaises(TypeError, self.d.sector, 1, 2)
        self.assertRaises(TypeError, self.d.sector, 'a')

    def testAutosectors(self):
        #autosector [0-7]
        ss=self.d._mapper._sectorSelector
        self.d.autosector() # should print mapper state
        self.assertEquals(ss.autosectors, [], "test assumes no auto sectors to start")
        self.d.autosector(1)
        self.assertEquals(ss.autosectors, [1])
        self.d.autosector(1,2)
        self.assertEquals(ss.autosectors, [1,2])
        self.d.autosector(1)
        self.assertEquals(ss.autosectors, [1])
        self.d.autosector(3)
        self.assertEquals(ss.autosectors, [3])
        self.assertRaises(TypeError, self.d.autosector, 1, 'a')
        self.assertRaises(TypeError, self.d.autosector, 'a')

    def testSetcut(self):
        print "*******"
        self.d.setcut()
        print "*******"
        self.d.setcut('alpha')
        print "*******"
        self.d.setcut('alpha', -181)
        print "*******"
        self.assertEquals(self.d._hardware.getCuts()['alpha'],-181)
        self.assertRaises(ValueError, self.d.setcut, 'alpha', 'not a number')
        self.assertRaises(KeyError, self.d.setcut, 'not an axis', 1)
                          
class BaseTestDiffractionCalculatorHklWithData():
    
    def setSessionAndCalculation(self):
        raise Exception("Abstract")

    def setUp(self):
        self.geometry = SixCircleGammaOnArmGeometry()
        self.hardware = DummyHardwareMonitorPlugin(('alpha','delta','gamma','omega','chi','phi'))
        self.d = Diffcalc(self.geometry, self.hardware, True, True, UbCalculationNonPersister())
        self.d.raiseExceptionsForAllErrors = True
        #self.scenarios = scenarios.sessions()
        self.setSessionAndCalculation()
        prepareRawInput([])
    
    def setDataAndReturnObject(self, sessionScenario, calculationScenario):
        self.sess = sessionScenario
        self.calc = calculationScenario
        return self
    
    def test_anglesToHkl(self):
        
        self.assertRaises(DiffcalcException, self.d._anglesToHkl ,(1,2,3,4,5,6)) # because no energy has been set yet
        self.d._hardware.setEnergy(10)
        self.assertRaises(DiffcalcException, self.d._anglesToHkl ,(1,2,3,4,5,6)) # because no ub matrix has been calculated yet
        s=self.sess
        c=self.calc
        
        # setup session info
        self.d.newub(s.name)
        self.d.setlat(s.name, *s.lattice)
        r=s.ref1; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r=s.ref2; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.d.calcub()
        
        # check the ubcalculation is okay before continuing (useful to check for typos!)        
        self.assert_(self.d._ubcommands.getUBMatrix().minus(Matrix(s.umatrix).times(Matrix(s.bmatrix))).norm1()<=.0001,\
                                                         "wrong UB matrix after calculating U")
        # Test each hkl/position pair
        for idx in range(len(c.hklList)):
            hkl=c.hklList[idx]
            pos = c.posList[idx]
            # 1) specifying energy explicitely
            ((h,k,l), params) = self.d._anglesToHkl(pos.totuple(),c.energy)
            self.assert_( (abs(h-hkl[0])<.001) & (abs(k-hkl[1])<.001) & (abs(l-hkl[2])<.001),"wrong hkl calcualted for TestScenario=%s, AngleTestScenario=%s, pos=%s):\n  expected hkl=%f %f %f\n  returned hkl=%f %f %f "\
                        % (s.name, c.tag, str(pos), hkl[0], hkl[1], hkl[2], h, k, l ) )
            # 2) specifying energy via hardware
            self.d._hardware.setEnergy(c.energy)
            ((h,k,l), params) = self.d._anglesToHkl(pos.totuple())
            self.assert_( (abs(h-hkl[0])<.001) & (abs(k-hkl[1])<.001) & (abs(l-hkl[2])<.001),"wrong hkl calcualted for TestScenario=%s, AngleTestScenario=%s, pos=%s):\n  expected hkl=%f %f %f\n  returned hkl=%f %f %f "\
                        % (s.name, c.tag, str(pos), hkl[0], hkl[1], hkl[2], h, k, l ) )
            del params
        
    def test_hklToAngles(self):
        s=self.sess
        c=self.calc
        
        ## setup session info
        self.d.newub(s.name)
        self.d.setlat(s.name, *s.lattice)
        r=s.ref1; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r=s.ref2; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.d.calcub()
        # check the ubcalculation is okay before continuing (useful to check for typos!)        
        self.assert_(self.d._ubcommands.getUBMatrix().minus(Matrix(s.umatrix).times(Matrix(s.bmatrix))).norm1()<=.0001,\
                                                         "wrong UB matrix after calculating U")
    
        ## setup calculation info
        self.d.hklmode(c.modeNumber)
        # Set fixed parameters
        if c.alpha!=None:
            self.d.setpar('alpha',c.alpha)        
        if c.gamma!=None:
            self.d.setpar('gamma',c.alpha)                    
    
        # Test each hkl/position pair
        for idx in range(len(c.hklList)):
            (h,k,l) = c.hklList[idx]
            
            expectedangles = self.geometry.internalPositionToPhysicalAngles(c.posList[idx])
            (angles, params) = self.d._hklToAngles(h, k, l, c.energy)
            expectedAnglesString = ("%f "*len(expectedangles)) % expectedangles
            anglesString = ("%f "*len(angles)) % angles    
            namesString = ("%s "*len(self.hardware.getPhysicalAngleNames()) ) % self.hardware.getPhysicalAngleNames()
            self.assert_(Matrix([list(expectedangles)]).minus(Matrix([list(angles)])).normF()<=.03,\
                        "wrong position calcualted for TestScenario=%s, AngleTestScenario=%s, hkl=%f %f %f:\n                       { %s }\n  expected pos=%s\n  returned pos=%s "\
                        % (s.name, c.tag, h, k, l, namesString, expectedAnglesString, anglesString ))
            del params
    
    def testSimWithHklAndSixc(self):
        dummySixcScannableGroup = ScannableGroup('sixcgrp', createDummyAxes(['alpha','delta','gamma','omega','chi','phi']))
        sixcdevice = DiffractometerScannableGroup('SixCircleGammaOnArmGeometry', self.d, dummySixcScannableGroup)
        hkldevice = Hkl('hkl', sixcdevice, self.d)    
            
        self.assertRaises(TypeError,self.d.sim)
        self.assertRaises(TypeError,self.d.sim, hkldevice)
        self.assertRaises(TypeError,self.d.sim, hkldevice, 1, 2, 3)        
        self.assertRaises(TypeError, self.d.sim, 'not a proper scannable', 1)
        self.assertRaises(TypeError, self.d.sim, hkldevice, (1,2,'not a number'))

        self.assertRaises(TypeError, self.d.sim, hkldevice, 1) #wrong length for hkl
        self.assertRaises(ValueError, self.d.sim, hkldevice, (1,2,3,4))#wrong length for hkl
        
        s=self.sess
        c=self.calc
        # setup session info
        self.d.newub(s.name)
        self.d.setlat(s.name, *s.lattice)
        r=s.ref1; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r=s.ref2; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.d.calcub()
        
        # check the ubcalculation is okay before continuing (useful to check for typos!)        
        self.assert_(self.d._ubcommands.getUBMatrix().minus(Matrix(s.umatrix).times(Matrix(s.bmatrix))).norm1()<=.0001,\
                                                         "wrong UB matrix after calculating U")
        self.hardware.setEnergy(c.energy)
        # Test each hkl/position pair
        for idx in range(len(c.hklList)):
            hkl=c.hklList[idx]
            pos = c.posList[idx].totuple()
            self.d.sim(sixcdevice, pos)
            self.d.sim(hkldevice, hkl)
    
    def testCheckub(self):
        ## setup session info
        s=self.sess
        self.d.newub(s.name)
        self.d.setlat(s.name, *s.lattice)
        r=s.ref1; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        r=s.ref2; self.d.addref(r.h, r.k, r.l, r.pos.totuple(), r.energy, r.tag)
        self.d.calcub()
        print "*** checkub ***"
        print self.d.checkub()
        print "***************"
    
class AdhocTestIncludingExternalScannables(unittest.TestCase):
    
    def getDCCommands(self):
        d=self.d
        return (d.newub, d.setlat, d.addref, d.checkub, d.sigtau, d.hklmode, d.setpar)
    
    def pos_en(self, *args):
        if len(args):
            self.en.asynchronousMoveTo(args[0])
        else:
            return self.en.getPosition()
        
    def pos_hkl(self, *args):
        if len(args):
            self.hkl.asynchronousMoveTo(args)
        else:
            return self.hkl.getPosition()                    

    def pos_hklverbose(self, *args):
        if len(args):
            self.hklverbose.asynchronousMoveTo(args)
        else:
            return self.hklverbose.getPosition()    

    def areClose(self, expected, actual):
        if Matrix([expected]).minus(Matrix([actual])).norm1()<=.001:
            return True
        else:
            print "              alpha     delta      gamma      omega        chi      phi"
            fmt = "Expected = "+ "% f"*len(tuple(expected))
            print  fmt % tuple(expected)
            fmt = "Actual   ="+ "% f"*len(tuple(actual))
            print fmt %tuple(actual)
            return False

class SixCircleGammaOnArmAdhocTestIncludingExternalScannables(AdhocTestIncludingExternalScannables):

    def setUp(self):        
        self.en = DummyPD('en')
        dummySixCircleScannableGroup = ScannableGroup('sixcgrp', createDummyAxes(['alpha','delta','gamma','omega','chi','phi']))    
        self.SixCircleGammaOnArmGeometry = DiffractometerScannableGroup('SixCircleGammaOnArmGeometry', None, dummySixCircleScannableGroup)
        hwmp = ScannableHardwareMonitorPlugin(self.SixCircleGammaOnArmGeometry, self.en)
        self.d = Diffcalc(SixCircleGammaOnArmGeometry(), hwmp, True, True, UbCalculationNonPersister())
        self.SixCircleGammaOnArmGeometry.setDiffcalcObject(self.d)
        self.hkl= Hkl('hkl', self.SixCircleGammaOnArmGeometry, self.d)
        self.hklverbose = Hkl('hkl', self.SixCircleGammaOnArmGeometry, self.d, ('theta','2theta','Bin','Bout','azimuth') )
        prepareRawInput([])
    
    def pos_sixc(self, *args):
        if len(args):
            self.SixCircleGammaOnArmGeometry.asynchronousMoveTo(args)
        else:
            return self.SixCircleGammaOnArmGeometry.getPosition()

    def testDiffractionCalculatorScannableIntegration(self):
        betain = DiffractionCalculatorParameter('betain', 'betain', self.d)
        betain.asynchronousMoveTo(12.34)
        self.assertEqual(betain.getPosition(),12.34)

    def testWithAdhocScript(self):
            
        (pos_sixc, pos_en, pos_hkl, pos_hklverbose) = (self.pos_sixc, self.pos_en, self.pos_hkl, self.pos_hklverbose)
        del pos_hklverbose
        (newub, setlat, addref, checkub, sigtau, hklmode, set) = self.getDCCommands()
        
        newub('b16_270608')
        setlat('xtal', 3.8401, 3.8401, 5.43072)
        pos_en(12.39842/1.24)
        pos_sixc( 5.000, 22.790, 0.000, 1.552, 22.400, 14.255)
        addref(1, 0, 1.0628)
        pos_sixc(5.000, 22.790, 0.000, 4.575, 24.275, 101.320)
        addref(0, 1, 1.0628)
        checkub()
        
        ### Alpha parameter set to track alpha axis  ###
        self.d.trackalpha(True)
        
        hklmode(1)
        sigtau(0,0)
        pos_sixc(0, None, None, None, None, None) #setalpha(0)
        set('gamma',0)
        
        #1
        pos_hkl(.7,.9,1.3)
        resultDif = (0.0000,  27.3557, 0.0000,  13.6779,  37.7746,  53.9654)
        result = pos_sixc()
        self.assert_(self.areClose(resultDif, result))
        print self.hkl
        print self.hklverbose
        
        #2
        pos_sixc(5, None, None, None, None, None) #setalpha(5)
        pos_hkl(.7,.9,1.3)
        resultDif = (5.0000, 26.9296, 0.0000, 8.4916, 27.2563, 59.5855)
        result = pos_sixc()
        self.assert_(self.areClose(resultDif, result))
        
        #3
        set('gamma',10)
        pos_hkl(.7,.9,1.3)
        resultDif = (5.0000, 22.9649, 10.0000, 42.2204, 4.9721, 23.0655)
        result = pos_sixc()        
        self.assert_(self.areClose(resultDif, result))
        
        #4
        hklmode(2) # Fix Bin
        set('betain',4)
        # cut phi at -180 to match dif
        oldcuts = self.d._hardware.getCuts()
        self.d._hardware.setCut('phi', -180)
        pos_hkl(.7,.9,1.3)
        self.d._hardware.setCut('phi', oldcuts['phi'])
        resultDif = ( 5, 22.9649, 10.0000, -11.8850, 4.7799, 80.4416)
        result = pos_sixc()
        self.assert_(self.areClose(resultDif, result), "\n%s!=\n%s"%(result, resultDif))
        #print self.hkl.simulateMoveTo((.7,.9,1.3))
        
        #5
        hklmode(1)
        sigtau(-1.3500,-106)
        pos_hkl(.7,.9,1.3)        
        resultDif = (5.0000, 22.9649, 10.0000, 30.6586, 4.5295, 35.4036)
        result = pos_sixc()        
        #print self.hkl.simulateMoveTo((.7,.9,1.3))
        self.assert_(self.areClose(resultDif, result))
        
        #6
        hklmode(2) # Fix Bin
        set('betain',6)
        pos_hkl(.7,.9,1.3)    
        resultDif = (5.0000, 22.9649, 10.0000, 2.2388, 4.3898, 65.4395)
        result = pos_sixc()        
        #print self.hkl.simulateMoveTo((.7,.9,1.3))
        self.assert_(self.areClose(resultDif, result))
        
        #7
        hklmode(3) # Fix Bout
        set('betaout',7)
        pos_hkl(.7,.9,1.3)    
        resultDif = (5.0000, 22.9649, 10.0000, 43.4628, 5.0387, 21.7292)
        result = pos_sixc()        
        print self.hkl.simulateMoveTo((.7,.9,1.3))
        self.assert_(self.areClose(resultDif, result))

        #7a
        hklmode(5) #Fix phi
        set('phi',10)
        pos_hkl(.7,.9,1.3)
        print pos_sixc()
        print self.hkl.simulateMoveTo((.7,.9,1.3))
        print "****"
        
        #8
        hklmode(10) #5cgBeq
        set('gamma',10)
        sigtau(-1.35,-106)
        pos_hkl(.7,.9,1.3)        
        resultDif = (6.1937,  22.1343,  10.0000,  46.9523,   1.5102,  18.8112)
        result = pos_sixc()        
        #print self.hkl.simulateMoveTo((.7,.9,1.3))
        self.assert_(self.areClose(resultDif, result))

        #9
        hklmode(13) # 5caBeq
        pos_sixc(5, None, None, None, None, None) # setalpha(5)
        pos_hkl(.7,.9,1.3)        
        resultDif = (5.0000, 22.2183, 11.1054, 65.8276, 2.5180, -0.0749)
        result = pos_sixc()        
        #print self.hkl.simulateMoveTo((.7,.9,1.3))
        self.assert_(self.areClose(resultDif, result), "\n%s!=\n%s"%(result, resultDif))

        #10
        hklmode(20) #6czBeq
        pos_hkl(.7,.9,1.3)        
        resultDif = (8.1693, 22.0156, 8.1693, -40.2188, 1.3500, 106.0000)
        result = pos_sixc()        
        #print self.hkl.simulateMoveTo((.7,.9,1.3))
        self.assert_(self.areClose(resultDif, result))
                
        #11
        hklmode(21) #6czBin
        set('betain',8)
        pos_hkl(.7,.9,1.3)        
        resultDif = (8.0000, 22.0156, 8.3386, -40.0939, 1.3500, 106.0000)
        result = pos_sixc()        
        #print self.hkl.simulateMoveTo((.7,.9,1.3))
        self.assert_(self.areClose(resultDif, result))
        
        #12
        hklmode(22) #6czBin
        set('betaout',1)
        pos_hkl(.7,.9,1.3)        
        resultDif = (15.4706, 22.0994, 1.0000, -45.5521, 1.3500, 106.0000)
        result = pos_sixc()        
        #print self.hkl.simulateMoveTo((.7,.9,1.3))
        self.assert_(self.areClose(resultDif, result))
        
class ZAxisGammaOnBaseIncludingExternalScannables(AdhocTestIncludingExternalScannables):

    def setUp(self):        
        self.en = DummyPD('en')
        dummySixCircleScannableGroup = ScannableGroup('sixcgrp', createDummyAxes(['alpha','delta','gamma','omega','chi','phi']))    
        self.SixCircleGammaOnArmGeometry = DiffractometerScannableGroup('SixCircleGammaOnArmGeometry', None, dummySixCircleScannableGroup)
        hwmp = ScannableHardwareMonitorPlugin(self.SixCircleGammaOnArmGeometry, self.en)
        self.d = Diffcalc(SixCircleGeometry(), hwmp, True, True, UbCalculationNonPersister())
        self.SixCircleGammaOnArmGeometry.setDiffcalcObject(self.d)
        self.hkl= Hkl('hkl', self.SixCircleGammaOnArmGeometry, self.d)
        self.hklverbose = Hkl('hkl', self.SixCircleGammaOnArmGeometry, self.d, ('Bout') )
        prepareRawInput([])
        
        (newub, setlat, _, _, sigtau, hklmode, _) = self.getDCCommands()
        newub('From DDIF')
        setlat('cubic', 1, 1, 1)
        self.pos_en(12.39842/1)
        self.d.setu([[1,0,0],[0,1,0],[0,0,1]])    
        hklmode(20) # zaxis
        sigtau(0,0)
    
    def pos_sixc(self, *args):
        if len(args):
            self.SixCircleGammaOnArmGeometry.asynchronousMoveTo(args)
        else:
            return self.SixCircleGammaOnArmGeometry.getPosition()
    
    def _testHKL(self, h, k, l,  a, d, g, o, c, p,  betaout, nu):
        self.pos_hkl(h, k, l)
        self.assert_(self.areClose(self.pos_sixc(), (a, d, g, o, c, p)), 'a, d, g, o, c, p\n%s!=\n%s'%(self.pos_sixc(), (a, d, g, o, c, p)) )
        self.assert_(self.areClose(self.hklverbose(), (h, k, l, betaout)), 'h, k, l, betaout\n%s!=\n%s'%(self.hklverbose(), (h, k, l, betaout)) )
        # nu ignored for now
        
    def testHKL_001(self):
        h, k, l = 0, 0, 1
        a, d, g, o, c, p = 30, 0, 60, 90, 0, 0 # NOTE: DDIF gives omega = 45, nut the case is degenerate.
        betaout = 30
        nu = 0
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)

    def testHKL_010(self):
        h, k, l = 0, 1, 0
        a, d, g, o, c, p = 0, 60, 0, 120, 0, 0
        betaout = 0
        nu = 0
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)

    def testHKL_011(self):
        h, k, l = 0, 1, 1
        a, d, g, o, c, p = 30, 54.7356, 90, 125.2644 , 0, 0 
        betaout = 30
        nu = -54.7356  
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)

    def testHKL_100(self):
        h, k, l = 1, 0, 0
        a, d, g, o, c, p = 0, 60, 0, 30, 0, 0
        betaout = 0
        nu = 0
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)
        
    def testHKL_101(self):
        h, k, l = 1, 0, 1
        a, d, g, o, c, p = 30, 54.7356, 90, 35.2644, 0, 0
        betaout = 30
        nu = -54.7356
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)
        
    def testHKL_110(self):
        h, k, l = 1, 1, 0 
        a, d, g, o, c, p = 0, 90, 0, 90, 0, 0 # NOTE: DDIF gave gamma = 180, here
        #TODO: Modify test to ask that in this case gamma is left unmoved
        betaout = 0
        nu = 0
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)

    def testHKL_1_1_0001(self):
        h, k, l = 1, 1, .0001
        a, d, g, o, c, p =  0.0029, 89.9971, 90.0058, 90.0000, 0, 0
        betaout = 0.0029
        nu = 89.9971
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)

    def testHKL_111(self):
        h, k, l = 1, 1, 1
        a, d, g, o, c, p = 30, 54.7356, 150, 99.7356, 0, 0 
        betaout = 30
        nu = 54.7356
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)
        
    def testHKL_11_0_0(self):
        h, k, l = 1.1, 0 ,0
        a, d, g, o, c, p = 0, 66.7340, 0.0000, 33.3670, 0, 0
        betaout = 0
        nu = 0
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)

    def testHKL_09_0_0(self):
        h, k, l = .9, 0, 0
        a, d, g, o, c, p = 0, 53.4874, 0, 26.7437, 0, 0
        betaout = 0
        nu = 0
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)
        
    def testHKL_07_08_08(self):
        h, k, l = .7, .8, .8
        a, d, g, o, c, p = 23.5782, 59.9980, 76.7037, 84.2591, 0, 0
        betaout = 23.5782
        nu = -49.1014
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)

    def testHKL_07_08_09(self):
        h, k, l = .7, .8, .9
        a, d, g, o, c, p = 26.743, 58.6754, 86.6919, 85.3391, 0, 0
        betaout = 26.7437
        nu = -55.8910
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)

    def testHKL_07_08_1(self):
        h, k, l = .7, .8, 1
        a, d, g, o, c, p = 30, 57.0626, 96.8659, 86.6739, 0, 0
        betaout = 30
        nu = -63.0210
        self._testHKL(h, k, l,  a, d, g, o, c, p,  betaout, nu)

class ZAxisGammaOnBaseIncludingExternalScannablesAndNuRotation(ZAxisGammaOnBaseIncludingExternalScannables):

    def setUp(self):
        ZAxisGammaOnBaseIncludingExternalScannables.setUp(self)
        self.nu = DummyPD('nu')
        self.SixCircleGammaOnArmGeometry.slaveScannableDriver = NuDriverForSixCirclePlugin(self.nu)

    def _testHKL(self, h, k, l,  a, d, g, o, c, p,  betaout, nu):
        ZAxisGammaOnBaseIncludingExternalScannables._testHKL(self, h, k, l,  a, d, g, o, c, p,  betaout, None)
        self.assertAlmostEquals(nu, self.nu(), 4)

class SixcGammaOnBaseIncludingExternalScannables(AdhocTestIncludingExternalScannables):

    def setUp(self):        
        self.en = DummyPD('en')
        dummySixCircleScannableGroup = ScannableGroup('sixcgrp', createDummyAxes(['alphaB','deltaB','gammaB','omegaB','chiB','phiB']))    
        self.SixCircleGammaOnArmGeometry = DiffractometerScannableGroup('SixCircleGammaOnArmGeometry', None, dummySixCircleScannableGroup)
        hwmp = ScannableHardwareMonitorPlugin(self.SixCircleGammaOnArmGeometry, self.en)
        self.d = Diffcalc(SixCircleGeometry(), hwmp, True, True, UbCalculationNonPersister())
        self.SixCircleGammaOnArmGeometry.setDiffcalcObject(self.d)
        self.hkl= Hkl('hkl', self.SixCircleGammaOnArmGeometry, self.d)
        self.hklverbose = Hkl('hkl', self.SixCircleGammaOnArmGeometry, self.d, ('Bout') )
        prepareRawInput([])
        (newub, setlat, _, _, sigtau, hklmode, _) = self.getDCCommands()
        newub('From DDIF')
        setlat('cubic', 1, 1, 1)
        self.pos_en(12.39842/1)
        self.d.setu([[1,0,0],[0,1,0],[0,0,1]])    
        sigtau(0,0)
        
    
    def pos_sixc(self, *args):
        if len(args):
            self.SixCircleGammaOnArmGeometry.asynchronousMoveTo(args)
        else:
            return self.SixCircleGammaOnArmGeometry.getPosition()
    
    def testToFigureOut101and011(self):
        (pos_sixc, pos_en, pos_hkl, _) = (self.pos_sixc, self.pos_en, self.pos_hkl, self.pos_hklverbose)
        (newub, _setlat, addref, checkub, sigtau, hklmode, set) = self.getDCCommands()
        self.pos_hkl(1,0,1)
        print "101: ", self.pos_sixc()
        self.pos_hkl(0,1,1)
        print "011: ", self.pos_sixc()
        print "**"
    
    def testOrientation(self):
        (pos_sixc, pos_en, pos_hkl, _) = (self.pos_sixc, self.pos_en, self.pos_hkl, self.pos_hklverbose)
        (newub, setlat, addref, checkub, sigtau, hklmode, set) = self.getDCCommands()
        newub('cubic')
        setlat('cubic', 1, 1, 1)
        self.pos_en(12.39842/1)        
        sigtau(0,0)
        pos_sixc(0, 90, 0, 45, 45, 0)
        addref(1, 0, 1)
        pos_sixc(0, 90, 0, 45, 45, 90)
        addref(0, 1, 1)
        checkub()
        res = self.d._ubcommands.getUMatrix()
        des = Matrix([[1,0,0],[0,1,0],[0,0,1]])
        self.assert_( res.minus(des).norm1()<=.0001 )
        print "***"
        self.d.ub()
        print "***"
        self.d.showref()
        print "***"
        self.d.hklmode()
        print "***"

class FiveCircleAdhocTestIncludingExternalScannables(AdhocTestIncludingExternalScannables):
    def setUp(self):
        dummyFiveCircleScannableGroup = ScannableGroup('fivecgrp', createDummyAxes(['alpha','delta','omega','chi','phi']))    
        self.fivec = DiffractometerScannableGroup('fivec', None, dummyFiveCircleScannableGroup)
        self.en = DummyPD('en')
        self.d = Diffcalc(fivec(), ScannableHardwareMonitorPlugin(self.fivec, self.en), True, True, UbCalculationNonPersister())
        self.d.raiseExceptionsForAllErrors = True
        self.fivec.setDiffcalcObject(self.d)
        self.hkl= Hkl('hkl', self.fivec, self.d)
        self.hklverbose = Hkl('hkl', self.fivec, self.d, ('theta','2theta','Bin','Bout','azimuth') )
    
    def pos_fivec(self, *args):
        if len(args):
            self.fivec.asynchronousMoveTo(args)
        else:
            return self.fivec.getPosition()

    def testSetGammaFails(self):
        self.assertRaises(DiffcalcException, self.d.setpar, 'gamma', 9999)

    def testWithAdhocScript(self):
            
        (pos_fivec, pos_en, pos_hkl, pos_hklverbose) = (self.pos_fivec, self.pos_en, self.pos_hkl, self.pos_hklverbose)
        (newub, setlat, addref, checkub, sigtau, hklmode, set) = self.getDCCommands()
        del pos_hklverbose
        newub('b16_270608')
        setlat('xtal', 3.8401, 3.8401, 5.43072)
        pos_en(12.39842/1.24)
        pos_fivec( 5.000, 22.790, 1.552, 22.400, 14.255)
        addref(1, 0, 1.0628)
        pos_fivec(5.000, 22.790, 4.575, 24.275, 101.320)
        addref(0, 1, 1.0628)
        checkub()
        
        hklmode(1)
        sigtau(0,0)
        set('alpha', 0)

        
        #1
        pos_hkl(.7,.9,1.3)
        resultDif = (0.0000,  27.3557,  13.6779,  37.7746,  53.9654)
        result = pos_fivec()
        self.assert_(self.areClose(resultDif, result))
        
        #2
        set('alpha',5)
        pos_hkl(.7,.9,1.3)
        resultDif = (5.0000, 26.9296, 8.4916, 27.2563, 59.5855)
        result = pos_fivec()
        self.assert_(self.areClose(resultDif, result))

        self.d.calcub()
        
        hklmode()
        print "**"
        hklmode(1)
        
        
class FourCircleAdhocTestIncludingExternalScannables(AdhocTestIncludingExternalScannables):
    def setUp(self):
        dummyFourCircleScannableGroup = ScannableGroup('fourcgrp', createDummyAxes(['delta','omega','chi','phi']))    
        self.fourc = DiffractometerScannableGroup('fourcc', None, dummyFourCircleScannableGroup)
        self.en = DummyPD('en')
        self.d = Diffcalc(fourc(), ScannableHardwareMonitorPlugin(self.fourc, self.en), True, True, UbCalculationNonPersister())
        self.d.raiseExceptionsForAllErrors = True
        self.fourc.setDiffcalcObject(self.d)
        self.hkl= Hkl('hkl', self.fourc, self.d)
        self.hklverbose = Hkl('hkl', self.fourc, self.d, ('theta','2theta','Bin','Bout','azimuth') )
    
    def pos_fourc(self, *args):
        if len(args):
            self.fourc.asynchronousMoveTo(args)
        else:
            return self.fourc.getPosition()

    def testSetGammaFails(self):
        self.assertRaises(DiffcalcException, self.d.setpar, 'gamma', 9999)

    def testWithAdhocScript(self):
            
        (pos_fourc, pos_en, pos_hkl, pos_hklverbose) = (self.pos_fourc, self.pos_en, self.pos_hkl, self.pos_hklverbose)
        (newub, setlat, addref, checkub, sigtau, hklmode, set) = self.getDCCommands()
        del pos_hklverbose
        newub('fromDiffcalcItself')   # This dataset generated by diffcalc code itself (not a proper test of code guts)
        setlat('xtal', 3.8401, 3.8401, 5.43072)
        pos_en(12.39842/1.24)
        pos_fourc( 22.790, 1.552, 22.400, 14.255)
        addref(1, 0, 1.0628)
        pos_fourc(22.790, 4.575, 24.275, 101.320)
        addref(0, 1, 1.0628)
        checkub()
        
        hklmode(1)
        sigtau(0,0)

        #1
        pos_hkl(.7,.9,1.3)
        resultDif = (27.3557325339904, 13.67786626699521, 23.481729970652825, 47.81491152277463)
        result = pos_fourc()
        self.assert_(self.areClose(resultDif, result))
        
        self.d.calcub()
        
        hklmode()
        print "**"
        hklmode(1)

class FourCircleWithcubic(AdhocTestIncludingExternalScannables):
    
    def setUp(self):
        dummyFourCircleScannableGroup = ScannableGroup('fourcgrp', createDummyAxes(['delta','omega','chi','phi']))    
        self.fourc = DiffractometerScannableGroup('fourcc', None, dummyFourCircleScannableGroup)
        self.en = DummyPD('en')
        self.d = Diffcalc(fourc(), ScannableHardwareMonitorPlugin(self.fourc, self.en), True, True, UbCalculationNonPersister())
        self.d.raiseExceptionsForAllErrors = True
        self.fourc.setDiffcalcObject(self.d)
        self.hkl= Hkl('hkl', self.fourc, self.d)
        self.hklverbose = Hkl('hkl', self.fourc, self.d, ('theta','2theta','Bin','Bout','azimuth') )
        self.orient()
        
    def pos_fourc(self, *args):
        if len(args):
            self.fourc.asynchronousMoveTo(args)
        else:
            return self.fourc.getPosition()

    def orient(self):
        (pos_fourc, pos_en, pos_hkl, pos_hklverbose) = (self.pos_fourc, self.pos_en, self.pos_hkl, self.pos_hklverbose)
        (newub, setlat, addref, checkub, sigtau, hklmode, set) = self.getDCCommands()
        del pos_hklverbose
        newub('cubic')   # This dataset generated by diffcalc code itself (not a proper test of code guts)
        setlat('cube', 1, 1, 1, 90, 90, 90)
        pos_en(12.39842)
        pos_fourc( 60, 30, 0, 0)
        addref(1, 0, 0)
        pos_fourc( 60, 30, 90, 0)
        addref(0, 0, 1)
        checkub()

    def testHkl100(self):
        (pos_fourc, pos_en, pos_hkl, pos_hklverbose) = (self.pos_fourc, self.pos_en, self.pos_hkl, self.pos_hklverbose)
        (newub, setlat, addref, checkub, sigtau, hklmode, set) = self.getDCCommands()
        hklmode(1)
        sigtau(0,0)
        #dif gives
        #h       k       l       alpha    delta    gamma    omega      chi      phi
        #1.000   0.000   0.000   0.0000  60.0000   0.0000 -60.0000   0.0000  90.0000
        #beta_in beta_out      rho      eta twotheta
        #-0.0000   0.0000   0.0000   0.0000  60.0000
        pos_hkl(1, 0, 0)
        self.assert_(self.areClose(pos_fourc(), (60, -60, 0, 90)),"%s!=\n%s"%(pos_fourc(), (60, 30, 0, 0))        )

    def testHkl001(self):
        (pos_fourc, pos_en, pos_hkl, pos_hklverbose) = (self.pos_fourc, self.pos_en, self.pos_hkl, self.pos_hklverbose)
        (newub, setlat, addref, checkub, sigtau, hklmode, set) = self.getDCCommands()
        hklmode(1)
        sigtau(0,0)
        #h       k       l        alpha    delta    gamma    omega      chi      phi
        #0.000   0.000   1.000   0.0000  60.0000   0.0000  30.0000  90.0000  45.0000
        #                          beta_in beta_out      rho      eta twotheta
        #                          30.0000  30.0000  60.0000   0.5236  60.0000
        pos_hkl(0, 0, 1)
        self.assert_(self.areClose(pos_fourc()[0:3], (60, 30, 90)), "%s!=\n%s (phi is undetermined here)"%(pos_fourc(), (60, 30, 90, 0)))        

    def testHkl110(self):
        (pos_fourc, pos_en, pos_hkl, pos_hklverbose) = (self.pos_fourc, self.pos_en, self.pos_hkl, self.pos_hklverbose)
        (newub, setlat, addref, checkub, sigtau, hklmode, set) = self.getDCCommands()
        hklmode(1)
        sigtau(0,0)
        #    h       k       l    alpha    delta    gamma    omega   chi      phi
        #1.000   1.000   0.000   0.0000  90.0000   0.0000 135.0000   0.0000 -45.0000
        #                          beta_in beta_out      rho      eta twotheta
        #                           0.0000  -0.0000  -0.0000   0.0000  90.0000
        pos_hkl(1, 1, 0)

class TestDiffractionCalculatorHklWithDataSess2Calc0(BaseTestDiffractionCalculatorHklWithData, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session2
        self.calc = scenarios.session2.calculations[0]


class TestDiffractionCalculatorHklWithDataSess3Calc0(BaseTestDiffractionCalculatorHklWithData, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session3
        self.calc = scenarios.session3.calculations[0]