'''
Created on 28 Feb 2017

@author: zrb13439
'''
import unittest
from diffcalc.gdasupport.scannable.mock import MockMotor
from startup.beamlinespecific.i21 import I21SampleStage, calc_tp_lab,\
    I21DiffractometerStage, I21TPLab, move_lab_origin_into_phi
import mock
from diffcalc.gdasupport.minigda.scannable import Scannable, ScannableBase
from nose.tools import eq_
from test.tools import assert_array_almost_equal as aneq_, aneq_
from math import sqrt


def mock_scannable(name='mock', pos=0):
    scn = mock.Mock(ScannableBase)
    scn.getName.return_value = name
    scn.getPosition.return_value = pos
    return scn


class TestI21SampleStageBase(unittest.TestCase):

    def setUp(self):
        self.sapol = mock_scannable('sapol', 1)
        self.satilt = mock_scannable('satilt', 2)
        self.saaz = mock_scannable('saaz',3 )
        self.xyz_eta = mock_scannable('xyz_eta', [10, 11, 12])

        self.sa = I21SampleStage('sa', self.sapol, self.satilt, self.saaz,
                                 self.xyz_eta)


class TestI21SampleStageNoTp(TestI21SampleStageBase):
        
    def testGetInputNames(self):
        eq_(self.sa.getInputNames(), ['sapol', 'satilt', 'saaz'])
        
    def testGetPosition(self):
        eq_(self.sa.getPosition(), [1, 2, 3])
        
    def testAsynchronousMoveTo(self):
        self.sa.asynchronousMoveTo([4, 5, 6])
        self.sapol.asynchronousMoveTo.assert_called_with(4)
        self.satilt.asynchronousMoveTo.assert_called_with(5)
        self.saaz.asynchronousMoveTo.assert_called_with(6)
        
    def test__str__(self):
        self.sa.tp_phi = [1, 2, 3]
        self.sapol.getPosition.return_value = 0
        self.satilt.getPosition.return_value = -90  # chi = 0
        self.saaz.getPosition.return_value = 0
        self.xyz_eta.getPosition.return_value = [10, 20, 30]
        
        print self.sa.__str__()
        desired = \
"""sa:                             
sapolar:   0.00000 (eta)        tp_phi :  1.0000  2.0000  3.0000 (set)
satilt:    -90.00000 (chi-90)   tp_lab : 11.0000 22.0000 33.0000
saazimuth: 0.00000 (phi)        xyz_eta: 10.0000 20.0000 30.0000"""
        result_lines = self.sa.__str__().split('\n')[0:4]
        print 'Result:'
        print '\n'.join(result_lines)
        print '---'
        eq_('\n'.join(result_lines), desired)
        
    def test_tp_scannable_get(self):
        self.sa.tp_phi = [1, 2, 3]
        eq_(self.sa.tp_phi_scannable.getPosition(), [1, 2, 3])
        
    def test_tp_scannable_set(self):
        self.sa.tp_phi_scannable.asynchronousMoveTo([4, 5, 6])
        eq_(self.sa.tp_phi, [4, 5, 6])


class TestI21DiffractometerStage(unittest.TestCase):
       
    def setUp(self):
        self.delta = mock_scannable('delta', 1 )
        self.sa = mock_scannable('sa', [2, 3, 4]) 
        self.fourc = I21DiffractometerStage('four', self.delta, self.sa, 90)
        
    def testGetPosition(self):
        aneq_(self.fourc.getPosition(), [1, 2, 93, 4])

    def testAsynchMoveToComplete(self):
        self.fourc.asynchronousMoveTo([1, 2, 93, 4])
        self.delta.asynchronousMoveTo.assert_called_with(1)
        self.sa.asynchronousMoveTo.assert_called_with([2, 3, 4])

    def testAsynchMoveToDeltaOnly(self):
        self.fourc.asynchronousMoveTo([1, None, None, None])
        self.delta.asynchronousMoveTo.assert_called_with(1)
        self.sa.asynchronousMoveTo.assert_not_called()

    def testAsynchMoveToEtaOnly(self):
        self.fourc.asynchronousMoveTo([None, 2, None, None])
        self.delta.asynchronousMoveTo.assert_not_called()
        self.sa.asynchronousMoveTo.assert_called_with([2, None, None])

    def testAsynchMoveToChiOnly(self):
        self.fourc.asynchronousMoveTo([None, None, 93, None])
        self.delta.asynchronousMoveTo.assert_not_called()
        self.sa.asynchronousMoveTo.assert_called_with([None, 3, None])
        
 
class TestI21TPLab(unittest.TestCase):
       
    def setUp(self):
        self.delta = mock_scannable('delta', 1 )
        self.sa = mock.Mock()
        self.sa.tp_phi = [1, 2, 3]
        self.sa.xyz_eta_scn.getPosition.return_value = [10, 20, 30]
        self.sa.getEulerPosition.return_value = [0, 0, 0]
        self.tp_lab = I21TPLab('tp_lab', self.sa)
        
    def testGetPosition(self):
        aneq_(self.tp_lab.getPosition(), [11, 22, 33])

    def testAsynchMoveToComplete(self):
        self.tp_lab.asynchronousMoveTo([11, 22, 33])
        self.sa.xyz_eta_scn.asynchronousMoveTo.assert_called_with([10, 20, 30])              

        

class TestCalcTpLab_No_xyz_eta(unittest.TestCase):
    
    def test_calc_tp_lab__tp_phi_0(self):
        eq_(calc_tp_lab([0, 0, 0], 0, 0, 0), [0, 0, 0])
        eq_(calc_tp_lab([0, 0, 0], 1, 2, 3), [0, 0, 0])

    def test_calc_tp_lab__lab_eq_phi_frame(self):
        eq_(calc_tp_lab([1, 2, 3], 0, 0, 0), [1, 2, 3])

    def test_calc_tp_lab__lab_z_parallel_to_phi_and_eta(self):
        eq_(calc_tp_lab([0, 0, 1], 1, 0, 0), [0, 0, 1])
        eq_(calc_tp_lab([0, 0, 1], 0, 0, 1), [0, 0, 1])
        eq_(calc_tp_lab([0, 0, 1], 1, 0, 1), [0, 0, 1])
        
    def test_calc_tp_lab_eta0_chi90(self):
        aneq_(calc_tp_lab([0, 0, 1], 0, 90, 0), [1, 0, 0]) 
        aneq_(calc_tp_lab([0, 0, 1], 0, 90, 1), [1, 0, 0])
        eq_(calc_tp_lab([0, 0, 1], 1, 0, 1), [0, 0, 1])
        
    def test_calc_tp_lab_eta0_eta90(self):
        aneq_(calc_tp_lab([0, 1, 0], 90, 0, 0), [1, 0, 0]) 
        aneq_(calc_tp_lab([0, 1, 0], 90, 1, 0), [1, 0, 0])

    def test_calc_tp_lab_tp_phi_101(self):
        aneq_(calc_tp_lab([1, 0, 1], 0, 45, 0), [sqrt(2), 0, 0]) 

    def test_calc_tp_lab_tp_phi_110(self):
        aneq_(calc_tp_lab([1, 1, 0], 45, 0, 0), [sqrt(2), 0, 0]) 
        aneq_(calc_tp_lab([1, 1, 0], 0, 0, 45), [sqrt(2), 0, 0]) 
        aneq_(calc_tp_lab([1, 1, 0], 46, 0, -1), [sqrt(2), 0, 0]) 
        

class TestCalcTpLabWithXyzEta(unittest.TestCase):
    
    def test_calc_tp_lab__tp_phi_0(self):
        eq_(calc_tp_lab([0, 0, 0], 0, 0, 0, [0, 0, 0]), [0, 0, 0])
        eq_(calc_tp_lab([0, 0, 0], 0, 0, 0, [4, 5, 6]), [4, 5, 6])
        eq_(calc_tp_lab([10, 20, 30], 0, 0, 0, [1, 2, 3]), [11, 22, 33])

    def test_calc_tp_lab__lab_eq_phi_frame(self):
        eq_(calc_tp_lab([0, 0, 1], 0, 0, 99, [1, 2, 3]), [1, 2, 4])
        eq_(calc_tp_lab([0, 0, 1], 0, 0, 99, [0, 0, 0]), [0, 0, 1])
        eq_(calc_tp_lab([0, 0, 1], 1, 0, 99, [0, 0, 0]), [0, 0, 1])
         
    def test_calc_tp_lab_eta0_chi90(self):
        aneq_(calc_tp_lab([0, 0, 1], 0, 90, 0, [0, 0, 0]), [1, 0, 0]) 
        aneq_(calc_tp_lab([0, 0, 1], 0, 90, 1, [0, 0, 0]), [1, 0, 0])
        aneq_(calc_tp_lab([0, 0, 1], 1, 00, 1, [0, 0, 0]), [0, 0, 1])
#         
#     def test_calc_tp_lab_eta0_eta90(self):
#         aneq_(calc_tp_lab([0, 1, 0], 90, 0, 0), [1, 0, 0]) 
#         aneq_(calc_tp_lab([0, 1, 0], 90, 1, 0), [1, 0, 0])
# 
#     def test_calc_tp_lab_tp_phi_101(self):
#         aneq_(calc_tp_lab([1, 0, 1], 0, 45, 0), [sqrt(2), 0, 0]) 
# 
#     def test_calc_tp_lab_tp_phi_110(self):
#         aneq_(calc_tp_lab([1, 1, 0], 45, 0, 0), [sqrt(2), 0, 0]) 
#         aneq_(calc_tp_lab([1, 1, 0], 0, 0, 45), [sqrt(2), 0, 0]) 
#         aneq_(calc_tp_lab([1, 1, 0], 46, 0, -1), [sqrt(2), 0, 0]) 
#  
class TestMoveLabOriginIntoPhi(unittest.TestCase):
    
    def test_xyz_eta_0(self):
        aneq_(move_lab_origin_into_phi(0, 0, [0, 0, 0]), [0, 0, 0])
        aneq_(move_lab_origin_into_phi(1, 2, [0, 0, 0]), [0, 0, 0])

    def test_chi_phi_0(self):
        aneq_(move_lab_origin_into_phi(0, 0, [1, 2, 3]), [-1, -2, -3])
        aneq_(move_lab_origin_into_phi(0, 0, [-3, -2, -1]), [3, 2, 1])
        
    def test_stable_about_phi(self):
        aneq_(move_lab_origin_into_phi(0, 99, [0, 0, 3]), [0, 0, -3])

    def test_stable_about_chi(self):
        aneq_(move_lab_origin_into_phi(99, 0, [0, 3, 0]), [0, -3, 0])

    def test_rotate_about_phi(self):
        aneq_(move_lab_origin_into_phi(0, 45, [0, 1, 4]),
              [sqrt(.5), -sqrt(.5), -4])


class TestI21SampleStageWithTP(TestI21SampleStageBase):
    # Npte all are independent of eta
    # Note tp_phi is the TARGET tool point to end up at the diffractometer centre
    
    def _move(self, tp_phi, pol, tilt, az):
        self.sa.tp_phi = tp_phi
        self.sa.asynchronousMoveTo([pol, tilt, az])

    def _check(self, desired_xyz):
        called_with_xyz = self.xyz_eta.asynchronousMoveTo.call_args[0][0]
        aneq_(called_with_xyz, desired_xyz)
    
    def testAsynchronousMoveTo_tp_phi_0(self):
        self._move([0, 0, 0], 99, 2 - 90, 3); self._check([0, 0, 0])
        
    def test_calc_tp_lab__tp_phi_0(self):
        self._move([0, 0, 0], 99, 0 - 90, 0); self._check([0, 0, 0])
        self._move([0, 0, 0], 99, 2 - 90, 3); self._check([0, 0, 0])
  
    def test_calc_tp_lab__lab_eq_phi_frame(self):
        self._move([1, 2, 3], 99, 0 - 90, 0); self._check([-1, -2, -3])
 
    def test_calc_tp_lab__lab_z_parallel_to_phi_and_eta(self):
        self._move([0, 0, 1], 99, 0 - 90, 0); self._check([0, 0, -1])
        self._move([0, 0, 1], 99, 0 - 90, 1); self._check([0, 0, -1])
        self._move([0, 0, 1], 99, 0 - 90, 1); self._check([0, 0, -1])
         
    def test_calc_tp_lab_eta0_chi90(self):
        self._move([0, 0, 1], 99, 90 - 90, 0); self._check([-1, 0, 0]) 
        self._move([0, 0, 1], 99, 90 - 90, 1); self._check([-1, 0, 0])
        self._move([0, 0, 1], 99, 0 - 90, 1); self._check([0, 0, -1])
 
    def test_calc_tp_lab_tp_phi_101(self):
        self._move([1, 0, 1], 99, 45 - 90, 0); self._check([-sqrt(2), 0, 0]) 
# 
    def test_calc_tp_lab_tp_phi_110(self):
        self._move([1, 1, 0], 99, 0 - 90, 45); self._check([-sqrt(2), 0, 0]) 

