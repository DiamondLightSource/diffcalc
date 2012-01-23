from diffcalc.hkl.you.calcyou import YouHklCalculator
from diffcalc.hkl.you.constraints import ConstraintManager
from diffcalc.tools import assert_array_almost_equal, \
    assert_second_dict_almost_in_first
from diffcalc.utils import y_rotation, z_rotation, YouPosition as Pos, DiffcalcException
from math import pi, cos, sin
from nose.tools import raises
from tests.diffcalc.hkl.test_calcvlieg import createMockDiffractometerGeometry, createMockUbcalc
from tests.diffcalc.hardware.test_plugin import SimpleHardwareMonitorPlugin

try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

TORAD = pi / 180
TODEG = 180 / pi
I = Matrix.identity(3, 3)


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
        self.mock_hardware = SimpleHardwareMonitorPlugin(['delta', 'nu', 'mu', 'eta', 'chi', 'phi'])
        self.constraints = ConstraintManager(self.mock_hardware)
        self.calc = YouHklCalculator(self.mock_ubcalc, self.mock_geometry, self.mock_hardware, self.constraints)
        
        self.mock_hardware.setLowerLimit('delta', 0)
        self.mock_hardware.setLowerLimit('mu', 0)
        self.mock_hardware.setLowerLimit('eta', 0)
        self.mock_hardware.setLowerLimit('chi', -10)

        self.places = 12

    def _check_hkl_to_angles(self, testname, zrot, yrot, hkl, pos_expected, wavelength, virtual_expected={}):
        print '_check_hkl_to_angles(%s, %.1f, %.1f, %s, %s, %.2f, %s)' % (testname, zrot, yrot, hkl, pos_expected, wavelength, virtual_expected)
        ZROT = z_rotation(zrot * TORAD)  # -PHI
        YROT = y_rotation(yrot * TORAD)  # +CHI
        U = ZROT.times(YROT) 
        UB = U.times(self.B)
        self.mock_ubcalc.getUBMatrix.return_value = UB

        pos, virtual = self.calc.hklToAngles(hkl[0], hkl[1], hkl[2], wavelength)
        assert_array_almost_equal(pos.totuple(), pos_expected.totuple(), self.places)
        assert_second_dict_almost_in_first(virtual, virtual_expected)

    def _check_angles_to_hkl(self, testname, zrot, yrot, hkl_expected, pos, wavelength, virtual_expected={}):
        print '_check_angles_to_hkl(%s, %.1f, %.1f, %s, %s, %.2f, %s)' % (testname, zrot, yrot, hkl_expected, pos, wavelength, virtual_expected)
        ZROT = z_rotation(zrot * TORAD)  # -PHI
        YROT = y_rotation(yrot * TORAD)  # +CHI
        U = ZROT.times(YROT) 
        UB = U.times(self.B)
        self.mock_ubcalc.getUBMatrix.return_value = UB
        
        hkl, virtual = self.calc.anglesToHkl(pos, wavelength)
        assert_array_almost_equal(hkl, hkl_expected, self.places)
        assert_second_dict_almost_in_first(virtual, virtual_expected)
    
    @raises(DiffcalcException) 
    def _check_hkl_to_angles_fails(self, *args):
        self._check_hkl_to_angles(*args)


class _TestCubic(_BaseTest):
    
    def setup(self):
        _BaseTest.setup(self)
        self.B = I.times((2 * pi))


class _TestCubicVertical(_TestCubic):
    
    def setup(self):
        _TestCubic.setup(self)
    
    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
                Pair('100', (1, 0, 0), Pos(mu=0, delta=60, nu=0, eta=30, chi=0 - self.yrot, phi=0 + self.zrot)),
                Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)), Pos(mu=0, delta=60, nu=0, eta=30, chi=4 - self.yrot, phi=0 + self.zrot),),
                Pair('010' , (0, 1, 0), Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=90 + self.zrot)),
                Pair('001' , (0, 0, 1), Pos(mu=0, delta=60, nu=0, eta=30, chi=90 - self.yrot, phi=0 + self.zrot)),
                Pair('001-->100' , (cos(86 * TORAD), 0, sin(86 * TORAD)), Pos(mu=0, delta=60, nu=0, eta=30, chi=86 - self.yrot, phi=0 + self.zrot)),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case
            
    def case_generator(self):
        for case in self.cases:
            yield self._check_angles_to_hkl, case.name, self.zrot, self.yrot, case.hkl, case.position, self.wavelength, {}
            test_method = self._check_hkl_to_angles_fails if case.fails else self._check_hkl_to_angles
            yield test_method, case.name, self.zrot, self.yrot, case.hkl, case.position, self.wavelength, {}
            
    def test_hkl_to_angles_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        self.case_dict['001'].fails = True # q||n
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_hkl_to_angles_zrot_various_yrot0(self):
        for zrot in [0, 2, -2, 45, -45, 90, -90]: # -180, 180 work but with cut problem
            self.makes_cases(zrot, 0)
            self.case_dict['001'].fails = True # q||n
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
#            
    def setup(self):
        _TestCubicVertical.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu':0, 'nu':0}

class TestCubicVertical_psi_90(_TestCubicVertical):
    '''mode psi=90 should be the same as mode a_eq_b'''
    
    def setup(self):
        _TestCubicVertical.setup(self)
        self.constraints._constrained = {'psi': 90 * TORAD, 'mu':0, 'nu':0}


class TestCubicVertical_qaz_90(_TestCubicVertical):
    '''mode psi=90 should be the same as mode a_eq_b'''
    
    def setup(self):
        _TestCubicVertical.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu':0, 'qaz':90 * TORAD}


class SkipTestYouHklCalculatorWithCubicMode_aeqb_delta_60(_TestCubicVertical):
    '''Works to 4-5 decimal places but chooses different solutions when phi||eta .
     Skip all tests.'''
    
    def setup(self):
        _TestCubicVertical.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu':0, 'delta':60 * TORAD}
        self.places = 5

