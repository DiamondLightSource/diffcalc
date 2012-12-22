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

from diffcalc.hkl.you.calc import YouUbCalcStrategy
from diffcalc.hkl.you.geometry import SixCircle, YouPosition
from diffcalc.ub.calc import UBCalculation
from diffcalc.ub.persistence import UBCalculationJSONPersister
from math import pi
from mock import Mock
from nose.tools import eq_
from test.tools import matrixeq_
import tempfile
import datetime

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix



def posFromI16sEuler(phi, chi, eta, mu, delta, gamma):
    return YouPosition(mu, delta, gamma, eta, chi, phi)

UB1 = matrix(
    ((0.9996954135095477, -0.01745240643728364, -0.017449748351250637),
     (0.01744974835125045, 0.9998476951563913, -0.0003045864904520898),
     (0.017452406437283505, -1.1135499981271473e-16, 0.9998476951563912))
    ) * (2 * pi)

EN1 = 12.39842
REF1a = posFromI16sEuler(1, 1, 30, 0, 60, 0)
REF1b = posFromI16sEuler(1, 91, 30, 0, 60, 0)


class TestUBCalculationWithYouStrategy():
    """Testing the math only here.
    """

    def setUp(self):
        
        self.tempdir = tempfile.mkdtemp()

        geometry = SixCircle()  # pass through
        hardware = Mock()
        names = 'm', 'd', 'n', 'e', 'c', 'p'
        hardware.get_axes_names.return_value = names
        self.tmpdir = tempfile.mkdtemp()
        print self.tmpdir
        self.ubcalc = UBCalculation(hardware,
                                    geometry,
                                    UBCalculationJSONPersister(self.tmpdir),
                                    YouUbCalcStrategy())

    def testAgainstI16Results(self):
        self.ubcalc.start_new('cubcalc')
        self.ubcalc.set_lattice('latt', 1, 1, 1, 90, 90, 90)
        self.ubcalc.add_reflection(1, 0, 0, REF1a, EN1, '100', None)
        self.ubcalc.add_reflection(0, 0, 1, REF1b, EN1, '001', None)
        matrixeq_(self.ubcalc.UB, UB1)
        
    def test_save_and_restore_empty_ubcalc_with_one_already_started(self):
        NAME = 'test_save_and_restore_empty_ubcalc_with_one_already_started'
        self.ubcalc.start_new(NAME)
        self.ubcalc.start_new(NAME)
    
    
    def test_save_and_restore_empty_ubcalc(self):
        NAME = 'test_save_and_restore_empty_ubcalc'
        self.ubcalc.start_new(NAME)
        
        self.ubcalc.start_new(NAME + '2')
        self.ubcalc.load(NAME)
        
        eq_(self.ubcalc.name, NAME)
        
    def test_save_and_restore_ubcalc_with_lattice(self):
        NAME = 'test_save_and_restore_ubcalc_with_lattice'
        self.ubcalc.start_new(NAME)
        self.ubcalc.set_lattice('latt', 1, 1, 1, 90, 90, 90)
        
        self.ubcalc.start_new(NAME + '2')
        self.ubcalc.load(NAME)
        
        eq_(self.ubcalc._state.crystal.getLattice(), ('latt', 1, 1, 1, 90, 90, 90))
        
    def test_save_and_restore_ubcalc_with_reflections(self):
        NAME = 'test_save_and_restore_ubcalc_with_reflections'
        self.ubcalc.start_new(NAME)
        now = datetime.datetime.now()
        self.ubcalc.add_reflection(1, 0, 0, REF1a, EN1, '100', now)
        self.ubcalc.add_reflection(0, 0, 1, REF1b, EN1, '001', now)
        self.ubcalc.add_reflection(0, 0, 1.5, REF1b, EN1, '001_5', now)
        ref1 = self.ubcalc.get_reflection(1)
        ref2 = self.ubcalc.get_reflection(2)
        ref3 = self.ubcalc.get_reflection(3)
        eq_(self.ubcalc.get_reflection(1), ref1)
        eq_(self.ubcalc.get_reflection(2), ref2)
        eq_(self.ubcalc.get_reflection(3), ref3)
        
        self.ubcalc.start_new(NAME + '2')
        self.ubcalc.load(NAME)
        
        eq_(self.ubcalc.get_reflection(1), ref1)
        eq_(self.ubcalc.get_reflection(2), ref2)
        eq_(self.ubcalc.get_reflection(3), ref3)
        
    def test_save_and_restore_ubcalc_with_UB_from_two_ref(self):
        NAME = 'test_save_and_restore_ubcalc_with_UB_from_two_ref'
        self.ubcalc.start_new(NAME)
        self.ubcalc.set_lattice('latt', 1, 1, 1, 90, 90, 90)
        self.ubcalc.add_reflection(1, 0, 0, REF1a, EN1, '100', None)
        self.ubcalc.add_reflection(0, 0, 1, REF1b, EN1, '001', None)
        matrixeq_(self.ubcalc.UB, UB1)
        
        self.ubcalc.start_new(NAME + '2')
        self.ubcalc.load(NAME)
        
        matrixeq_(self.ubcalc.UB, UB1)
        
    def test_save_and_restore_ubcalc_with_UB_from_one_ref(self):
        NAME = 'test_save_and_restore_ubcalc_with_UB_from_one_ref'
        self.ubcalc.start_new(NAME)
        self.ubcalc.set_lattice('latt', 1, 1, 1, 90, 90, 90)
        self.ubcalc.add_reflection(1, 0, 0, REF1a, EN1, '100', None)
        self.ubcalc.calculate_UB_from_primary_only()
        matrixeq_(self.ubcalc.UB, UB1,  places=2)
        
        self.ubcalc.start_new(NAME + '2')
        self.ubcalc.load(NAME)
        
        matrixeq_(self.ubcalc.UB, UB1,  places=2)

    def test_save_and_restore_ubcalc_with_manual_ub(self):
        NAME = 'test_save_and_restore_ubcalc_with_manual_ub'
        UB = matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.ubcalc.start_new(NAME)
        self.ubcalc.set_UB_manually(UB)
        matrixeq_(self.ubcalc.UB, UB)
        
        self.ubcalc.start_new(NAME + '2')
        self.ubcalc.load(NAME)
        
        matrixeq_(self.ubcalc.UB, UB)

    def test_save_and_restore_ubcalc_with_manual_u(self):
        NAME = 'test_save_and_restore_ubcalc_with_manual_u'
        U = matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.ubcalc.start_new(NAME)
        self.ubcalc.set_lattice('latt', 1, 1, 1, 90, 90, 90)
        self.ubcalc.set_U_manually(U)
        matrixeq_(self.ubcalc.UB, U * 2 * pi)
        
        self.ubcalc.start_new(NAME + '2')
        self.ubcalc.load(NAME)
        
        matrixeq_(self.ubcalc.UB, U * 2 * pi)


