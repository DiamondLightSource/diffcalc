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

from mock import Mock
from diffcalc.ub.reference import YouReference
from test.tools import assert_array_almost_equal, assert_2darray_almost_equal

try:
    from numpy import matrix, hstack
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix, hstack
    from numjy.linalg import norm


class TestYouReference():

    def setUp(self):
        self.ubcalc = Mock()
        self.reference = YouReference(self.ubcalc)
        self.ubcalc.UB = matrix('1 0 0; 0 1 0; 0 0 1')
        
    def test_default_n_phi(self):
        assert_2darray_almost_equal(self.reference.n_phi.tolist(), matrix('0; 0; 1').tolist())
        
    def test__str__with_phi_configured(self):
        print self.reference
        
    def test__str__with_hkl_configured(self):
        self.reference.n_hkl_configured = matrix('0; 1; 1')
        print self.reference
        
    def test_n_phi_from_hkl_with_unity_matrix_001(self):
        self.ubcalc.UB = matrix('1 0 0; 0 1 0; 0 0 1')
        self.reference.n_hkl_configured = matrix('0; 0; 1')
        assert_2darray_almost_equal(self.reference.n_phi.tolist(), matrix('0; 0; 1').tolist())

    def test_n_phi_from_hkl_with_unity_matrix_010(self):
        self.ubcalc.UB = matrix('1 0 0; 0 1 0; 0 0 1')
        self.reference.n_hkl_configured = matrix('0; 1; 0')
        assert_2darray_almost_equal(self.reference.n_phi.tolist(), matrix('0; 1; 0').tolist())
        
        
        

 