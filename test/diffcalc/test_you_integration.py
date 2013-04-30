###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

from diffcalc.diffcalc_ import create_diffcalc
from diffcalc.hardware import DummyHardwareAdapter
from diffcalc.hkl.you.geometry import SixCircle, FourCircle
from math import pi
from test.tools import mneq_, aneq_, assert_dict_almost_equal
import diffcalc.gdasupport.factory # @UnusedImport for VERBOSE
import diffcalc.util
from diffcalc.hkl.you.constraints import NUNAME

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix


class _BaseCubic():
    
    def _new_ubcalc(self):
        wl = 1
        self.en = 12.39842 / wl 
        self.dc.ub.newub('test')
        self.dc.ub.setlat('cubic', 1, 1, 1, 90, 90, 90)
        
    
    def test_orientation_phase(self):
        # assumes reflections added were ideal (with no mis-mount)
        self.dc.ub.ub()
        self.dc.checkub()
        self.dc.ub.showref()

        U = matrix('1 0 0; 0 1 0; 0 0 1')
        UB = U * 2 * pi
        mneq_(self.dc.ub._ubcalc.U, U)
        mneq_(self.dc.ub._ubcalc.UB, UB)
        

class TestDiffcalcSixc(_BaseCubic):

    def setup(self):
        axes = 'mu', 'delta', NUNAME, 'eta', 'chi', 'phi'
        #axes = 'my_mu', 'my_delta', 'my_nu', 'my_eta', 'my_chi', 'my_phi' # TODO: Make pass!
        self.hardware = DummyHardwareAdapter(axes)
        self.dc = create_diffcalc('you', SixCircle(), self.hardware)
        
        self._new_ubcalc()
        self.dc.ub.addref([1, 0, 0], [0, 60, 0, 30, 0, 0], self.en, 'ref1')
        self.dc.ub.addref([0, 1, 0], [0, 60, 0, 30, 0, 90], self.en, 'ref2')
        
        self.hkl = [1, 0, 0]
        self.angles = [0, 60, 0, 30, 0, 0]
        self.param = {'tau': 90, 'psi': 90, 'beta': 0, 'alpha': 0, 'naz': 0, 'qaz': 90, 'theta': 30}
        
    def test_angles_to_hkl_bypassing_hardware_plugin(self):
        hkl_calc, param_calc = self.dc.angles_to_hkl(self.angles, self.en)
        aneq_(hkl_calc, self.hkl)
        assert_dict_almost_equal(param_calc, self.param)
        
    def test_hkl_to_angles_bypassing_hardware_plugin(self):
        self.dc.hkl.con('a_eq_b')
        self.dc.hkl.con('mu', 0)
        self.dc.hkl.con(NUNAME, 0)

        h, k, l = self.hkl
        angles_calc, param_calc = self.dc.hkl_to_angles(h, k, l, self.en)
        aneq_(angles_calc, self.angles)
        assert_dict_almost_equal(param_calc, self.param)

    def test_angles_to_hkl(self):
        self.energy = self.en
        hkl_calc, param_calc = self.dc.angles_to_hkl(self.angles)
        aneq_(hkl_calc, self.hkl)
        assert_dict_almost_equal(param_calc, self.param)
        
    def test_hkl_to_angles(self):
        self.dc.hkl.con('a_eq_b')
        self.dc.hkl.con('mu', 0)
        self.dc.hkl.con(NUNAME, 0)

        h, k, l = self.hkl
        self.energy = self.en
        angles_calc, param_calc = self.dc.hkl_to_angles(h, k, l)
        aneq_(angles_calc, self.angles)
        assert_dict_almost_equal(param_calc, self.param)
        
    def test_allhkl(self):
        diffcalc.util.DEBUG = True
        self.dc.hkl.con('eta', 0, 'chi', 0, 'phi', 0)
        self.dc.hkl.allhkl([.1, 0, .01], 1)


class TestDiffcalcFourc(_BaseCubic):

    def setup(self):
        axes = 'delta', 'eta', 'chi', 'phi'
        hardware = DummyHardwareAdapter(axes)
        self.dc = create_diffcalc('you', FourCircle(), hardware)

        self._new_ubcalc()
        self.dc.ub.addref([1, 0, 0], [60, 30, 0, 0], self.en, 'ref1')
        self.dc.ub.addref([0, 1, 0], [60, 30, 0, 90], self.en, 'ref2')
        
        self.hkl = [1, 0, 0]
        self.angles = [60, 30, 0, 0]
        self.param = {'tau': 90, 'psi': 90, 'beta': 0, 'alpha': 0, 'naz': 0, 'qaz': 90, 'theta': 30}
        
    def test_angles_to_hkl_bypassing_hardware_plugin(self):
        hkl_calc, param_calc = self.dc.angles_to_hkl(self.angles, self.en)
        aneq_(hkl_calc, self.hkl)
        assert_dict_almost_equal(param_calc, self.param)
        
    def test_hkl_to_angles_bypassing_hardware_plugin(self):
        self.dc.hkl.con('a_eq_b')
        h, k, l = self.hkl
        angles_calc, param_calc = self.dc.hkl_to_angles(h, k, l, self.en)
        aneq_(angles_calc, self.angles)
        assert_dict_almost_equal(param_calc, self.param)
        
        
    def test_angles_to_hkl(self):
        self.energy = self.en
        hkl_calc, param_calc = self.dc.angles_to_hkl(self.angles, self.en)
        aneq_(hkl_calc, self.hkl)
        assert_dict_almost_equal(param_calc, self.param)
        
    def test_hkl_to_angles(self):
        self.dc.hkl.con('a_eq_b')
        h, k, l = self.hkl
        self.energy = self.en
        angles_calc, param_calc = self.dc.hkl_to_angles(h, k, l, self.en)
        aneq_(angles_calc, self.angles)
        assert_dict_almost_equal(param_calc, self.param)