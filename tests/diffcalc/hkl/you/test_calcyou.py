from math import pi, cos, sin
from nose.tools import raises

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.hkl.you.calcyou import YouHklCalculator
from diffcalc.hkl.you.constraints import ConstraintManager
from diffcalc.tools import assert_array_almost_equal, \
    assert_second_dict_almost_in_first
from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.utils import y_rotation, z_rotation, DiffcalcException
from tests.diffcalc.test_hardware_adapter import SimpleHardwareAdapter
from tests.diffcalc.hkl.vlieg.test_calcvlieg import \
    createMockDiffractometerGeometry, createMockUbcalc
from diffcalc.hkl.you.position import YouPosition as Pos, YouPosition as P


TORAD = pi / 180
TODEG = 180 / pi
I = matrix('1 0 0; 0 1 0; 0 0 1')


class Pair:

    def __init__(self, name, hkl, position, fails=False):
        self.name = name
        self.hkl = hkl
        self.position = position
        self.fails = fails


class _BaseTest():

    def setup(self):
        self.mock_ubcalc = createMockUbcalc(None)
        self.mock_geometry = createMockDiffractometerGeometry()
        names = ['delta', 'nu', 'mu', 'eta', 'chi', 'phi']
        self.mock_hardware = SimpleHardwareAdapter(names)
        self.constraints = ConstraintManager(self.mock_hardware)
        self.calc = YouHklCalculator(self.mock_ubcalc, self.mock_geometry,
                                     self.mock_hardware, self.constraints)

        self.mock_hardware.setLowerLimit('delta', 0)
        self.mock_hardware.setUpperLimit('delta', 179.999)
        self.mock_hardware.setLowerLimit('mu', 0)
        self.mock_hardware.setLowerLimit('eta', 0)
        self.mock_hardware.setLowerLimit('chi', -10)

        self.places = 11

    def _configure_ub(self):
        ZROT = z_rotation(self.zrot * TORAD)  # -PHI
        YROT = y_rotation(self.yrot * TORAD)  # +CHI
        U = ZROT * YROT
        UB = U * self.B
        self.mock_ubcalc.getUBMatrix.return_value = UB

    def _check_hkl_to_angles(self, testname, zrot, yrot, hkl, pos_expected,
                             wavelength, virtual_expected={}):
        print ('_check_hkl_to_angles(%s, %.1f, %.1f, %s, %s, %.2f, %s)' %
               (testname, zrot, yrot, hkl, pos_expected, wavelength,
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

    def case_generator(self):
        for case in self.cases:
            yield (self._check_angles_to_hkl, case.name, self.zrot, self.yrot,
                   case.hkl, case.position, self.wavelength, {})
            test_method = (self._check_hkl_to_angles_fails if case.fails else
                           self._check_hkl_to_angles)
            yield (test_method, case.name, self.zrot, self.yrot, case.hkl,
                                case.position, self.wavelength, {})


class _TestCubic(_BaseTest):

    def setup(self):
        _BaseTest.setup(self)
        self.B = I * 2 * pi


class _TestCubicVertical(_TestCubic):

    def setup(self):
        _TestCubic.setup(self)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('100', (1, 0, 0),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=0 - self.yrot,
                     phi=0 + self.zrot)),
            Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=4 - self.yrot,
                     phi=0 + self.zrot),),
            Pair('010', (0, 1, 0),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=90 + self.zrot)),
            Pair('001', (0, 0, 1),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=90 - self.yrot,
                     phi=0 + self.zrot)),
            Pair('001-->100', (cos(86 * TORAD), 0, sin(86 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=86 - self.yrot,
                     phi=0 + self.zrot)),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        self.case_dict['001'].fails = True  # q||n
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_pairs_various_zrot_and_yrot0(self):
        for zrot in [0, 2, -2, 45, -45, 90, -90]:  # -180, 180 work if recut
            self.makes_cases(zrot, 0)
            self.case_dict['001'].fails = True  # q||n
            for case_tuple in self.case_generator():
                yield case_tuple

    def test_hkl_to_angles_zrot1_yrot2(self):
        self.makes_cases(1, 2)
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_hkl_to_angles_zrot1_yrotm2(self):
        self.makes_cases(1, -2)
        for case_tuple in self.case_generator():
            yield case_tuple


class TestCubicVertical_aeqb(_TestCubicVertical):

    def setup(self):
        _TestCubicVertical.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu': 0, 'nu': 0}


class TestCubicVertical_psi_90(_TestCubicVertical):
    '''mode psi=90 should be the same as mode a_eq_b'''

    def setup(self):
        _TestCubicVertical.setup(self)
        self.constraints._constrained = {'psi': 90 * TORAD, 'mu': 0, 'nu': 0}


class TestCubicVertical_qaz_90(_TestCubicVertical):
    '''mode psi=90 should be the same as mode a_eq_b'''

    def setup(self):
        _TestCubicVertical.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu': 0,
                                         'qaz': 90 * TORAD}


class SkipTestYouHklCalculatorWithCubicMode_aeqb_delta_60(_TestCubicVertical):
    '''
    Works to 4-5 decimal places but chooses different solutions when phi||eta .
    Skip all tests.
    '''

    def setup(self):
        _TestCubicVertical.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu': 0,
                                         'delta': 60 * TORAD}
        self.places = 5


class _TestCubicHorizontal(_TestCubic):

    def setup(self):
        _TestCubic.setup(self)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
             Pair('100', (1, 0, 0),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=90 + self.yrot,
                      phi=-180 + self.zrot)),
             Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=90 - 4 + self.yrot,
                      phi=-180 + self.zrot)),
             Pair('010', (0, 1, 0),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=90,
                      phi=-90 + self.zrot)),  # no yrot as chi||q
             Pair('001', (0, 0, 1),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=0 - self.yrot,
                      phi=0 + self.zrot)),
             Pair('001-->100', (cos(86 * TORAD), 0, sin(86 * TORAD)),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=0 - 4 - self.yrot,
                      phi=0 + self.zrot)),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        self.case_dict['001'].fails = True  # q||n
        self.case_dict['100'].position.phi = 180  # not -180
        self.case_dict['100-->001'].position.phi = 180  # not -180
        for case_tuple in self.case_generator():
            yield case_tuple

#    def test_pairs_various_zrot_and_yrot0(self):
#        for zrot in [0, 2, -2, 45, -45, 90, -90]:
# -180, 180 work but with cut problem
#            self.makes_cases(zrot, 0)
#            self.case_dict['001'].fails = True # q||n
#            for case_tuple in self.case_generator():
#                yield case_tuple

    def test_hkl_to_angles_zrot1_yrot2(self):
        self.makes_cases(1, 2)
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_hkl_to_angles_zrot1_yrotm2(self):
        self.makes_cases(1, -2)
        for case_tuple in self.case_generator():
            yield case_tuple


class TestCubicHorizontal_qaz0_aeqb(_TestCubicHorizontal):

    def setup(self):
        _TestCubicHorizontal.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'qaz': 0, 'eta': 0}


class TestCubicHorizontal_delta0_aeqb(_TestCubicHorizontal):

    def setup(self):
        _TestCubicHorizontal.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'delta': 0, 'eta': 0}


class TestAgainstSpecSixcB16_270608(_BaseTest):
    '''NOTE: copied from tests.diffcalc.scenarios.session3'''
    def setup(self):
        _BaseTest.setup(self)

        U = matrix(((0.997161, -0.062217, 0.042420),
                    (0.062542, 0.998022, -0.006371),
                    (-0.041940, 0.009006, 0.999080)))

        B = matrix(((1.636204, 0, 0),
                    (0, 1.636204, 0),
                    (0, 0, 1.156971)))

        self.UB = U * B
        self.constraints._constrained = {'a_eq_b': None, 'mu': 0, 'nu': 0}
        self.places = 2  # TODO: the Vlieg code got this to 3 decimal places

    def _configure_ub(self):
        self.mock_ubcalc.getUBMatrix.return_value = self.UB

    def makes_cases(self, zrot, yrot):
        del zrot, yrot  # not used
        self.wavelength = 1.24
        self.cases = (
            Pair('7_9_13', (0.7, 0.9, 1.3),
                 Pos(mu=0, delta=27.352179, nu=0, eta=13.676090,
                     chi=37.774500, phi=53.965500)),
            Pair('100', (1, 0, 0),
                 Pos(mu=0, delta=18.580230, nu=0, eta=9.290115,
                     chi=-2.403500, phi=3.589000)),
            Pair('010', (0, 1, 0),
                 Pos(mu=0, delta=18.580230, nu=0, eta=9.290115,
                     chi=0.516000, phi=93.567000)),
            Pair('110', (1, 1, 0),
                 Pos(mu=0, delta=26.394192, nu=0, eta=13.197096,
                     chi=-1.334500, phi=48.602000)),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def case_generator(self):
        zrot, yrot = 999, 999
        for case in self.cases:
            yield (self._check_angles_to_hkl, case.name, zrot, yrot, case.hkl,
                   case.position, self.wavelength, {})
            test_method = (self._check_hkl_to_angles_fails if case.fails else
                           self._check_hkl_to_angles)
            yield (test_method, case.name, zrot, yrot, case.hkl, case.position,
                   self.wavelength, {})

    def test_hkl_to_angles_given_UB(self):
        self.makes_cases(None, None)  # xrot, yrot unused
        for case_tuple in self.case_generator():
            yield case_tuple


class SkipTestThreeTwoCircleForDiamondI06andI10(_BaseTest):
    """
    This is a three circle diffractometer with only delta and omega axes
    and a chi axis with limited range around 90. It is operated with phi
    fixed and can only reach reflections with l (or z) component.

    The data here is taken from an experiment performed on Diamonds I06
    beamline.
    """

    def setup(self):
        _BaseTest.setup(self)
        self.constraints._constrained = {'phi': -pi / 2, 'nu': 0, 'mu': 0}
        self.wavelength = 12.39842 / 1.650

    def _configure_ub(self):
        U = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        B = CrystalUnderTest('xtal', 5.34, 5.34, 13.2, 90, 90, 90).getBMatrix()
        self.mock_ubcalc.getUBMatrix.return_value = U * B

    def testHkl001(self):
        hkl = (0, 0, 1)
        pos = Pos(mu=0, delta=33.07329403295449, nu=0, eta=16.536647016477247,
                  chi=90, phi=-90)
        self._check_angles_to_hkl(
            '001', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '001', 999, 999, hkl, pos, self.wavelength, {})

    def testHkl100(self):
        hkl = (1, 0, 0)
        pos = Pos(mu=0, delta=89.42926563609406, nu=0, eta=134.71463281804702,
                  chi=90, phi=-90)
        self._check_angles_to_hkl(
            '100', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '100', 999, 999, hkl, pos, self.wavelength, {})

    def testHkl101(self):
        hkl = (1, 0, 1)
        pos = Pos(mu=0, delta=98.74666191021282, nu=0, eta=117.347760720783,
                  chi=90, phi=-90)
        self._check_angles_to_hkl(
            '101', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '101', 999, 999, hkl, pos, self.wavelength, {})


class TestFixedChiPhiPsiMode_DiamondI07SurfaceNormalHorizontal(_TestCubic):
    """
    The data here is taken from an experiment performed on Diamonds I07
    beamline, obtained using Vlieg's DIF software"""

    def setup(self):
        _TestCubic.setup(self)
        self.mock_hardware.setLowerLimit('nu', 0)
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'a_eq_b': None}
        self.wavelength = 1
        self.UB = I * 2 * pi
        self.places = 4

    def _configure_ub(self):
        self.mock_ubcalc.getUBMatrix.return_value = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl(
            '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def testHkl001(self):
        self._check((0, 0, 1),  # betaout=30
                    P(mu=30, delta=0, nu=60, eta=90, chi=0, phi=0), fails=True)

    def testHkl010(self):
        self._check((0, 1, 0),  # betaout=0
                    P(mu=0, delta=60, nu=0, eta=120, chi=0, phi=0))

    def testHkl011(self):
        self._check((0, 1, 1),  # betaout=30
                    P(mu=30, delta=54.7356, nu=90, eta=125.2644, chi=0, phi=0))

    def testHkl100(self):
        self._check((1, 0, 0),  # betaout=0
                    P(mu=0, delta=60, nu=0, eta=30, chi=0, phi=0))

    def testHkl101(self):
        self._check((1, 0, 1),  # betaout=30
                    P(mu=30, delta=54.7356, nu=90, eta=35.2644, chi=0, phi=0))

    def testHkl110(self):
        self._check((1, 1, 0),  # betaout=0
                    P(mu=0, delta=90, nu=0, eta=90, chi=0, phi=0))

    def testHkl11nearly0(self):
        self.places = 3
        self._check((1, 1, .0001),  # betaout=0
                    P(mu=0.0029, delta=89.9971, nu=90.0058, eta=90, chi=0,
                      phi=0))

    def testHkl111(self):
        self._check((1, 1, 1),  # betaout=30
                    P(mu=30, delta=54.7356, nu=150, eta=99.7356, chi=0, phi=0))

    def testHklover100(self):
        self._check((1.1, 0, 0),  # betaout=0
                    P(mu=0, delta=66.7340, nu=0, eta=33.3670, chi=0, phi=0))

    def testHklunder100(self):
        self._check((.9, 0, 0),  # betaout=0
                    P(mu=0, delta=53.4874, nu=0, eta=26.7437, chi=0, phi=0))

    def testHkl788(self):
        self._check((.7, .8, .8),  # betaout=23.5782
                    P(mu=23.5782, delta=59.9980, nu=76.7037, eta=84.2591,
                      chi=0, phi=0))

    def testHkl789(self):
        self._check((.7, .8, .9),  # betaout=26.7437
                    P(mu=26.74368, delta=58.6754, nu=86.6919, eta=85.3391,
                      chi=0, phi=0))

    def testHkl7810(self):
        self._check((.7, .8, 1),  # betaout=30
                    P(mu=30, delta=57.0626, nu=96.86590, eta=86.6739, chi=0,
                      phi=0))


class SkipTestFixedChiPhiPsiModeSurfaceNormalVertical(_TestCubic):

    def setup(self):
        _TestCubic.setup(self)
        self.mock_hardware.setLowerLimit('nu', 0)
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0,
                                         'a_eq_b': None}
        self.wavelength = 1
        self.UB = I * 2 * pi
        self.places = 4

        self.mock_hardware.setLowerLimit('mu', None)
        self.mock_hardware.setLowerLimit('eta', None)
        self.mock_hardware.setLowerLimit('chi', None)

    def _configure_ub(self):
        self.mock_ubcalc.getUBMatrix.return_value = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl(
            '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def testHkl001(self):
        self._check((0, 0, 1),  # betaout=30
                    P(mu=30, delta=0, nu=60, eta=90, chi=0, phi=0), fails=True)

    def testHkl010(self):
        self._check((0, 1, 0),  # betaout=0
                    P(mu=120, delta=0, nu=60, eta=0, chi=90, phi=0))

    def testHkl011(self):
        self._check((0, 1, 1),  # betaout=30
                    P(mu=30, delta=54.7356, nu=90, eta=125.2644, chi=0, phi=0))

    def testHkl100(self):
        self._check((1, 0, 0),  # betaout=0
                    P(mu=0, delta=60, nu=0, eta=30, chi=0, phi=0))

    def testHkl101(self):
        self._check((1, 0, 1),  # betaout=30
                    P(mu=30, delta=54.7356, nu=90, eta=35.2644, chi=0, phi=0))

    def testHkl110(self):
        self._check((1, 1, 0),  # betaout=0
                    P(mu=0, delta=90, nu=0, eta=90, chi=0, phi=0))

    def testHkl11nearly0(self):
        self.places = 3
        self._check((1, 1, .0001),  # betaout=0
                    P(mu=0.0029, delta=89.9971, nu=90.0058, eta=90, chi=0,
                      phi=0))

    def testHkl111(self):
        self._check((1, 1, 1),  # betaout=30
                    P(mu=30, delta=54.7356, nu=150, eta=99.7356, chi=0, phi=0))

    def testHklover100(self):
        self._check((1.1, 0, 0),  # betaout=0
                    P(mu=0, delta=66.7340, nu=0, eta=33.3670, chi=0, phi=0))

    def testHklunder100(self):
        self._check((.9, 0, 0),  # betaout=0
                    P(mu=0, delta=53.4874, nu=0, eta=26.7437, chi=0, phi=0))

    def testHkl788(self):
        self._check((.7, .8, .8),  # betaout=23.5782
                    P(mu=23.5782, delta=59.9980, nu=76.7037, eta=84.2591,
                      chi=0, phi=0))

    def testHkl789(self):
        self._check((.7, .8, .9),  # betaout=26.7437
                    P(mu=26.74368, delta=58.6754, nu=86.6919, eta=85.3391,
                      chi=0, phi=0))

    def testHkl7810(self):
        self._check((.7, .8, 1),  # betaout=30
                    P(mu=30, delta=57.0626, nu=96.86590, eta=86.6739, chi=0,
                      phi=0))
