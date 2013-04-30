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


from nose.tools import eq_  # @UnresolvedImport
from mock import Mock

from diffcalc.hkl.you.constraints import YouConstraintManager
from diffcalc.util import DiffcalcException
from nose.tools import raises
from nose.tools import assert_raises  # @UnresolvedImport

from diffcalc.hkl.you.constraints import NUNAME

def joined(d1, d2):
    d1.update(d2)
    return d1


class TestConstraintManager:

    def setUp(self):
        self.hardware_monitor = Mock()
        self.hardware_monitor.get_position.return_value = (1.,) * 6
        self.hardware_monitor.get_axes_names.return_value = [
                                      'mu', 'delta', NUNAME, 'eta', 'chi', 'phi']
        self.cm = YouConstraintManager(self.hardware_monitor)

    def test_init(self):
        eq_(self.cm.all, {})
        eq_(self.cm.detector, {})
        eq_(self.cm.reference, {})
        eq_(self.cm.sample, {})
        eq_(self.cm.naz, {})

    def test_build_display_table(self):
        self.cm.constrain('qaz')
        self.cm.constrain('alpha')
        self.cm.constrain('eta')
        self.cm.set_constraint('qaz', 1.234)
        self.cm.set_constraint('eta', 99.)
        print self.cm.build_display_table_lines()
        eq_(self.cm.build_display_table_lines(),
            ['    DET        REF        SAMP',
             '    ======     ======     ======',
             '    delta      a_eq_b     mu',
             '    %s o-> alpha  --> eta' % NUNAME.ljust(6),
             '--> qaz        beta       chi',
             '    naz        psi        phi',
             '                          mu_is_%s' % NUNAME])


#"""
#    DET        REF        SAMP                  Available:
#    ======     ======     ======
#    delta      a_eq_b     mu                    3x samp:         80 of 80
#    nu     o-> alpha  --> eta                   2x samp and ref: chi & phi
#--> qaz        beta       chi                                    mu & eta
#    naz        psi        phi                                    chi=90 & mu=0
#                          mu_is_nu              2x samp and det: 0 of 6
#                                                3x samp:         0 of 4
#"""[1:-1]

    def test_unconstrain_okay(self):
        eq_(self.cm.all, {})
        self.cm.constrain('delta')
        self.cm.constrain('mu')
        eq_(self.cm.all, {'delta': None, 'mu': None})
        eq_(self.cm.unconstrain('delta'), None)
        eq_(self.cm.all, {'mu': None})
        
    def test_clear_constraints(self):
        self.cm.constrain('delta')
        self.cm.constrain('mu')
        self.cm.clear_constraints()
        eq_(self.cm.all, {})

    def test_unconstrain_bad(self):
        eq_(self.cm.all, {})
        eq_(self.cm.unconstrain('delta'), "Delta was not already constrained.")

    def test_constrain_det(self, pre={}):
        eq_(self.cm.all, pre)
        eq_(self.cm.constrain('delta'), None)
        eq_(self.cm.all, joined({'delta': None}, pre))
        eq_(self.cm.constrain('delta'), 'Delta is already constrained.')
        eq_(self.cm.all, joined({'delta': None}, pre))
        eq_(self.cm.constrain('naz'), 'Delta constraint replaced.')
        eq_(self.cm.all, joined({'naz': None}, pre))
        eq_(self.cm.constrain('delta'), 'Naz constraint replaced.')
        eq_(self.cm.all, joined({'delta': None}, pre))

    def test_constrain_det_one_preexisting_ref(self):
        self.cm.constrain('alpha')
        self.test_constrain_det({'alpha': None})

    def test_constrain_det_one_preexisting_samp(self):
        self.cm.constrain('phi')
        self.test_constrain_det({'phi': None})

    def test_constrain_det_one_preexisting_samp_and_ref(self):
        self.cm.constrain('alpha')
        self.cm.constrain('phi')
        self.test_constrain_det({'alpha': None, 'phi': None})

    def test_constrain_det_two_preexisting_samp(self):
        self.cm.constrain('chi')
        self.cm.constrain('phi')
        self.test_constrain_det({'chi': None, 'phi': None})

    def test_constrain_det_three_preexisting_other(self):
        self.cm.constrain('alpha')
        self.cm.constrain('phi')
        self.cm.constrain('chi')
        try:
            self.cm.constrain('delta')
            assert False
        except DiffcalcException, e:
            eq_(e.args[0], (
                "Delta could not be constrained. First un-constrain one of the"
                "\nangles alpha, chi or phi (with 'uncon')"))

    def test_constrain_det_three_preexisting_samp(self):
        self.cm.constrain('phi')
        self.cm.constrain('chi')
        self.cm.constrain('eta')
        try:
            self.cm.constrain('delta')
            assert False
        except DiffcalcException, e:
            eq_(e.args[0],
                "Delta could not be constrained. First un-constrain one of the"
                "\nangles eta, chi or phi (with 'uncon')")

    def test_constrain_ref(self, pre={}):
        eq_(self.cm.all, pre)
        eq_(self.cm.constrain('alpha'), None)
        eq_(self.cm.all, joined({'alpha': None}, pre))
        eq_(self.cm.constrain('alpha'), 'Alpha is already constrained.')
        eq_(self.cm.all, joined({'alpha': None}, pre))
        eq_(self.cm.constrain('beta'), 'Alpha constraint replaced.')
        eq_(self.cm.all, joined({'beta': None}, pre))

    def test_constrain_ref_one_preexisting_det(self):
        self.cm.constrain('delta')
        self.test_constrain_ref({'delta': None})

    def test_constrain_ref_one_preexisting_samp(self):
        self.cm.constrain('phi')
        self.test_constrain_ref({'phi': None})

    def test_constrain_ref_one_preexisting_samp_and_det(self):
        self.cm.constrain('delta')
        self.cm.constrain('phi')
        self.test_constrain_ref({'delta': None, 'phi': None})

    def test_constrain_ref_two_preexisting_samp(self):
        self.cm.constrain('chi')
        self.cm.constrain('phi')
        self.test_constrain_ref({'chi': None, 'phi': None})

    def test_constrain_ref_three_preexisting_other(self):
        self.cm.constrain('delta')
        self.cm.constrain('phi')
        self.cm.constrain('chi')
        try:
            self.cm.constrain('alpha'),
            assert False
        except DiffcalcException, e:
            eq_(e.args[0],
                "Alpha could not be constrained. First un-constrain one of the"
                "\nangles delta, chi or phi (with 'uncon')")

    def test_constrain_ref_three_preexisting_samp(self):
        self.cm.constrain('phi')
        self.cm.constrain('chi')
        self.cm.constrain('eta')
        try:
            self.cm.constrain('delta')
            assert False
        except DiffcalcException, e:
            eq_(e.args[0],
                "Delta could not be constrained. First un-constrain one of the"
                "\nangles eta, chi or phi (with 'uncon')")

    def test_constrain_samp_when_one_free(self, pre={}):
        eq_(self.cm.all, pre)
        eq_(self.cm.constrain('phi'), None)
        eq_(self.cm.all, joined({'phi': None}, pre))
        eq_(self.cm.constrain('phi'), 'Phi is already constrained.')
        eq_(self.cm.all, joined({'phi': None}, pre))

    def test_constrain_samp_one_preexisting_samp(self):
        self.cm.constrain('chi')
        self.test_constrain_samp_when_one_free({'chi': None})

    def test_constrain_samp_two_preexisting_samp(self):
        self.cm.constrain('chi')
        self.cm.constrain('eta')
        self.test_constrain_samp_when_one_free({'chi': None, 'eta': None})

    def test_constrain_samp_two_preexisting_other(self):
        self.cm.constrain('delta')
        self.cm.constrain('alpha')
        self.test_constrain_samp_when_one_free({'delta': None, 'alpha': None})

    def test_constrain_samp_two_preexisting_one_det(self):
        self.cm.constrain('delta')
        self.cm.constrain('eta')
        self.test_constrain_samp_when_one_free({'delta': None, 'eta': None})

    def test_constrain_samp_two_preexisting_one_ref(self):
        self.cm.constrain('alpha')
        self.cm.constrain('eta')
        self.test_constrain_samp_when_one_free({'alpha': None, 'eta': None})

    def test_constrain_samp_three_preexisting_only_one_samp(self):
        self.cm.constrain('delta')
        self.cm.constrain('alpha')
        self.cm.constrain('eta')
        eq_(self.cm.constrain('phi'), 'Eta constraint replaced.')
        eq_(self.cm.all, {'delta': None, 'alpha': None, 'phi': None})
        eq_(self.cm.constrain('phi'), 'Phi is already constrained.')
        eq_(self.cm.all, {'delta': None, 'alpha': None, 'phi': None})

    def test_constrain_samp_three_preexisting_two_samp_one_det(self):
        self.cm.constrain('delta')
        self.cm.constrain('eta')
        self.cm.constrain('chi')
        try:
            self.cm.constrain('phi')
            assert False
        except DiffcalcException, e:
            eq_(e.args[0],
                "Phi could not be constrained. First un-constrain one of the"
                "\nangles delta, eta or chi (with 'uncon')")

    def test_constrain_samp_three_preexisting_two_samp_one_ref(self):
        self.cm.constrain('alpha')
        self.cm.constrain('eta')
        self.cm.constrain('chi')
        try:
            self.cm.constrain('phi')
            assert False
        except DiffcalcException, e:
            eq_(e.args[0],
                "Phi could not be constrained. First un-constrain one of the"
                "\nangles alpha, eta or chi (with 'uncon')")

    def test_constrain_samp_three_preexisting_samp(self):
        self.cm.constrain('mu')
        self.cm.constrain('eta')
        self.cm.constrain('chi')
        try:
            self.cm.constrain('phi')
            assert False
        except DiffcalcException, e:
            eq_(e.args[0],
                "Phi could not be constrained. First un-constrain one of the"
                "\nangles mu, eta or chi (with 'uncon')")

    def test_report_constraints_none(self):
        eq_(self.cm.report_constraints_lines(),
            ['!   3 more constraints required'])

    def test_report_constraints_one_with_value(self):
        self.cm.constrain(NUNAME)
        self.cm.set_constraint(NUNAME, 9.12343)
        eq_(self.cm.report_constraints_lines(),
            ['!   2 more constraints required',
             '    %s: 9.1234' % NUNAME])

    def test_report_constraints_one_with_novalue(self):
        self.cm.constrain(NUNAME)
        eq_(self.cm.report_constraints_lines(),
            ['!   2 more constraints required',
             '!   %s: ---' % NUNAME])

    def test_report_constraints_one_with_valueless(self):
        self.cm.constrain('a_eq_b')
        eq_(self.cm.report_constraints_lines(),
            ['!   2 more constraints required',
             '    a_eq_b'])

    def test_report_constraints_one_with_two(self):
        self.cm.constrain('naz')
        self.cm.set_constraint('naz', 9.12343)
        self.cm.constrain('a_eq_b')
        eq_(self.cm.report_constraints_lines(),
            ['!   1 more constraint required',
             '    naz: 9.1234',
             '    a_eq_b'])

    def test_report_constraints_one_with_three(self):
        self.cm.constrain('naz')
        self.cm.set_constraint('naz', 9.12343)
        self.cm.constrain('a_eq_b')
        self.cm.constrain('mu')
        self.cm.set_constraint('mu', 9.12343)

        eq_(self.cm.report_constraints_lines(),
            ['    naz: 9.1234',
             '    a_eq_b',
             '    mu: 9.1234'])

    def _constrain(self, *args):
        for con in args:
            self.cm.constrain(con)

    @raises(ValueError)
    def test_is_implemented_invalid(self):
        self._constrain('naz')
        self.cm.is_current_mode_implemented()

    # 1 samp

    def test_is_implemented_1_samp_naz(self):
        self._constrain('naz', 'alpha', 'mu')
        eq_(self.cm.is_current_mode_implemented(), True)

    def test_is_implemented_1_samp_det(self):
        self._constrain('qaz', 'alpha', 'mu')
        eq_(self.cm.is_current_mode_implemented(), True)

    # 2 samp + ref

    def test_is_implemented_2_samp_ref_mu_chi(self):
        self._constrain('beta', 'mu', 'chi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_2_samp_ref_mu90_chi0(self):
        self._constrain('beta', 'mu', 'chi')
        self.cm.set_constraint('mu', 0)
        self.cm.set_constraint('chi', 90)
        eq_(self.cm.is_current_mode_implemented(), True)

    def test_is_implemented_2_samp_ref_mu_eta(self):
        self._constrain('beta', 'mu', 'eta')
        eq_(self.cm.is_current_mode_implemented(), True)

    def test_is_implemented_2_samp_ref_mu_phi(self):
        self._constrain('beta', 'mu', 'phi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_2_samp_ref_eta_chi(self):
        self._constrain('beta', 'eta', 'chi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_2_samp_ref_eta_phi(self):
        self._constrain('beta', 'eta', 'phi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_2_samp_ref_chi_phi(self):
        self._constrain('beta', 'chi', 'phi')
        eq_(self.cm.is_current_mode_implemented(), True)

    # 2 samp + det

    def test_is_implemented_2_samp_det_mu_chi(self):
        self._constrain('qaz', 'mu', 'chi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_2_samp_det_mu_eta(self):
        self._constrain('qaz', 'mu', 'eta')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_2_samp_det_mu_phi(self):
        self._constrain('qaz', 'mu', 'phi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_2_samp_det_eta_chi(self):
        self._constrain('qaz', 'eta', 'chi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_2_samp_det_eta_phi(self):
        self._constrain('qaz', 'eta', 'phi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_2_samp_det_chi_phi(self):
        self._constrain('qaz', 'chi', 'phi')
        eq_(self.cm.is_current_mode_implemented(), False)

    # 3 samp

    def test_is_implemented_3_samp_no_mu(self):
        self._constrain('eta', 'chi', 'phi')
        eq_(self.cm.is_current_mode_implemented(), True)

    def test_is_implemented_3_samp_no_eta(self):
        self._constrain('mu', 'chi', 'phi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_3_samp_no_chi(self):
        self._constrain('mu', 'eta', 'phi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_is_implemented_3_samp_no_phi(self):
        self._constrain('mu', 'eta', 'chi')
        eq_(self.cm.is_current_mode_implemented(), False)

    def test_set_fails(self):
        try:
            self.cm.set_constraint('not_a_constraint', object())
            assert False
        except DiffcalcException, e:
            eq_(e.args[0], "Could not set not_a_constraint. This is not an "
                "available constraint.")

        try:
            self.cm.set_constraint('delta', object())
            assert False
        except DiffcalcException, e:
            eq_(e.args[0],
                "Could not set delta. This is not currently constrained.")

        self.cm.constrain('a_eq_b')
        try:
            self.cm.set_constraint('a_eq_b', object())
            assert False
        except DiffcalcException, e:
            eq_(e.args[0],
                "Could not set a_eq_b. This constraint takes no value.")

#        self.cm.constrain('delta')
#        self.cm.track('delta')
#        try:
#            self.cm.set('delta', object())
#            assert False
#        except DiffcalcException, e:
#            eq_(e.args[0], ("Could not set delta as this constraint is "
#                            "configured to track its associated\n"
#                            "physical angle. First remove this tracking "
#                            "(use 'untrack delta')."))

    def test_set(self):
        #"%s: %s --> %f %s"
        self.cm.constrain('alpha')
        eq_(self.cm.set_constraint('alpha', 1.), 'alpha : --- --> 1.0')
        eq_(self.cm.set_constraint('alpha', 2.), 'alpha : 1.0 --> 2.0')



#    def test_track_fails(self):
#        try:
#            self.cm.track('not_a_constraint')
#            assert False
#        except DiffcalcException, e:
#            eq_(e.args[0], "Could not track not_a_constraint as this is not "
#                "an available constraint.")
#
#        try:
#            self.cm.track('delta')
#            assert False
#        except DiffcalcException, e:
#            eq_(e.args[0],
#                "Could not track delta as this is not currently constrained.")
#
#        self.cm.constrain('a_eq_b')
#        try:
#            self.cm.track('a_eq_b')
#            assert False
#        except DiffcalcException, e:
#            eq_(e.args[0],
#                "Could not track a_eq_b as this constraint takes no value.")
#
#        self.cm.constrain('alpha')
#        try:
#            self.cm.track('alpha')
#            assert False
#        except DiffcalcException, e:
#            eq_(e.args[0], ("Could not configure alpha to track as this "
#                            "constraint is not associated with a\n"
#                            "physical angle."))
#
#    def test_track(self):
#        #"%s: %s --> %f %s"
#        self.cm.constrain('delta')
#        eq_(self.cm.track('delta'), 'delta : --- ~~> 1.0 (tracking)')
#        eq_(self.cm.track('delta'), 'Delta was already configured to track.')
#        self.cm.untrack('delta')
#        self.cm.set_constraint('delta', 2.)
#        eq_(self.cm.track('delta'), 'delta : 2.0 ~~> 1.0 (tracking)')

class TestConstraintManagerWithFourCircles:

    def setUp(self):
        self.cm = YouConstraintManager(None, {NUNAME: 0, 'mu': 0})    

    def test_init(self):
        eq_(self.cm.all, {NUNAME: 0, 'mu': 0})
        eq_(self.cm.detector, {NUNAME: 0})
        eq_(self.cm.reference, {})
        eq_(self.cm.sample, {'mu': 0})
        eq_(self.cm.naz, {})

    def test_build_initial_display_table_with_fixed_detector(self):
        self.cm = YouConstraintManager(None, {NUNAME: 0})
        print self.cm.build_display_table_lines()
        eq_(self.cm.build_display_table_lines(),
            ['    REF        SAMP',
             '    ======     ======',
             '    a_eq_b     mu',
             '    alpha      eta',
             '    beta       chi',
             '    psi        phi'])
        
    def test_build_initial_display_table_with_fixed_sample(self):
        self.cm = YouConstraintManager(None, {'mu': 0})
        print self.cm.build_display_table_lines()
        eq_(self.cm.build_display_table_lines(),
            ['    DET        REF        SAMP',
             '    ======     ======     ======',
             '    delta      a_eq_b     eta',
             '    %s     alpha      chi' % NUNAME.ljust(6),
             '    qaz        beta       phi',
             '    naz        psi'])
        
    def test_build_initial_display_table_for_four_circle(self):
        self.cm = YouConstraintManager(None, {'mu': 0, NUNAME: 0})
        print self.cm.build_display_table_lines()
        eq_(self.cm.build_display_table_lines(),
            ['    REF        SAMP',
             '    ======     ======',
             '    a_eq_b     eta',
             '    alpha      chi',
             '    beta       phi',
             '    psi'])
        
    def test_constrain_fixed_detector_angle(self):
        assert_raises(DiffcalcException, self.cm.constrain, 'delta')
        assert_raises(DiffcalcException, self.cm.constrain, NUNAME)
        assert_raises(DiffcalcException, self.cm.constrain, 'naz')
        assert_raises(DiffcalcException, self.cm.constrain, 'qaz')

    def test_unconstrain_fixed_detector_angle(self):
        assert_raises(DiffcalcException, self.cm.unconstrain, 'delta')
        assert_raises(DiffcalcException, self.cm.unconstrain, NUNAME)
        assert_raises(DiffcalcException, self.cm.unconstrain, 'naz')
        assert_raises(DiffcalcException, self.cm.unconstrain, 'qaz')
        
    def test_set_constrain_fixed_detector_angle(self):
        assert_raises(DiffcalcException, self.cm.set_constraint, 'delta', 0)
        assert_raises(DiffcalcException, self.cm.set_constraint, NUNAME, 0)
        assert_raises(DiffcalcException, self.cm.set_constraint, 'naz', 0)
        assert_raises(DiffcalcException, self.cm.set_constraint, 'qaz', 0)
    
    @raises(DiffcalcException)
    def test_constrain_fixed_sample_angle(self):
        self.cm.constrain('mu')

    @raises(DiffcalcException)
    def test_unconstrain_fixed_sample_angle(self):
        self.cm.unconstrain('mu')

    @raises(DiffcalcException)
    def test_set_constrain_fixed_sample_angle(self):
        self.cm.set_constraint('mu', 0)