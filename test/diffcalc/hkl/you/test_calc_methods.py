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

import math
from math import pi, sin, cos
from nose.plugins.skip import SkipTest
from nose.tools import assert_almost_equal, raises, eq_  # @UnresolvedImport
from mock import Mock

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.hkl.you.calc import YouHklCalculator, I, \
    _calc_angle_between_naz_and_qaz, merge_nearly_equal_pairs
from test.tools import  assert_matrix_almost_equal, \
    assert_2darray_almost_equal, aneq_
from diffcalc.hkl.you.geometry  import YouPosition
from test.diffcalc.hkl.vlieg.test_calc import \
    createMockDiffractometerGeometry, createMockHardwareMonitor, \
    createMockUbcalc
from test.diffcalc.test_hardware import SimpleHardwareAdapter
from diffcalc.util import DiffcalcException

from diffcalc.hkl.you.constraints import NUNAME

TORAD = pi / 180
TODEG = 180 / pi

x = matrix('1; 0; 0')
y = matrix('0; 1; 0')
z = matrix('0; 0; 1')


def isnan(n):
    # math.isnan was introduced only in python 2.6 and is not in Jython (2.5.2)
    try:
        return math.isnan(n)
    except AttributeError:
        return n != n  # for Jython


class Test_anglesToVirtualAngles():

    def setup(self):
        constraints = Mock()
        constraints.is_fully_constrained.return_value = True
        self.calc = YouHklCalculator(createMockUbcalc(None),
                                     createMockDiffractometerGeometry(),
                                     createMockHardwareMonitor(),
                                     constraints)

    def check_angle(self, name, expected, mu=-99, delta=99, nu=99,
                     eta=99, chi=99, phi=99):
        """All in degrees"""
        pos = YouPosition(mu, delta, nu, eta, chi, phi)
        pos.changeToRadians()
        calculated = self.calc._anglesToVirtualAngles(pos, None)[name] * TODEG
        assert_almost_equal(calculated, expected)

    # theta

    def test_theta0(self):
        self.check_angle('theta', 0, delta=0, nu=0)

    def test_theta1(self):
        self.check_angle('theta', 1, delta=2, nu=0)

    def test_theta2(self):
        self.check_angle('theta', 1, delta=0, nu=2)

    def test_theta3(self):
        self.check_angle('theta', 1, delta=-2, nu=0)

    def test_theta4(self):
        self.check_angle('theta', 1, delta=0, nu=-2)

    # qaz

    def test_qaz0_degenerate_case(self):
        self.check_angle('qaz', 0, delta=0, nu=0)

    def test_qaz1(self):
        self.check_angle('qaz', 90, delta=2, nu=0)

    def test_qaz2(self):
        self.check_angle('qaz', 90, delta=90, nu=0)

    def test_qaz3(self):
        self.check_angle('qaz', 0, delta=0, nu=1,)

    # Can't see one by eye
    # def test_qaz4(self):
    #    pos = YouPosition(delta=20*TORAD, nu=20*TORAD)#.inRadians()
    #    assert_almost_equal(
    #        self.calc._anglesToVirtualAngles(pos, None)['qaz']*TODEG, 45)

    #alpha
    def test_defaultReferenceValue(self):
        # The following tests depemd on this
        assert_matrix_almost_equal(self.calc._ubcalc.reference.n_phi, matrix([[0], [0], [1]]))

    def test_alpha0(self):
        self.check_angle('alpha', 0, mu=0, eta=0, chi=0, phi=0)

    def test_alpha1(self):
        self.check_angle('alpha', 0, mu=0, eta=0, chi=0, phi=10)

    def test_alpha2(self):
        self.check_angle('alpha', 0, mu=0, eta=0, chi=0, phi=-10)

    def test_alpha3(self):
        self.check_angle('alpha', 2, mu=2, eta=0, chi=0, phi=0)

    def test_alpha4(self):
        self.check_angle('alpha', -2, mu=-2, eta=0, chi=0, phi=0)

    def test_alpha5(self):
        self.check_angle('alpha', 2, mu=0, eta=90, chi=2, phi=0)

    #beta

    def test_beta0(self):
        self.check_angle('beta', 0, delta=0, nu=0, mu=0, eta=0, chi=0, phi=0)

    def test_beta1(self):
        self.check_angle('beta', 0, delta=10, nu=0, mu=0, eta=6, chi=0, phi=5)

    def test_beta2(self):
        self.check_angle('beta', 10, delta=0, nu=10, mu=0, eta=0, chi=0, phi=0)

    def test_beta3(self):
        self.check_angle('beta', -10, delta=0, nu=-10, mu=0, eta=0, chi=0,
                         phi=0)

    def test_beta4(self):
        self.check_angle('beta', 5, delta=0, nu=10, mu=5, eta=0, chi=0, phi=0)

    # azimuth
    def test_naz0(self):
        self.check_angle('naz', 0, mu=0, eta=0, chi=0, phi=0)

    def test_naz1(self):
        self.check_angle('naz', 0, mu=0, eta=0, chi=0, phi=10)

    def test_naz3(self):
        self.check_angle('naz', 0, mu=10, eta=0, chi=0, phi=10)

    def test_naz4(self):
        self.check_angle('naz', 2, mu=0, eta=0, chi=2, phi=0)

    def test_naz5(self):
        self.check_angle('naz', -2, mu=0, eta=0, chi=-2, phi=0)

    #tau
    def test_tau0(self):
        self.check_angle('tau', 0, mu=0, delta=0, nu=0, eta=0, chi=0, phi=0)
        #self.check_angle('tau_from_dot_product', 90, mu=0, delta=0,
        #nu=0, eta=0, chi=0, phi=0)

    def test_tau1(self):
        self.check_angle('tau', 90, mu=0, delta=20, nu=0, eta=10, chi=0, phi=0)
        #self.check_angle('tau_from_dot_product', 90, mu=0, delta=20,
        #nu=0, eta=10, chi=0, phi=0)

    def test_tau2(self):
        self.check_angle('tau', 90, mu=0, delta=20, nu=0, eta=10, chi=0, phi=3)
        #self.check_angle('tau_from_dot_product', 90, mu=0, delta=20,
        #nu=0, eta=10, chi=0, phi=3)

    def test_tau3(self):
        self.check_angle('tau', 88, mu=0, delta=20, nu=0, eta=10, chi=2, phi=0)
        #self.check_angle('tau_from_dot_product', 88, mu=0, delta=20,
        #nu=0, eta=10, chi=2, phi=0)

    def test_tau4(self):
        self.check_angle('tau', 92, mu=0, delta=20, nu=0, eta=10, chi=-2,
                         phi=0)
        #self.check_angle('tau_from_dot_product', 92, mu=0, delta=20,
        #nu=0, eta=10, chi=-2, phi=0)

    def test_tau5(self):
        self.check_angle('tau', 10, mu=0, delta=0, nu=20, eta=0, chi=0, phi=0)
        #self.check_angle('tau_from_dot_product', 10, mu=0, delta=0,
        #nu=20, eta=0, chi=0, phi=0)

    #psi

    def test_psi0(self):
        pos = YouPosition(0, 0, 0, 0, 0, 0)
        assert isnan(self.calc._anglesToVirtualAngles(pos, None)['psi'])

    def test_psi1(self):
        self.check_angle('psi', 90, mu=0, delta=11, nu=0, eta=0, chi=0, phi=0)

    def test_psi2(self):
        self.check_angle(
            'psi', 100, mu=10, delta=.00000001, nu=0, eta=0, chi=0, phi=0)

    def test_psi3(self):
        self.check_angle(
            'psi', 80, mu=-10, delta=.00000001, nu=0, eta=0, chi=0, phi=0)

    def test_psi4(self):
        self.check_angle(
            'psi', 90, mu=0, delta=11, nu=0, eta=0, chi=0, phi=12.3)

    def test_psi5(self):
        #self.check_angle('psi', 0, mu=10, delta=.00000001,
        #nu=0, eta=0, chi=90, phi=0)
        pos = YouPosition(0, .00000001, 0, 0, 90, 0)
        pos.changeToRadians()
        assert isnan(self.calc._anglesToVirtualAngles(pos, None)['psi'])

    def test_psi6(self):
        self.check_angle(
            'psi', 90, mu=0, delta=0.00000001, nu=0, eta=90, chi=0, phi=0)

    def test_psi7(self):
        self.check_angle(
            'psi', 92, mu=0, delta=0.00000001, nu=0, eta=90, chi=2, phi=0)

    def test_psi8(self):
        self.check_angle(
            'psi', 88, mu=0, delta=0.00000001, nu=0, eta=90, chi=-2, phi=0)


class Test_calc_theta():

    def setup(self):
        self.calc = YouHklCalculator(createMockUbcalc(I * 2 * pi),
                                     createMockDiffractometerGeometry(),
                                     createMockHardwareMonitor(),
                                     Mock())
        self.e = 12.398420  # 1 Angstrom

    def test_100(self):
        h_phi = matrix([[1], [0], [0]])
        assert_almost_equal(self.calc._calc_theta(h_phi * 2 * pi, 1) * TODEG,
                            30)

    @raises(DiffcalcException)
    def test_too_short(self):
        h_phi = matrix([[1], [0], [0]])
        self.calc._calc_theta(h_phi * 0, 1)

    @raises(DiffcalcException)
    def test_too_long(self):
        h_phi = matrix([[1], [0], [0]])
        self.calc._calc_theta(h_phi * 2 * pi, 10)


class Test_calc_remaining_reference_angles_given_one():

    # TODO: These are very incomplete due to either totally failing inutuition
    #       or code!
    def setup(self):
        self.calc = YouHklCalculator(createMockUbcalc(None),
                                     createMockDiffractometerGeometry(),
                                     createMockHardwareMonitor(),
                                     Mock())

    def check(self, name, value, theta, tau, psi_e, alpha_e, beta_e):
        # all in deg
        psi, alpha, beta = self.calc._calc_remaining_reference_angles(
            name, value * TORAD, theta * TORAD, tau * TORAD)
        print 'psi', psi * TODEG, ' alpha:', alpha * TODEG,\
              ' beta:', beta * TODEG
        if psi_e is not None:
            assert_almost_equal(psi * TODEG, psi_e)
        if alpha_e is not None:
            assert_almost_equal(alpha * TODEG, alpha_e)
        if beta_e is not None:
            assert_almost_equal(beta * TODEG, beta_e)

    def test_psi_given0(self):
        self.check('psi', 90, theta=10, tau=90, psi_e=90,
                    alpha_e=0, beta_e=0)

    def test_psi_given1(self):
        self.check('psi', 92, theta=0, tau=90, psi_e=92,
                    alpha_e=2, beta_e=-2)

    def test_psi_given3(self):
        self.check('psi', 88, theta=0, tau=90, psi_e=88,
                    alpha_e=-2, beta_e=2)

    def test_psi_given4(self):
        self.check('psi', 0, theta=0, tau=90, psi_e=0,
                    alpha_e=-90, beta_e=90)

    def test_psi_given4a(self):
        self.check('psi', 180, theta=0, tau=90, psi_e=180,
                    alpha_e=90, beta_e=-90)

    def test_psi_given5(self):
        raise SkipTest
        # TODO: I don't understand why this one passes!
        self.check('psi', 180, theta=0, tau=80,
                   psi_e=180, alpha_e=80, beta_e=-80)
        self.check('psi', 180, theta=0, tau=80,
                   psi_e=180, alpha_e=90, beta_e=-90)

    def test_a_eq_b0(self):
        self.check('a_eq_b', 9999, theta=0, tau=90,
                   psi_e=90, alpha_e=0, beta_e=0)

    def test_alpha_given(self):
        self.check('alpha', 2, theta=0, tau=90,
                   psi_e=92, alpha_e=2, beta_e=-2)

    def test_beta_given(self):
        self.check('beta', 2, theta=0, tau=90,
                   psi_e=88, alpha_e=-2, beta_e=2)
#    def test_a_eq_b1(self):
#        self.check('a_eq_b', 9999, theta=20, tau=90,
#                   psi_e=90, alpha_e=10, beta_e=10)

#    def test_psi_given0(self):
#        self.check('psi', 90, theta=10, tau=45, psi_e=90,
#                    alpha_e=7.0530221302831952, beta_e=7.0530221302831952)
    
    def test_merge_nearly_equal_detector_angle_pairs_different(self):
        pairs = [(1,2), (1,2.1)]
        assert_2darray_almost_equal(
            merge_nearly_equal_pairs(pairs), pairs)

    def test_merge_nearly_equal_detector_angle_pairs_1(self):
        pairs = [(1, 2), (1, 2)]
        assert_2darray_almost_equal(
            merge_nearly_equal_pairs(pairs), [(1, 2)])

    def test_merge_nearly_equal_detector_angle_pairs_2(self):
        pairs = [(1, 2), (1, 2), (1, 2)]
        assert_2darray_almost_equal(
            merge_nearly_equal_pairs(pairs), [(1, 2)])

    def test_merge_nearly_equal_detector_angle_pairs_3(self):
        pairs = [(1, 2.2), (1, 2), (1, 2), (1, 2)]
        assert_2darray_almost_equal(
            merge_nearly_equal_pairs(pairs), [(1, 2.2), (1, 2)])

    def test_merge_nearly_equal_detector_angle_pairs_4(self):
        pairs = [(1, 2.2), (1, 2), (1, 2), (1, 2.2)]
        assert_2darray_almost_equal(
            merge_nearly_equal_pairs(pairs), [(1, 2.2), (1, 2)])

class Test_calc_detector_angles_given_one():

    def setup(self):
        self.calc = YouHklCalculator(createMockUbcalc(None),
                                     createMockDiffractometerGeometry(),
                                     createMockHardwareMonitor(),
                                     Mock())

    def check(self, name, value, theta, delta_e, nu_e, qaz_e):
        # all in deg
        delta, nu, qaz = self.calc._calc_remaining_detector_angles(
            name, value * TORAD, theta * TORAD)
        assert_almost_equal(delta * TODEG, delta_e)
        assert_almost_equal(nu * TODEG, nu_e)
        if qaz_e is not None:
            assert_almost_equal(qaz * TODEG, qaz_e)

    def test_nu_given0(self):
        self.check(NUNAME, 0, theta=3, delta_e=6, nu_e=0, qaz_e=90)

    def test_nu_given1(self):
        self.check(NUNAME, 10, theta=7.0530221302831952,
                   delta_e=10, nu_e=10, qaz_e=None)

    def test_nu_given2(self):
        self.check(NUNAME, 6, theta=3, delta_e=0, nu_e=6, qaz_e=0)

    def test_delta_given0(self):
        self.check('delta', 0, theta=3, delta_e=0, nu_e=6, qaz_e=0)

    def test_delta_given1(self):
        self.check('delta', 10, theta=7.0530221302831952,
                   delta_e=10, nu_e=10, qaz_e=None)

    def test_delta_given2(self):
        self.check('delta', 6, theta=3, delta_e=6, nu_e=0, qaz_e=90)

    def test_qaz_given0(self):
        self.check('qaz', 90, theta=3, delta_e=6, nu_e=0, qaz_e=90)

    def test_qaz_given2(self):
        self.check('qaz', 0, theta=3, delta_e=0, nu_e=6, qaz_e=0)


class Test_calc_angle_between_naz_and_qaz():

    def test1(self):
        diff = _calc_angle_between_naz_and_qaz(
            theta=0, alpha=0, tau=90 * TORAD)
        assert_almost_equal(diff * TODEG, 90)

    def test2(self):
        diff = _calc_angle_between_naz_and_qaz(
            theta=0 * TORAD, alpha=0, tau=80 * TORAD)
        assert_almost_equal(diff * TODEG, 80)


class Test_calc_remaining_sample_angles_given_one():
    #_calc_remaining_detector_angles_given_one
    def setup(self):
        self.calc = YouHklCalculator(createMockUbcalc(None),
                                     createMockDiffractometerGeometry(),
                                     createMockHardwareMonitor(),
                                     Mock())

    def check(self, name, value, Q_lab, n_lab, Q_phi, n_phi,
              phi_e, chi_e, eta_e, mu_e):
        phi, chi, eta, mu = self.calc._calc_remaining_sample_angles(
                            name, value * TORAD, Q_lab, n_lab, Q_phi, n_phi)
        print 'phi', phi * TODEG, ' chi:', chi * TODEG, ' eta:', eta * TODEG,\
              ' mu:', mu * TODEG
        if phi_e is not None:
            assert_almost_equal(phi * TODEG, phi_e)
        if chi_e is not None:
            assert_almost_equal(chi * TODEG, chi_e)
        if eta_e is not None:
            assert_almost_equal(eta * TODEG, eta_e)
        if mu_e is not None:
            assert_almost_equal(mu * TODEG, mu_e)

    @raises(ValueError)
    def test_constrain_xx_degenerate(self):
        self.check('mu', 0, Q_lab=x, n_lab=x, Q_phi=x, n_phi=x,
                    phi_e=0, chi_e=0, eta_e=0, mu_e=0)

    def test_constrain_mu_0(self):
        raise SkipTest()
        self.check('mu', 0, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=0, chi_e=0, eta_e=0, mu_e=0)

    def test_constrain_mu_10(self):
        raise SkipTest()
        self.check('mu', 10, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=-90, chi_e=10, eta_e=-90, mu_e=10)

    def test_constrain_mu_n10(self):
        raise SkipTest()
        self.check('mu', -10, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=90, chi_e=10, eta_e=90, mu_e=-10)

    def test_constrain_eta_10_wasfailing(self):
        # Required the choice of a different equation
        self.check('eta', 10, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=-10, chi_e=0, eta_e=10, mu_e=0)

    def test_constrain_eta_n10(self):
        self.check('eta', -10, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=10, chi_e=0, eta_e=-10, mu_e=0)

    def test_constrain_eta_20_with_theta_20(self):
        theta = 20 * TORAD
        Q_lab = matrix([[cos(theta)], [-sin(theta)], [0]])
        self.check('eta', 20, Q_lab=Q_lab, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=0, chi_e=0, eta_e=20, mu_e=0)

    @raises(ValueError)
    def test_constrain_chi_0_degenerate(self):
        self.check('chi', 0, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=0, chi_e=0, eta_e=0, mu_e=0)

    def test_constrain_chi_10(self):
        self.check('chi', 10, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=-90, chi_e=10, eta_e=90, mu_e=-10)

    def test_constrain_chi_90(self):
        # mu is off by 180, but youcalc tries +-x and 180+-x anyway
        raise SkipTest()
        self.check('chi', 90, Q_lab=z * (-1), n_lab=x, Q_phi=x, n_phi=z,
                    phi_e=0, chi_e=90, eta_e=0, mu_e=0)

    def test_constrain_phi_0(self):
        self.check('phi', 0, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=0, chi_e=0, eta_e=0, mu_e=0)

    def test_constrain_phi_10(self):
        self.check('phi', 10, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=10, chi_e=0, eta_e=-10, mu_e=0)

    def test_constrain_phi_n10(self):
        self.check('phi', -10, Q_lab=x, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=-10, chi_e=0, eta_e=10, mu_e=0)

    def test_constrain_phi_20_with_theta_20(self):
        theta = 20 * TORAD
        Q_lab = matrix([[cos(theta)], [-sin(theta)], [0]])
        self.check('phi', 20, Q_lab=Q_lab, n_lab=z, Q_phi=x, n_phi=z,
                    phi_e=20, chi_e=0, eta_e=0, mu_e=0)


class TestSolutionGenerator():
    def setup(self):

        names = ['delta', NUNAME, 'mu', 'eta', 'chi', 'phi']
        self.hardware = SimpleHardwareAdapter(names)
        self.calc = YouHklCalculator(createMockUbcalc(None),
                                     createMockDiffractometerGeometry(),
                                     self.hardware,
                                     Mock())

    # constraint could have been 'delta', NUNAME, 'qaz' or 'naz'.

    def test_generate_possible_det_soln_no_limits_constrained_qaz_or_naz(self):
        # we will enfoce the order too, incase this later effects heuristically
        # made choices
        expected = (
                    (.1, .2),
                    (.1, -.2),
                    (.1, .2 - pi),
                    (.1, pi - .2),
                    (-.1, .2),
                    (-.1, -.2),
                    (-.1, .2 - pi),
                    (-.1, pi - .2),
                    (.1 - pi, .2),  # pi + x cuts to x-pi
                    (.1 - pi, -.2),
                    (.1 - pi, .2 - pi),
                    (.1 - pi, pi - .2),
                    (pi - .1, .2),
                    (pi - .1, -.2),
                    (pi - .1, .2 - pi),
                    (pi - .1, pi - .2),
                   )

        assert_2darray_almost_equal(expected,
            self.calc._generate_possible_solutions(
                (.1, .2), ('delta', NUNAME), ('naz',)))
        assert_2darray_almost_equal(expected,
            self.calc._generate_possible_solutions(
                (.1, .2), ('delta', NUNAME), ('qaz',)))

    def test_generate_poss_det_soln_no_lim_cons_qaz_or_naz_delta_and_nu_at_zro(self):  # @IgnorePep8
        # we will enfoce the order too, incase this later effects hearistically
        # made choices
        expected = (
                    (0., 0,),
                    (0., pi),
                    (pi, 0.),
                    (pi, pi)
                    )

        assert_2darray_almost_equal(expected,
            self.calc._generate_possible_solutions(
                (-2e-9, 2e-9), ('delta', NUNAME), ('naz',)))
        assert_2darray_almost_equal(expected,
            self.calc._generate_possible_solutions(
                (-2e-9, 2e-9), ('delta', NUNAME), ('qaz',)))

    def test_generate_possible_det_solutions_no_limits_constrained_delta(self):
        expected = (
                    (.1, .2),
                    (.1, -.2),
                    (.1, .2 - pi),
                    (.1, pi - .2),
                   )

        assert_2darray_almost_equal(expected,
                self.calc._generate_possible_solutions(
                    (.1, .2), ('delta', NUNAME), ('delta',)))

    def test_generate_possible_det_solutions_no_limits_constrained_nu(self):
        expected = (
                    (.1, .2),
                    (-.1, .2),
                    (.1 - pi, .2),
                    (pi - .1, .2),
                   )

        assert_2darray_almost_equal(expected,
            self.calc._generate_possible_solutions(
                (.1, .2), ('delta', NUNAME), (NUNAME,)))

    def test_generate_possible_det_soln_with_limits_constrained_delta(self):
        self.hardware.set_lower_limit(NUNAME, 0)
        expected = (
                    (.1, .2),
                    (.1, pi - .2),
                   )

        assert_2darray_almost_equal(expected,
            self.calc._generate_possible_solutions(
                (.1, .2), ('delta', NUNAME), ('delta',)))

    def test_generate_possible_det_solutions_with_limits_constrained_nu(self):
        self.hardware.set_upper_limit('delta', 0)
        expected = (
                    (-.1, .2),
                    (.1 - pi, .2),  # cuts to .1-pi
                   )

        assert_2darray_almost_equal(expected,
            self.calc._generate_possible_solutions(
                (.1, .2), ('delta', NUNAME), (NUNAME,)))

    def test_generate_poss_det_soln_with_limits_overly_constrained_nu(self):
        self.hardware.set_lower_limit('delta', .3)
        self.hardware.set_upper_limit('delta', .31)
        eq_(len(self.calc._generate_possible_solutions(
            (.1, .2), ('delta', NUNAME), (NUNAME,))), 0)

    def test_generate_possible_sample_solutions(self):
        result = self.calc._generate_possible_solutions(
            (.1, .2, .3, .4), ('mu', 'eta', 'chi', 'phi'), ('naz',))
        generated = self._hardcoded_generate_possible_sample_solutions(
            .1, .2, .3, .4, 'naz')
        assert_2darray_almost_equal(generated, result)
        eq_(4 ** 4, len(result))

    def test_generate_possible_sample_solutions_fixed_chi(self):
        result = self.calc._generate_possible_solutions(
            (.1, .2, .3, .4), ('mu', 'eta', 'chi', 'phi'), ('chi',))
        generated = self._hardcoded_generate_possible_sample_solutions(
            .1, .2, .3, .4, 'chi')
        assert_2darray_almost_equal(generated, result)
        eq_(4 ** 3, len(result))

    def test_generate_possible_sample_solutions_fixed_chi_positive_mu(self):
        self.hardware.set_lower_limit('mu', 0)
        result = self.calc._generate_possible_solutions(
            (.1, .2, .3, .4), ('mu', 'eta', 'chi', 'phi'), ('chi',))
        generated = self._hardcoded_generate_possible_sample_solutions(
            .1, .2, .3, .4, 'chi')
        assert_2darray_almost_equal(generated, result)
        eq_(2 * (4 ** 2), len(result))

    def _hardcoded_generate_possible_sample_solutions(self, mu, eta, chi, phi,
                                                      sample_constraint_name):
        possible_solutions = []
        _identity = lambda x: x
        _transforms = (_identity,
                      lambda x: -x,
                      lambda x: pi + x,
                      lambda x: pi - x)
        _transforms_for_zero = (lambda x: 0.,
                               lambda x: pi,)
        SMALL = 1e-8

        def cut_at_minus_pi(value):
            if value < (-pi - SMALL):
                return value + 2 * pi
            if value >= pi + SMALL:
                return value - 2 * pi
            return value

        def is_small(x):
            return abs(x) < SMALL

        name = sample_constraint_name

        for transform in ((_identity,) if name == 'mu' else
                           _transforms if not is_small(mu) else
                           _transforms_for_zero):
            transformed_mu = (transform(mu))
            if not self.hardware.is_axis_value_within_limits('mu',
                    self.hardware.cut_angle('mu', transformed_mu * TODEG)):
                continue
            for transform in ((_identity,) if name == 'eta' else
                               _transforms if not is_small(eta) else
                               _transforms_for_zero):
                transformed_eta = transform(eta)
                if not self.hardware.is_axis_value_within_limits('eta',
                    self.hardware.cut_angle('eta', transformed_eta * TODEG)):
                    continue
                for transform in ((_identity,) if name == 'chi' else
                                   _transforms if not is_small(chi) else
                                   _transforms_for_zero):
                    transformed_chi = transform(chi)
                    if not self.hardware.is_axis_value_within_limits('chi',
                        self.hardware.cut_angle('chi',
                                               transformed_chi * TODEG)):
                        continue
                    for transform in ((_identity,) if name == 'phi' else
                                       _transforms if not is_small(phi) else
                                       _transforms_for_zero):
                        transformed_phi = transform(phi)
                        if not self.hardware.is_axis_value_within_limits('phi',
                            self.hardware.cut_angle('phi',
                                                   transformed_phi * TODEG)):
                            continue
                        possible_solutions.append((
                            cut_at_minus_pi(transformed_mu),
                            cut_at_minus_pi(transformed_eta),
                            cut_at_minus_pi(transformed_chi),
                            cut_at_minus_pi(transformed_phi)))
        return possible_solutions
