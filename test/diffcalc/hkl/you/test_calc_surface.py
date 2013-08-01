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

# TODO: class largely copied from test_calc

from math import pi
from mock import Mock
from nose.plugins.skip import SkipTest

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.hkl.you.geometry import SixCircle
from diffcalc.hkl.willmott.calc import \
    WillmottHorizontalPosition as WillPos
from diffcalc.hkl.you.geometry import YouPosition as YouPos
from diffcalc.hkl.you.calc import YouUbCalcStrategy
from test.tools import matrixeq_
from diffcalc.ub.calc import UBCalculation
from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.ub.persistence import UbCalculationNonPersister
from test.diffcalc.hkl.you.test_calc import _BaseTest
from diffcalc.hkl.you.constraints import NUNAME

TORAD = pi / 180
TODEG = 180 / pi
I = matrix('1 0 0; 0 1 0; 0 0 1')


class SkipTestSurfaceNormalVerticalCubic(_BaseTest):

    def setup(self):

        _BaseTest.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu': -pi / 2,
                                         'eta': 0}
        self.wavelength = 1
        self.UB = I * 2 * pi

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        if pos is not None:
            self._check_angles_to_hkl('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails('', 999, 999, hkl, pos,
                                            self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)

    def testHkl001(self):
        pos = YouPos(mu=-90, delta=60, nu=0, eta=0, chi=90 + 30, phi=-90)
        self._check((0, 0, 1), pos, {'alpha': 30, 'beta': 30})

    def testHkl011(self):
        # raise SkipTest()
        # skipped because we can't calculate values to check against by hand
        pos = YouPos(mu=-90, delta=90, nu=0, eta=0, chi=90 + 90, phi=-90)
        self._check((0, 1, 1), pos, {'alpha': 45, 'beta': 45})

    def testHkl010fails(self):
        self._check((0, 1, 0),
                    None,
                    {'alpha': 30, 'beta': 30}, fails=True)

    def testHkl100fails(self):
        self._check((1, 0, 0),
                    None,
                    {'alpha': 30, 'beta': 30}, fails=True)

    def testHkl111(self):
        raise SkipTest()
        # skipped because we can't calculate values to check against by hand
        pos = YouPos(mu=-90, delta=90, nu=0, eta=0, chi=90 + 90, phi=-90)
        self._check((1, 1, 1), pos, {'alpha': 45, 'beta': 45})


# Primary and secondary reflections found with the help of DDIF on Diamond's
# i07 on Jan 27 2010


HKL0 = 2, 19, 32
REF0 = WillPos(delta=21.975, gamma=4.419, omegah=2, phi=326.2)

HKL1 = 0, 7, 22
REF1 = WillPos(delta=11.292, gamma=2.844, omegah=2, phi=124.1)

WAVELENGTH = 0.6358
ENERGY = 12.39842 / WAVELENGTH


# This is the version that Diffcalc comes up with ( see following test)
U_DIFFCALC = matrix([[-0.7178876, 0.6643924, -0.2078944],
                     [-0.6559596, -0.5455572, 0.5216170],
                     [0.2331402, 0.5108327, 0.8274634]])


#class WillmottHorizontalGeometry(VliegGeometry):
#
#    def __init__(self):
#        VliegGeometry.__init__(self,
#                    name='willmott_horizontal',
#                    supported_mode_groups=[],
#                    fixed_parameters={},
#                    gamma_location='base'
#                    )
#
#    def physical_angles_to_internal_position(self, physicalAngles):
#        assert (len(physicalAngles) == 4), "Wrong length of input list"
#        return WillPos(*physicalAngles)
#
#    def internal_position_to_physical_angles(self, internalPosition):
#        return internalPosition.totuple()

def willmott_to_you_fixed_mu_eta(pos):
    pos = YouPos(mu=-90,
                       delta=pos.delta,
                       nu=pos.gamma,
                       eta=0,
                       chi=90 + pos.omegah,
                       phi=-90 - pos.phi)

    if pos.phi > 180:
        pos.phi -= 360
    elif pos.phi < -180:
        pos.phi += 360
    return pos


class TestUBCalculationWithWillmotStrategy_Si_5_5_12_FixedMuEta():

    def setUp(self):

        hardware = Mock()
        hardware.get_axes_names.return_value = ('m', 'd', 'n', 'e', 'c',
                                                       'p')
        self.ubcalc = UBCalculation(hardware, SixCircle(),
                                    UbCalculationNonPersister(),
                                    YouUbCalcStrategy())

    def testAgainstResultsFromJan_27_2010(self):
        self.ubcalc.start_new('test')
        self.ubcalc.set_lattice('Si_5_5_12', 7.68, 53.48, 75.63, 90, 90, 90)
        self.ubcalc.add_reflection(
            HKL0[0], HKL0[1], HKL0[2], willmott_to_you_fixed_mu_eta(REF0),
            ENERGY, 'ref0', None)
        self.ubcalc.add_reflection(
            HKL1[0], HKL1[1], HKL1[2], willmott_to_you_fixed_mu_eta(REF1),
            ENERGY, 'ref1', None)
        self.ubcalc.calculate_UB()
        print "U: ", self.ubcalc.U
        print "UB: ", self.ubcalc.UB
        matrixeq_(self.ubcalc.U, U_DIFFCALC)


class TestFixedMuEta(_BaseTest):

    def setup(self):
        _BaseTest.setup(self)
        self._configure_constraints()
        self.wavelength = 0.6358
        B = CrystalUnderTest('xtal', 7.68, 53.48,
                             75.63, 90, 90, 90).B
        self.UB = U_DIFFCALC * B
        self._configure_limits()

    def _configure_constraints(self):
        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu': -pi / 2,
                                         'eta': 0}

    def _configure_limits(self):
        self.mock_hardware.set_lower_limit(NUNAME, None)
        self.mock_hardware.set_upper_limit('delta', 90)
        self.mock_hardware.set_lower_limit('mu', None)
        self.mock_hardware.set_lower_limit('eta', None)
        self.mock_hardware.set_lower_limit('chi', None)

    def _convert_willmott_pos(self, willmott_pos):
        return  willmott_to_you_fixed_mu_eta(willmott_pos)

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl('', 999, 999, hkl, pos, self.wavelength)
#                                  virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails('', 999, 999, hkl, pos,
                                            self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)

    def testHkl_2_19_32_found_orientation_setting(self):
        '''Check that the or0 reflection maps back to the assumed hkl'''
        self.places = 2
        self._check_angles_to_hkl('', 999, 999, HKL0,
                        self._convert_willmott_pos(REF0),
                        self.wavelength, {'alpha': 2})

    def testHkl_0_7_22_found_orientation_setting(self):
        '''Check that the or1 reflection maps back to the assumed hkl'''
        self.places = 0
        self._check_angles_to_hkl('', 999, 999, HKL1,
                        self._convert_willmott_pos(REF1),
                        self.wavelength, {'alpha': 2})

    def testHkl_2_19_32_calculated_from_DDIF(self):
        raise SkipTest()  # diffcalc finds a different soln (with -ve gamma)
        self.places = 3
        willpos = WillPos(delta=21.974, gamma=4.419, omegah=2, phi=-33.803)
        self._check((2, 19, 32),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})

    def testHkl_0_7_22_calculated_from_DDIF(self):
        raise SkipTest()  # diffcalc finds a different soln (with -ve gamma)
        self.places = 3
        willpos = WillPos(delta=11.241801854649, gamma=-3.038407637123,
                          omegah=2, phi=-3.436557497330)
        self._check((0, 7, 22),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})

    def testHkl_2_m5_12_calculated_from_DDIF(self):
        raise SkipTest()  # diffcalc finds a different soln (with -ve gamma)
        self.places = 3
        willpos = WillPos(delta=5.224, gamma=10.415, omegah=2, phi=-1.972)
        self._check((2, -5, 12),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})

    def testHkl_2_19_32_calculated_predicted_with_diffcalc_and_found(self):
        willpos = WillPos(delta=21.974032376045, gamma=-4.418955754003,
                          omegah=2, phi=64.027358409574)
        self._check((2, 19, 32),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})

    def testHkl_0_7_22_calculated_predicted_with_diffcalc_and_found(self):
        willpos = WillPos(delta=11.241801854649, gamma=-3.038407637123,
                          omegah=2, phi=-86.563442502670)
        self._check((0, 7, 22),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})

    def testHkl_2_m5_12_calculated_predicted_with_diffcalc_and_found(self):
        willpos = WillPos(delta=5.223972025344, gamma=-10.415435905622,
                          omegah=2, phi=-90 - 102.995854571805)
        self._check((2, -5, 12),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})


###############################################################################

def willmott_to_you_fixed_mu_chi(pos):
    pos = YouPos(mu=-0,
                       delta=pos.delta,
                       nu=pos.gamma,
                       eta=pos.omegah,
                       chi=90,
                       phi=-pos.phi)
    if pos.phi > 180:
        pos.phi -= 360
    elif pos.phi < -180:
        pos.phi += 360
    return pos


class TestUBCalculationWithWillmotStrategy_Si_5_5_12_FixedMuChi():

    def setUp(self):

        hardware = Mock()
        names = 'm', 'd', 'n', 'e', 'c', 'p'
        hardware.get_axes_names.return_value = names
        self.ubcalc = UBCalculation(hardware, SixCircle(),
                                    UbCalculationNonPersister(),
                                    YouUbCalcStrategy())

    def testAgainstResultsFromJan_27_2010(self):
        self.ubcalc.start_new('test')
        self.ubcalc.set_lattice('Si_5_5_12', 7.68, 53.48, 75.63, 90, 90, 90)
        self.ubcalc.add_reflection(
            HKL0[0], HKL0[1], HKL0[2], willmott_to_you_fixed_mu_chi(REF0),
            ENERGY, 'ref0', None)
        self.ubcalc.add_reflection(
            HKL1[0], HKL1[1], HKL1[2], willmott_to_you_fixed_mu_chi(REF1),
            ENERGY, 'ref1', None)
        self.ubcalc.calculate_UB()
        print "U: ", self.ubcalc.U
        print "UB: ", self.ubcalc.UB
        matrixeq_(self.ubcalc.U, U_DIFFCALC)


class Test_Fixed_Mu_Chi(TestFixedMuEta):

    def _configure_constraints(self):
        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu': 0,
                                         'chi': pi / 2}

    def _convert_willmott_pos(self, willmott_pos):
        return  willmott_to_you_fixed_mu_chi(willmott_pos)


# Primary and secondary reflections found with the help of DDIF on Diamond's
# i07 on Jan 28/29 2010


Pt531_HKL0 = -1.000, 1.000, 6.0000
Pt531_REF0 = WillPos(delta=9.3971025, gamma=-16.1812303, omegah=2,
                                  phi=108.5510712)

Pt531_HKL1 = -2.000, -1.000, 7.0000
Pt531_REF1 = WillPos(delta=11.0126958, gamma=-11.8636128, omegah=2,
                                  phi=40.3803393)
Pt531_HKL2 = 1, 1, 9
Pt531_REF2 = WillPos(delta=14.1881617, gamma=-7.7585939, omegah=2,
                                  phi=176.5348540)
Pt531_WAVELENGTH = 0.6358

# This is U matrix displayed by DDIF
U_FROM_DDIF = matrix([[-0.00312594, -0.00063417, 0.99999491],
                      [0.99999229, -0.00237817, 0.00312443],
                      [0.00237618, 0.99999697, 0.00064159]])

# This is the version that Diffcalc comes up with ( see following test)
Pt531_U_DIFFCALC = matrix([[-0.0023763, -0.9999970, -0.0006416],
                           [0.9999923, -0.0023783, 0.0031244],
                           [-0.0031259, -0.0006342, 0.9999949]])


class TestUBCalculationWithYouStrategy_Pt531_FixedMuChi():

    def setUp(self):

        hardware = Mock()
        names = 'm', 'd', 'n', 'e', 'c', 'p'
        hardware.get_axes_names.return_value = names
        self.ubcalc = UBCalculation(hardware, SixCircle(),
                                    UbCalculationNonPersister(),
                                    YouUbCalcStrategy())

    def testAgainstResultsFromJan_28_2010(self):
        self.ubcalc.start_new('test')
        self.ubcalc.set_lattice('Pt531', 6.204, 4.806, 23.215, 90, 90, 49.8)

        self.ubcalc.add_reflection(Pt531_HKL0[0], Pt531_HKL0[1], Pt531_HKL0[2],
                                  willmott_to_you_fixed_mu_chi(Pt531_REF0),
                                  12.39842 / Pt531_WAVELENGTH,
                                  'ref0', None)
        self.ubcalc.add_reflection(Pt531_HKL1[0], Pt531_HKL1[1], Pt531_HKL1[2],
                                  willmott_to_you_fixed_mu_chi(Pt531_REF1),
                                  12.39842 / Pt531_WAVELENGTH,
                                  'ref1', None)
        self.ubcalc.calculate_UB()
        print "U: ", self.ubcalc.U
        print "UB: ", self.ubcalc.UB
        matrixeq_(self.ubcalc.U, Pt531_U_DIFFCALC)


class Test_Pt531_FixedMuChi(_BaseTest):

    def setup(self):
        _BaseTest.setup(self)
        self._configure_constraints()
        self.wavelength = Pt531_WAVELENGTH
        CUT = CrystalUnderTest('Pt531', 6.204, 4.806, 23.215, 90, 90, 49.8)
        B = CUT.B
        self.UB = Pt531_U_DIFFCALC * B
        self._configure_limits()

    def _configure_constraints(self):
        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu': 0,
                                         'chi': pi / 2}

    def _configure_limits(self):
        self.mock_hardware.set_lower_limit(NUNAME, None)
        #self.mock_hardware.set_lower_limit('delta', None)
        self.mock_hardware.set_upper_limit('delta', 90)
        self.mock_hardware.set_lower_limit('mu', None)
        self.mock_hardware.set_lower_limit('eta', None)
        self.mock_hardware.set_lower_limit('chi', None)

    def _convert_willmott_pos(self, willmott_pos):
        return  willmott_to_you_fixed_mu_chi(willmott_pos)

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
#        self._check_angles_to_hkl('', 999, 999, hkl, pos, self.wavelength,
#                                  virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails('', 999, 999, hkl, pos,
                                            self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)

    def testHkl_0_found_orientation_setting(self):
        '''Check that the or0 reflection maps back to the assumed hkl'''
        self.places = 1
        self._check_angles_to_hkl('', 999, 999, Pt531_HKL0,
                        self._convert_willmott_pos(Pt531_REF0),
                        self.wavelength, {'alpha': 2})

    def testHkl_1_found_orientation_setting(self):
        '''Check that the or1 reflection maps back to the assumed hkl'''
        self.places = 0
        self._check_angles_to_hkl('', 999, 999, Pt531_HKL1,
                        self._convert_willmott_pos(Pt531_REF1),
                        self.wavelength, {'alpha': 2})

    def testHkl_0_calculated_from_DDIF(self):
        self.places = 7
        pos_expected = self._convert_willmott_pos(Pt531_REF0)
        self._check(Pt531_HKL0,
                    pos_expected,
                    {'alpha': 2})

    def testHkl_1_calculated_from_DDIF(self):
        self.places = 7
        self._check(Pt531_HKL1,
                    self._convert_willmott_pos(Pt531_REF1),
                    {'alpha': 2})

    def testHkl_2_calculated_from_DDIF(self):
        self.places = 7
        self._check(Pt531_HKL2,
                    self._convert_willmott_pos(Pt531_REF2),
                    {'alpha': 2})

    def testHkl_2_m1_0_16(self):
        self.places = 7
        pos = WillPos(delta=25.7990976, gamma=-6.2413545, omegah=2,
                                  phi=47.4624380)
#        pos.phi -= 360
        self._check((-1, 0, 16),
                    self._convert_willmott_pos(pos),
                    {'alpha': 2})


class Test_Pt531_Fixed_Mu_eta_(Test_Pt531_FixedMuChi):

    def _configure_constraints(self):
        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu': -pi / 2,
                                         'eta': 0}

    def _convert_willmott_pos(self, willmott_pos):
        return  willmott_to_you_fixed_mu_eta(willmott_pos)
