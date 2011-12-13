from diffcalc.hkl.you.calculation import youAnglesToHkl, YouHklCalculator
from diffcalc.hkl.you.constraints import ConstraintManager
from diffcalc.tools import arrayeq_, assert_array_almost_equal, \
    assert_second_dict_almost_in_first, assert_matrix_almost_equal
from diffcalc.utils import Position, createYouMatrices, calcCHI, calcPHI, \
    y_rotation, z_rotation, YouPosition as Pos, DiffcalcException
from math import pi, sqrt, cos, sin
from nose.plugins.skip import SkipTest
from nose.tools import raises
from tests.diffcalc.hkl.test_calcvlieg import createMockDiffractometerGeometry, \
    createMockHardwareMonitor, createMockUbcalc

try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

TORAD = pi / 180
TODEG = 180 / pi



I = Matrix.identity(3, 3)


def posFromI16sEuler(phi, chi, eta, mu, delta, gamma):
    return Position(mu, delta, gamma, eta, chi, phi)

class TestAnglesToHkl_I16Examples():
    
    def __init__(self):
        self.UB1 = Matrix(
             ((0.9996954135095477, -0.01745240643728364, -0.017449748351250637),
              (0.01744974835125045, 0.9998476951563913, -0.0003045864904520898),
              (0.017452406437283505, -1.1135499981271473e-16, 0.9998476951563912))
            ).times(2 * pi)
        self.WL1 = 1 # Angstrom

    def test_anglesToHkl_mu_0_gam_0(self):
        pos = posFromI16sEuler(1, 1, 30, 0, 60, 0).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1), [1, 0, 0])
    
    def test_anglesToHkl_mu_0_gam_10(self):
        pos = posFromI16sEuler(1, 1, 30, 0, 60, 10).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1), [1.00379806, -0.006578435, 0.08682408])
        
    def test_anglesToHkl_mu_10_gam_0(self):
        pos = posFromI16sEuler(1, 1, 30, 10, 60, 0).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1), [0.99620193, 0.0065784359, 0.08682408])
        
    def test_anglesToHkl_arbitrary(self):
        pos = posFromI16sEuler(1.9, 2.9, 30.9, 0.9, 60.9, 2.9).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1), [1.01174189, 0.02368622, 0.06627361])
    

class TestBase():
    
    def setup(self):
        self.mock_ubcalc = createMockUbcalc(None)
        self.mock_geometry = createMockDiffractometerGeometry()
        self.mock_hardware = createMockHardwareMonitor
        
        self.constraints = ConstraintManager(self.mock_hardware)
        self.calc = YouHklCalculator(self.mock_ubcalc, self.mock_geometry, self.mock_hardware, self.constraints)
        
#    def _check_angles_to_virtual_angles(self, testname, pos, wavelength, virtual_expected):
#        assert_second_dict_almost_in_first(self.calc.anglesToVirtualAngles(pos, wavelength),
#                                 virtual_expected)
#    
#    def _check_angles_to_hkl(self, testname, hkl_expected, pos, wavelength, virtual_expected):
#        hkl, virtual = self.calc.anglesToHkl(pos, wavelength)
#        assert_array_almost_equal(hkl, hkl_expected)
#        assert_second_dict_almost_in_first(virtual, virtual_expected)
    
    def _check_hkl_to_angles(self, testname, zrot, yrot, hkl, pos_expected, wavelength, virtual_expected):
        ZROT = z_rotation(zrot * TORAD)  # -PHI
        YROT = y_rotation(yrot * TORAD)  # +CHI
        U = ZROT.times(YROT) 
        UB = U.times(self.B)
        self.mock_ubcalc.getUBMatrix.return_value = UB
        
        pos, virtual = self.calc.hklToAngles(hkl[0], hkl[1], hkl[2], wavelength)
        assert_array_almost_equal(pos.totuple(), pos_expected.totuple())
        assert_second_dict_almost_in_first(virtual, virtual_expected)
    
    @raises(DiffcalcException) 
    def _check_hkl_to_angles_fails(self, *args):
        self._check_hkl_to_angles(*args)


class TestYouHklCalculatorWithCubic(TestBase):
    
    def setup(self):
        TestBase.setup(self)
        self.B = I.times((2 * pi))
       
        
    
    def case(self, name, fails=False, mu=None, delta=None, nu=None, eta=None, chi=None, phi=None):
        cases = {
                '100': ((1, 0, 0),
                        Pos(mu=0, delta=60, nu=0, eta=30, chi=0 - self.yrot, phi=0 + self.zrot), 1, {}),
                '100-->001': ((cos(4 * TORAD), 0, sin(4 * TORAD)),
                        Pos(mu=0, delta=60, nu=0, eta=30, chi=4 - self.yrot, phi=0 + self.zrot), 1, {}),
                '010' : ((0, 1, 0),
                        Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=90 + self.zrot), 1, {}), # chi||010
                '001' : ((0, 0, 1),
                        Pos(mu=0, delta=60, nu=0, eta=30, chi=90 - self.yrot, phi=0 + self.zrot), 1, {}),
                '001-->100' : ((cos(86 * TORAD), 0, sin(86 * TORAD)),
                        Pos(mu=0, delta=60, nu=0, eta=30, chi=86 - self.yrot, phi=0 + self.zrot), 1, {}),
            }
        test_method = self._check_hkl_to_angles_fails if fails else self._check_hkl_to_angles
        t = (test_method, name, self.zrot, self.yrot) + cases[name]
        if mu is not None:
            t[5].mu = mu
        if delta is not None:
            t[5].delta = delta
        if nu is not None:
            t[5].nu = nu
        if eta is not None:
            t[5].eta = eta
        if chi is not None:
            t[5].chi = chi
        if phi is not None:
            t[5].phi = phi
        return t
    
    
#    def test_angles_to_hkl(self):
#        for testname, hkl_expected, pos, wavelength, virtual in self.cases:
#            yield self._check_angles_to_hkl, testname, hkl_expected, pos, wavelength, virtual

class TestYouHklCalculatorWithCubicMode_a_eq_b(TestYouHklCalculatorWithCubic):
#            
    def setup(self):
        TestYouHklCalculatorWithCubic.setup(self)
        self.constraints._constrained = {'psi': 90*TORAD, 'mu':0, 'nu':0}

    def test_hkl_to_angles_zrot0_yrot0(self):
        self.zrot = self.yrot = 0 
        yield self.case('100')
        yield self.case('100-->001')
        yield self.case('001-->100')
        yield self.case('001', fails=True) # q||n
        yield self.case('010')

    def test_hkl_to_angles_zrot_various_yrot0(self):
        self.yrot = 0
        for self.zrot in [0, 2, -2, 45, -45, 90, -90]: # -180, 180 work but with cut problem
            yield self.case('100')
            yield self.case('100-->001')
            yield self.case('001-->100')
            yield self.case('001', fails=True) # q||n
            yield self.case('010')
            
    def test_hkl_to_angles_zrot1_yrot2(self):
        self.zrot = 1
        self.yrot = 2 
        yield self.case('100', eta=-150,chi=178) # TODO: Unexpected solution
        yield self.case('100-->001')
        yield self.case('001-->100')
        yield self.case('001')
        yield self.case('010')
            
    def test_hkl_to_angles_zrot1_yrotm2(self):
        self.zrot = 1
        self.yrot = -2 
        yield self.case('100') # TODO: Unexpected solution
        yield self.case('100-->001')
        yield self.case('001-->100')
        yield self.case('001', chi=88, phi=-179)
        yield self.case('010')
    
            
class TestYouHklCalculatorWithCubicMode_psi_90(TestYouHklCalculatorWithCubicMode_a_eq_b):
    '''mode psi=90 should be the same as mode a_eq_b'''
    
    def setup(self):
        TestYouHklCalculatorWithCubicMode_a_eq_b.setup(self)
        self.constraints._constrained = {'psi': 90*TORAD, 'mu':0, 'nu':0}

class TestYouHklCalculatorWithCubicMode_aeqb_qaz_90(TestYouHklCalculatorWithCubicMode_a_eq_b):
    '''mode psi=90 should be the same as mode a_eq_b'''
    
    def setup(self):
        TestYouHklCalculatorWithCubicMode_a_eq_b.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu':0, 'qaz':90*TORAD}

# Many fail with unexpected solutions
#class TestYouHklCalculatorWithCubicMode_aeqb_delta_60(TestYouHklCalculatorWithCubicMode_a_eq_b):
#    
#    def setup(self):
#        TestYouHklCalculatorWithCubicMode_a_eq_b.setup(self)
#        self.constraints._constrained = {'a_eq_b': None, 'mu':0, 'delta':59.9999999999999*TORAD}