# TODO: class largely copied from test_calcyou
from diffcalc.geometry.plugin import DiffractometerGeometryPlugin
from diffcalc.hkl.willmott.calcwill_horizontal import \
    WillmottHorizontalPosition, \
    WillmottHorizontalUbCalcStrategy, WillmottHorizontalCalculator, I, \
    WillmottHorizontalPosition as Pos
from diffcalc.tools import assert_array_almost_equal, \
    assert_second_dict_almost_in_first, matrixeq_
from diffcalc.ub.calculation import UBCalculation
from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.utils import DiffcalcException
from math import pi
from mock import Mock
from nose.plugins.skip import SkipTest
from nose.tools import raises
from tests.diffcalc.hardware.test_plugin import SimpleHardwareMonitorPlugin
from tests.diffcalc.hkl.vlieg.test_calcvlieg import createMockUbcalc, \
    createMockDiffractometerGeometry

try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

TORAD = pi / 180
TODEG = 180 / pi


class _BaseTest():

    def setup(self):
        self.mock_ubcalc = createMockUbcalc(None)
        self.mock_geometry = createMockDiffractometerGeometry()
        self.mock_hardware = SimpleHardwareMonitorPlugin(
                             ['delta', 'gamma', 'omegah', 'phi'])
        self.constraints = Mock()
        self.calc = WillmottHorizontalCalculator(self.mock_ubcalc,
                    self.mock_geometry, self.mock_hardware, self.constraints)

        self.places = 12

    def _check_hkl_to_angles(self, testname, zrot, yrot, hkl, pos_expected,
                             wavelength, virtual_expected={}):
        print ('_check_hkl_to_angles(%s, %.1f, %.1f, %s, %s, %.2f, %s)'
               % (testname, zrot, yrot, hkl, pos_expected, wavelength,
                  virtual_expected))
        self.zrot, self.yrot = zrot, yrot
        self._configure_ub()
        pos, virtual = self.calc.hklToAngles(hkl[0], hkl[1], hkl[2],
                                             wavelength)
        assert_array_almost_equal(pos.totuple(), pos_expected.totuple(),
                                  self.places)
        assert_second_dict_almost_in_first(virtual, virtual_expected)

    def _check_angles_to_hkl(self, testname, zrot, yrot, hkl_expected, pos,
                             wavelength, virtual_expected={}):
        print ('_check_angles_to_hkl(%s, %.1f, %.1f, %s, %s, %.2f, %s)' %
               (testname, zrot, yrot, hkl_expected, pos, wavelength,
                virtual_expected))
        self.zrot, self.yrot = zrot, yrot
        self._configure_ub()
        hkl, virtual = self.calc.anglesToHkl(pos, wavelength)
        assert_array_almost_equal(hkl, hkl_expected, self.places)
        assert_second_dict_almost_in_first(virtual, virtual_expected)

    @raises(DiffcalcException)
    def _check_hkl_to_angles_fails(self, *args):
        self._check_hkl_to_angles(*args)


class TestSurfaceNormalVerticalCubic(_BaseTest):

    def setup(self):
        _BaseTest.setup(self)
        self.constraints.reference = {'betain_eq_betaout': None}
        self.wavelength = 1
        self.UB = Matrix((I * (2 * pi)).tolist())

    def _configure_ub(self):
        self.mock_ubcalc.getUBMatrix.return_value = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        if pos is not None and False:
            self._check_angles_to_hkl('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails('', 999, 999, hkl, pos,
                                            self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)

    def testHkl001(self):
        self._check((0, 0, 1),
                    Pos(delta=60, gamma=0, omegah=30, phi=0),
                    {'betain': 30, 'betaout': 30})

    def testHkl011(self):
        raise SkipTest()
        # skipped because we can't calculate values to check against by hand
        self._check((0, 1, 1),
                    Pos(delta=90, gamma=0, omegah=90, phi=0),
                    {'betain': 45, 'betaout': 45})

    def testHkl010fails(self):
        self._check((0, 1, 0),
                    None,
                    {'betain': 30, 'betaout': 30}, fails=True)

    def testHkl100fails(self):
        self._check((1, 0, 0),
                    None,
                    {'betain': 30, 'betaout': 30}, fails=True)

    def testHkl111(self):
        raise SkipTest()
        # skipped because we can't calculate values to check against by hand
        self._check((1, 1, 1),
                    Pos(delta=90, gamma=0, omegah=90, phi=0),
                    {'betain': 45, 'betaout': 45})


# Primary and secondary reflections found with the help of DDIF on Diamond's
# i07 on Jan 27 2010

HKL0 = 2, 19, 32
REF0 = WillmottHorizontalPosition(delta=21.975, gamma=4.419, omegah=2,
                                  phi=326.2)

HKL1 = 0, 7, 22
REF1 = WillmottHorizontalPosition(delta=11.292, gamma=2.844, omegah=2,
                                  phi=124.1)
WAVELENGTH = 0.6358
ENERGY = 12.39842 / WAVELENGTH

# This is U matrix displayed by DDIF
U_FROM_DDIF = Matrix([[0.233140, 0.510833, 0.827463],
                      [-0.65596, -0.545557, 0.521617],
                      [0.717888, -0.664392, 0.207894]])

# This is the version that Diffcalc comes up with ( see following test)
U_DIFFCALC = Matrix([[-0.7178876, 0.6643924, -0.2078944],
                     [-0.6559596, -0.5455572, 0.5216170],
                     [0.2331402, 0.5108327, 0.8274634]])


class WillmottHorizontalGeometry(DiffractometerGeometryPlugin):

    def __init__(self):
        DiffractometerGeometryPlugin.__init__(self,
                    name='willmott_horizontal',
                    supportedModeGroupList=[],
                    fixedParameterDict={},
                    gammaLocation='base'
                    )

    def physicalAnglesToInternalPosition(self, physicalAngles):
        assert (len(physicalAngles) == 4), "Wrong length of input list"
        return WillmottHorizontalPosition(*physicalAngles)

    def internalPositionToPhysicalAngles(self, internalPosition):
        return internalPosition.totuple()


class TestUBCalculationWithWillmotStrategy_Si_5_5_12():

    def setUp(self):
        hardware = Mock()
        hardware.getPhysicalAngleNames.return_value = ('d', 'g', 'oh', 'p')
        self.ubcalc = UBCalculation(hardware, WillmottHorizontalGeometry(),
                                    UbCalculationNonPersister(),
                                    WillmottHorizontalUbCalcStrategy())

    def testAgainstResultsFromJan_27_2010(self):
        self.ubcalc.newCalculation('test')
        self.ubcalc.setLattice('Si_5_5_12', 7.68, 53.48, 75.63, 90, 90, 90)
        self.ubcalc.addReflection(HKL0[0], HKL0[1], HKL0[2], REF0, ENERGY,
                                  'ref0', None)
        self.ubcalc.addReflection(HKL1[0], HKL1[1], HKL1[2], REF1, ENERGY,
                                  'ref1', None)
        self.ubcalc.calculateUB()
        print "U: ", self.ubcalc.getUMatrix()
        print "UB: ", self.ubcalc.getUBMatrix()
        matrixeq_(self.ubcalc.getUMatrix(), U_DIFFCALC)


class TestSurfaceNormalVertical_Si_5_5_12(_BaseTest):

    def setup(self):
        _BaseTest.setup(self)
        self.constraints.reference = {'betain': 2 * TORAD}
        self.wavelength = 0.6358
        B = CrystalUnderTest('xtal', 7.68, 53.48,
                             75.63, 90, 90, 90).getBMatrix()
        self.UB = U_DIFFCALC.times(B)

    def _configure_ub(self):
        self.mock_ubcalc.getUBMatrix.return_value = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl('', 999, 999, hkl, pos, self.wavelength,
                                  virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails('', 999, 999, hkl, pos,
                                            self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)

    def testHkl_2_19_32_found_orientation_setting(self):
        '''Check that the or0 reflection maps back to the assumed hkl'''
        self.places = 2
        self._check_angles_to_hkl('', 999, 999, (2, 19, 32),
                        Pos(delta=21.975, gamma=4.419, omegah=2, phi=326.2),
                        self.wavelength, {'betain': 2})

    def testHkl_0_7_22_found_orientation_setting(self):
        '''Check that the or1 reflection maps back to the assumed hkl'''
        self.places = 0
        self._check_angles_to_hkl('', 999, 999, (0, 7, 22),
                        Pos(delta=11.292, gamma=2.844, omegah=2, phi=124.1),
                        self.wavelength, {'betain': 2})

    def testHkl_2_19_32_calculated_from_DDIF(self):
        self.places = 3
        self._check((2, 19, 32),
                    Pos(delta=21.974, gamma=4.419, omegah=2, phi=-33.803),
                    {'betain': 2})

    def testHkl_0_7_22_calculated_from_DDIF(self):
        self.places = 3
        self._check((0, 7, 22),
                    Pos(delta=11.242, gamma=3.038, omegah=2, phi=123.064),
                    {'betain': 2})

    def testHkl_2_m5_12(self):
        self.places = 3
        self._check((2, -5, 12),
                    Pos(delta=5.224, gamma=10.415, omegah=2, phi=-1.972),
                    {'betain': 2})

# conlcusion:
# given or1 from testHkl_2_19_32_found_orientation_setting and,
# or1 from testHkl_0_7_22_found_orientation_setting
# we can calculate a U matrix which agrees with that from diff except for
# signs and row order
# We can also calculate values for 2_19_32 and 0_7_22 that match those
# calculated by DDIF to the number of recorded decimal places (3)
