import unittest

from diffcalc.gdasupport import GdaDiffcalcObjectFactory as Factory
from diffcalc.gdasupport.scannable.base import ScannableGroup
from diffcalc.geometry import fourc
from diffcalc.geometry import fivec
from diffcalc.geometry import SixCircleGeometry
from diffcalc.geometry import SixCircleGammaOnArmGeometry
from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.hardware_adapter import ScannableHardwareAdapter
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc.gdasupport.scannable.parameter import \
    DiffractionCalculatorParameter
from mock import Mock
from diffcalc.hkl.vlieg.parameters import VliegParameterManager
from diffcalc.diffractioncalculator import Diffcalc
from diffcalc.hardware_adapter import HardwareAdapter
try:
    from gdascripts.pd.dummy_pds import DummyPD
except ImportError:
    print "WARNING: ExampleSixCircleStartup.py is not running within the GDA:"
    print "falling back to the (very minimal!) minigda..."
    from diffcalc.gdasupport.minigda.scannable import DummyPD


class MockDiffcalc(object):

    def __init__(self):

        self.parameter_manager = Mock(spec=VliegParameterManager)


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
        self.motorList = (self.alpha, self.delta, self.gamma,
                          self.omega, self.chi, self.phi)
        self.motorNames = 'alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'
        self.group = ScannableGroup('group', self.motorList)

    def testDetermineGeometryPlugin(self):
        geometry = SixCircleGeometry()
        determine_geometry = Factory.determineGeometryPlugin
        self.assertEquals(determine_geometry(geometry), geometry)
        self.assertEquals(determine_geometry('fourc').__class__, fourc)
        self.assertEquals(determine_geometry('fivec').__class__, fivec)
        self.assertEquals(determine_geometry('sixc').__class__,
                          SixCircleGeometry)
        self.assertEquals(determine_geometry('sixc_gamma_on_arm').__class__,
                          SixCircleGammaOnArmGeometry)
        self.assertRaises(KeyError, determine_geometry, 'Not a geometry name')
        self.assertRaises(TypeError, determine_geometry, None)
        self.assertRaises(TypeError, determine_geometry, 9999)

    def testDetermineDiffractometerScannableName(self):
        geometry = SixCircleGeometry()
        determine_name = Factory.determineDiffractometerScannableName
        self.assertEquals(determine_name('a_name', geometry), 'a_name')
        self.assertEquals(determine_name(None, geometry), 'sixc')
        self.assertRaises(TypeError, determine_name, 1234, None)

    def testCreateDiffractometerScannable_BadInput(self):
        c = Factory.createDiffractometerScannableAndPossiblyDummies
        self.assertRaises(
            ValueError, c, self.motorNames, self.motorList, None, 'ncircle')

    def testCreateDiffractometerScannable_FromGroup(self):
        c = Factory.createDiffractometerScannableAndPossiblyDummies
        objects, diffractometerScannable = c(None, None, self.group, 'ncircle')
        self.assert_(isinstance(diffractometerScannable,
                                DiffractometerScannableGroup))
        self.assertEquals(diffractometerScannable.getName(), 'ncircle')
        self.assertEquals(list(diffractometerScannable.getInputNames()),
                          list(self.motorNames))
        self.assertEquals(
            diffractometerScannable._DiffractometerScannableGroup__group,
            self.group)
        self.assertEquals(objects['ncircle'], diffractometerScannable)
        self.assertEquals(len(objects), 1)
        print objects

    def testCreateDiffractometerScannable_FromMotors(self):
        c = Factory.createDiffractometerScannableAndPossiblyDummies
        objects, diffractometerScannable = c(None, self.motorList, None,
                                             'ncircle')
        group = diffractometerScannable._DiffractometerScannableGroup__group
        try:
            motors = group._ScannableGroup__motors
        except AttributeError:
            motors = group.getGroupMembers()
        self.assert_(len(motors), 6)
        self.assertEquals(list(motors), list(self.motorList))
        self.assertEquals(diffractometerScannable.getName(), 'ncircle')
        self.assertEquals(list(diffractometerScannable.getInputNames()),
                          list(self.motorNames))
        self.assertEquals(objects['ncircle'], diffractometerScannable)
        self.assertEquals(len(objects), 1)
        print objects

    def testCreateDiffractometerScannable_FromDummies(self):
        c = Factory.createDiffractometerScannableAndPossiblyDummies
        objects, diffractometerScannable = c(self.motorNames, None, None,
                                             'ncircle')
        group = diffractometerScannable._DiffractometerScannableGroup__group
        try:
            motors = group._ScannableGroup__motors
        except AttributeError:
            motors = group.getGroupMembers()
        self.assert_(len(motors), 6)
        self.assertEquals(list(motors[0].getInputNames()), ['alpha'])
        self.assertEquals(list(objects['alpha'].getInputNames()), ['alpha'])
        self.assertEquals(list(objects['delta'].getInputNames()), ['delta'])
        self.assertEquals(list(objects['gamma'].getInputNames()), ['gamma'])
        self.assertEquals(list(objects['omega'].getInputNames()), ['omega'])
        self.assertEquals(list(objects['chi'].getInputNames()), ['chi'])
        self.assertEquals(list(objects['phi'].getInputNames()), ['phi'])
        self.assertEquals(objects['ncircle'].getName(), 'ncircle')
        self.assertEquals(list(objects['ncircle'].getInputNames()),
                          list(self.motorNames))
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
        self.assertEquals(energyScannable.getPosition(), 12.39842)
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
        c(ScannableHardwareAdapter)  # no exceptions expected
        self.assertRaises(TypeError, c, 2)
        self.assertRaises(ValueError, c, str)

    def testBuildHklScannableAndComponents(self):
        dc = Mock(spec=Diffcalc)
        ds = MockDiffractometerScannable()
        self.assertRaises(
            TypeError, Factory.buildHklScannableAndComponents, ds, dc, ())
        objects = Factory.buildHklScannableAndComponents('myhkl', ds, dc, ())
        self.assertEquals(len(objects), 4)
        hkl = objects['myhkl']
        self.assert_(isinstance(hkl, Hkl))
        self.assertEquals(hkl.getName(), 'myhkl')
        self.assertEquals(list(hkl.getInputNames()), ['h', 'k', 'l'])
        self.assertEquals(list(hkl.getExtraNames()), [])
        self.assertEquals(objects['h'], hkl.h)
        self.assertEquals(objects['k'], hkl.k)
        self.assertEquals(objects['l'], hkl.l)

    def testBuildHklVerboseScannable(self):
        dc = Mock(spec=Diffcalc)
        ds = MockDiffractometerScannable()
        self.assertRaises(
            TypeError, Factory.buildHklverboseScannable, ds, dc, ())
        objects = Factory.buildHklverboseScannable('myhkl', ds, dc, ('a', 'b'))
        self.assertEquals(len(objects), 1)
        hkl = objects['myhkl']
        self.assert_(isinstance(hkl, Hkl))
        self.assertEquals(hkl.getName(), 'myhkl')
        self.assertEquals(list(hkl.getInputNames()), ['h', 'k', 'l'])
        self.assertEquals(list(hkl.getExtraNames()), ['a', 'b'])

    def testCreateParameterScannables(self):
        dc = MockDiffcalc()
        dc._hardware = Mock(spec=HardwareAdapter)
        dc._hardware.getPhysicalAngleNames.return_value = 'alpha',
        dc.parameter_manager = Mock(spec=VliegParameterManager)
        #dc.parameter_manager.get
        dc.parameter_manager.getParameterDict.return_value = {
            'alpha': None, 'betain': None, 'oopgamma': None}
        objects = Factory.createParameterScannables(dc)
        self.assertEquals(len(objects), 3)
        self.assert_(isinstance(objects['alpha_par'],
                                DiffractionCalculatorParameter))
        self.assert_(isinstance(objects['betain'],
                                DiffractionCalculatorParameter))
        self.assert_(isinstance(objects['oopgamma'],
                                DiffractionCalculatorParameter))

    def testCreateAndAliasCommands(self):
        alias = MockAlias()
        Factory.alias = alias

        def f():
            pass

        def g():
            pass

        objects = Factory.expose_and_alias_commands([f, g])
        self.assertEquals(len(objects), 2)

        self.assertEquals(objects['f'], f)
        self.assertEquals(objects['g'], g)
        self.assertEquals(alias.aliased, ['f', 'g'])

    def testCreateDiffcalcObjects(self):
        virtual_names = '2theta', 'Bin', 'Bout', 'azimuth'
        objects = Factory.createDiffcalcObjects(
            dummyAxisNames=self.motorNames,
            dummyEnergyName='en',
            geometryPlugin='sixc',  # Class or name (avoids needing to set path
                                    # before script is run)
            hklverboseVirtualAnglesToReport=virtual_names)
        print objects.keys()

        def assertHas(a, b):
            for aa in a:
                if aa not in b:
                    raise Exception("%s not in %s." % (aa, b))

        expected = ('en', 'wl', 'sixc', 'hkl', 'h', 'k', 'l', 'hklverbose',
                    'sixc', 'diffcalc_object')
        assertHas(self.motorNames + expected, objects.keys())
