from diffcalc.gdasupport import GdaDiffcalcObjectFactory as Factory
from diffcalc.gdasupport.scannable.base import ScannableGroup
from diffcalc.geometry.fourc import fourc
from diffcalc.geometry.fivec import fivec
from diffcalc.geometry.sixc import SixCircleGeometry
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup
from diffcalc.hardware.scannable import ScannableHardwareMonitorPlugin
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc.gdasupport.scannable.parameter import DiffractionCalculatorParameter
try:
    from gdascripts.pd.dummy_pds import DummyPD
except ImportError:
    print "WARNING: ExampleSixCircleStartup.py is not running within the GDA: falling back to the (very minimal!) minigda..."
    from diffcalc.gdasupport.minigda.scannable.dummy import DummyPD

import unittest

class MockDiffcalc(object):
        
    def _getParameterNames(self):
        return self.paramNames
    
    def _getAxisNames(self):
        return self.axisNames

    def command1(self):
        pass
    
    def command2(self):
        pass

class MockDiffractometerScannable(object):
    pass

class MockAlias(object):
    
    def __init__(self):
        self.aliased = []
    def __call__(self, name):
        self.aliased.append(name)

class Test(unittest.TestCase):
    
    def setUp(self):
        self.en = DummyPD('en')
        self.alpha = DummyPD('alpha')
        self.delta = DummyPD('delta')
        self.gamma = DummyPD('gamma')
        self.omega = DummyPD('omega')
        self.chi = DummyPD('chi')
        self.phi = DummyPD('phi')
        self.motorList = self.alpha, self.delta, self.gamma, self.omega, self.chi, self.phi
        self.motorNames = 'alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'
        self.group = ScannableGroup('group', self.motorList)

    def testDetermineGeometryPlugin(self):
        geometry = SixCircleGeometry()
        self.assertEquals(Factory.determineGeometryPlugin(geometry), geometry)
        self.assertEquals(Factory.determineGeometryPlugin('fourc').__class__, fourc)
        self.assertEquals(Factory.determineGeometryPlugin('fivec').__class__, fivec)
        self.assertEquals(Factory.determineGeometryPlugin('sixc').__class__, SixCircleGeometry)
        self.assertEquals(Factory.determineGeometryPlugin('sixc_gamma_on_arm').__class__, SixCircleGammaOnArmGeometry )
        self.assertRaises(KeyError, Factory.determineGeometryPlugin, 'Not a geometry name')
        self.assertRaises(TypeError, Factory.determineGeometryPlugin, None)
        self.assertRaises(TypeError, Factory.determineGeometryPlugin, 9999)

    def testDetermineDiffractometerScannableName(self):
        geometry = SixCircleGeometry()
        self.assertEquals(Factory.determineDiffractometerScannableName('a_name', geometry), 'a_name')
        self.assertEquals(Factory.determineDiffractometerScannableName(None, geometry), 'sixc')
        self.assertRaises(TypeError, Factory.determineDiffractometerScannableName, 1234, None)

    def testCreateDiffractometerScannable_BadInput(self):
        c = Factory.createDiffractometerScannableAndPossiblyDummies
        self.assertRaises(ValueError, c, self.motorNames, self.motorList, None, 'ncircle')

    def testCreateDiffractometerScannable_FromGroup(self):
        c = Factory.createDiffractometerScannableAndPossiblyDummies
        objects, diffractometerScannable = c(None, None, self.group, 'ncircle')
        self.assert_(isinstance(diffractometerScannable, DiffractometerScannableGroup))
        self.assertEquals(diffractometerScannable.getName(), 'ncircle')
        self.assertEquals(list(diffractometerScannable.getInputNames()), list(self.motorNames))
        self.assertEquals(diffractometerScannable._DiffractometerScannableGroup__group, self.group)
        self.assertEquals(objects['ncircle'], diffractometerScannable)
        self.assertEquals(len(objects), 1)
        print objects
    
    def testCreateDiffractometerScannable_FromMotors(self):
        c = Factory.createDiffractometerScannableAndPossiblyDummies
        objects, diffractometerScannable = c(None, self.motorList, None, 'ncircle')
        group = diffractometerScannable._DiffractometerScannableGroup__group
        self.assertEquals(group._ScannableGroup__motors, self.motorList)
        self.assertEquals(diffractometerScannable.getName(), 'ncircle')
        self.assertEquals(list(diffractometerScannable.getInputNames()), list(self.motorNames))
        self.assertEquals(objects['ncircle'], diffractometerScannable)
        self.assertEquals(len(objects), 1)
        print objects

    def testCreateDiffractometerScannable_FromDummies(self):
        c = Factory.createDiffractometerScannableAndPossiblyDummies
        objects, diffractometerScannable = c(self.motorNames, None, None, 'ncircle')
        group = diffractometerScannable._DiffractometerScannableGroup__group
        motors = group._ScannableGroup__motors
        self.assert_(len(motors), 6)
        self.assertEquals(list(motors[0].getInputNames()), ['alpha'])
        self.assertEquals(list(objects['alpha'].getInputNames()), ['alpha'])
        self.assertEquals(list(objects['delta'].getInputNames()), ['delta'])
        self.assertEquals(list(objects['gamma'].getInputNames()), ['gamma'])
        self.assertEquals(list(objects['omega'].getInputNames()), ['omega'])
        self.assertEquals(list(objects['chi'].getInputNames()), ['chi'])
        self.assertEquals(list(objects['phi'].getInputNames()), ['phi'])
        self.assertEquals(objects['ncircle'].getName(), 'ncircle')
        self.assertEquals(list(objects['ncircle'].getInputNames()), list(self.motorNames))
        self.assertEquals(len(objects), 7)

    def testBuildWavelengthAndPossiblyEnergyScannable_BadInput(self):
        b = Factory.buildWavelengthAndPossiblyEnergyScannable
        self.assertRaises(ValueError, b, 'en_to_make', b, 1)
        
    def testBuildWavelengthAndPossiblyEnergyScannable_FromReal(self):
        b = Factory.buildWavelengthAndPossiblyEnergyScannable
        self.en.asynchronousMoveTo(10)
        objects, energyScannable = b(None, self.en, 1)
        self.assertEquals(energyScannable, self.en)
        self.assertEquals(len(objects), 1)
        wl = objects['wl']
        self.assertEquals(wl.getName(), 'wl')
        self.assertEquals(list(wl.getInputNames()), ['wl'])
        self.assertEquals(wl.getPosition(), 1.2398419999999999)

    def testBuildWavelengthAndPossiblyEnergyScannable_FromDummy(self):
        b = Factory.buildWavelengthAndPossiblyEnergyScannable
        objects, energyScannable = b('dummy_en', None, 1)
        self.assertEquals(energyScannable.getName(), 'dummy_en')
        self.assertEquals(list(energyScannable.getInputNames()), ['dummy_en'])
        self.assertEquals(energyScannable.getPosition(), 12.39842)#
        self.assertEquals(len(objects), 2)
        self.assertEquals(objects['dummy_en'], energyScannable)
        wl = objects['wl']
        self.assertEquals(wl.getName(), 'wl')
        self.assertEquals(list(wl.getInputNames()), ['wl'])
        self.assertEquals(wl.getPosition(), 1)
        energyScannable.asynchronousMoveTo(10)
        self.assertEquals(wl.getPosition(), 1.2398419999999999)

    def testCheckHardwarePluginClass(self):
        c = Factory.checkHardwarePluginClass
        c(ScannableHardwareMonitorPlugin) # no exceptions expected
        self.assertRaises(TypeError, c, 2)
        self.assertRaises(ValueError, c, str)
        
    def testBuildHklScannableAndComponents(self):
        dc = MockDiffcalc()
        ds = MockDiffractometerScannable()
        self.assertRaises(TypeError, Factory.buildHklScannableAndComponents, ds, dc, () )
        objects = Factory.buildHklScannableAndComponents('myhkl', ds, dc, ())
        self.assertEquals(len(objects), 4)
        hkl = objects['myhkl']
        self.assert_(isinstance(hkl, Hkl))
        self.assertEquals(hkl.getName(), 'myhkl')
        self.assertEquals(list(hkl.getInputNames()), ['h', 'k', 'l'] )
        self.assertEquals(list(hkl.getExtraNames()), [] )
        self.assertEquals(objects['h'], hkl.h)
        self.assertEquals(objects['k'], hkl.k)
        self.assertEquals(objects['l'], hkl.l)

    def testBuildHklVerboseScannable(self):
        dc = MockDiffcalc()
        ds = MockDiffractometerScannable()
        self.assertRaises(TypeError, Factory.buildHklverboseScannable, ds, dc, () )
        objects = Factory.buildHklverboseScannable('myhkl', ds, dc, ('a','b'))
        self.assertEquals(len(objects), 1)
        hkl = objects['myhkl']
        self.assert_(isinstance(hkl, Hkl))
        self.assertEquals(hkl.getName(), 'myhkl')
        self.assertEquals(list(hkl.getInputNames()), ['h', 'k', 'l'] )
        self.assertEquals(list(hkl.getExtraNames()), ['a','b'] )

    def testCreateParameterScannables(self):
        dc = MockDiffcalc()
        dc.paramNames = 'alpha', 'betain', 'oopgamma'
        dc.axisNames = 'alpha',
        objects = Factory.createParameterScannables(dc)
        self.assertEquals(len(objects), 3)
        self.assert_(isinstance(objects['alpha_par'], DiffractionCalculatorParameter))
        self.assert_(isinstance(objects['betain'], DiffractionCalculatorParameter))
        self.assert_(isinstance(objects['oopgamma'], DiffractionCalculatorParameter))

    def testCreateAndAliasCommands(self):
        dc = MockDiffcalc()
        alias = MockAlias()
        Factory.alias = alias
        objects = Factory.createAndAliasCommands(dc)
        self.assertEquals(len(objects), 2)
        self.assertEquals(objects['command1'], dc.command1)
        self.assertEquals(objects['command2'], dc.command2)
        self.assertEquals(alias.aliased, ['command1','command2'])

    def testCreateDiffcalcObjects(self):
        objects = Factory.createDiffcalcObjects(
                        dummyAxisNames = self.motorNames,
                        dummyEnergyName = 'en',
                        geometryPlugin = 'sixc', # Class or name (avoids needing to set path before script is run)
                        hklverboseVirtualAnglesToReport = ('2theta','Bin','Bout','azimuth')
                        )
        print objects.keys()
        def assertHas(a,b):
            for aa in a:
                if aa not in b:
                    raise Exception, "%s not in %s." % (aa, b)

        assertHas( self.motorNames + ('en', 'wl', 'sixc', 'hkl', 'h', 'k', 'l', 'hklverbose', 'sixc', 'helphkl', 'helpub', 'diffcalc_object' ), objects.keys() )
