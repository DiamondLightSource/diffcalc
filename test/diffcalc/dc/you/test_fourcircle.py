from math import pi

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix
from test.tools import mneq_, aneq_, assert_dict_almost_equal

import diffcalc.util  # @UnusedImport
from diffcalc.hardware import DummyHardwareAdapter
from diffcalc.hkl.you.geometry import FourCircle
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc import settings


diffcalc.util.DEBUG = True
wl = 1
en = 12.39842 / wl

angles = [60, 30, 0, 0]
param = {'tau': 90, 'psi': 90, 'beta': 0, 'alpha': 0, 'naz': 0, 'qaz': 90, 'theta': 30, 'ttheta': 60, 'betain': 0, 'betaout': 0}


dc = None
def setup_module():
    global dc
    axes = 'delta', 'eta', 'chi', 'phi'
    settings.hardware = DummyHardwareAdapter(axes)
    settings.geometry = FourCircle()
    settings.ubcalc_persister = UbCalculationNonPersister()
    settings.reference_vector = matrix('0; 0; 1')
    
    from diffcalc.dc import dcyou as dc
    reload(dc)
    dc.newub('test')
    dc.setlat('cubic', 1, 1, 1, 90, 90, 90)
    dc.addref([1, 0, 0], [60, 30, 0, 0], en, 'ref1')
    dc.addref([0, 1, 0], [60, 30, 0, 90], en, 'ref2')

def test_orientation_phase():
    # assumes reflections added were ideal (with no mis-mount)
    dc.ub()
    dc.checkub()
    dc.showref()

    U = matrix('1 0 0; 0 1 0; 0 0 1')
    UB = U * 2 * pi
    mneq_(dc._ub.ubcalc.U, U)
    mneq_(dc._ub.ubcalc.UB, UB)
   
def test_angles_to_hkl_bypassing_hardware_plugin():
    hkl_calc, param_calc = dc.angles_to_hkl(angles, en)
    aneq_(hkl_calc, [1, 0, 0])
    assert_dict_almost_equal(param_calc, param)
    
def test_hkl_to_angles_bypassing_hardware_plugin():
    dc.con('a_eq_b')
    h, k, l = [1, 0, 0]
    angles_calc, param_calc = dc.hkl_to_angles(h, k, l, en)
    aneq_(angles_calc, angles)
    assert_dict_almost_equal(param_calc, param)
    
def test_angles_to_hkl():
    hkl_calc, param_calc = dc.angles_to_hkl(angles, en)
    aneq_(hkl_calc, [1, 0, 0])
    assert_dict_almost_equal(param_calc, param)
    
def test_hkl_to_angles():
    dc.con('a_eq_b')
    h, k, l = [1, 0, 0]
    angles_calc, param_calc = dc.hkl_to_angles(h, k, l, en)
    aneq_(angles_calc, angles)
    assert_dict_almost_equal(param_calc, param)