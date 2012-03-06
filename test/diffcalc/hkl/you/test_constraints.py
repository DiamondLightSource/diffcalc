from nose.tools import eq_  # @UnresolvedImport
from mock import Mock

from diffcalc.hkl.you.constraints import YouConstraintManager
from diffcalc.util import DiffcalcException


def joined(d1, d2):
    d1.update(d2)
    return d1


class TestConstraintManager:

    def setUp(self):
        self.hardware_monitor = Mock()
        self.hardware_monitor.getPosition.return_value = (1.,) * 6
        self.hardware_monitor.getPhysicalAngleNames.return_value = [
                                      'mu', 'delta', 'nu', 'eta', 'chi', 'phi']
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
        self.cm.set('qaz', 1.234)
        self.cm.set('eta', 99.)
        print self.cm.build_display_table()
        eq_(self.cm.build_display_table(),
"""
    DET        REF        SAMP
    ======     ======     ======
    delta      a_eq_b     mu
    nu     o-> alpha  --> eta
--> qaz        beta       chi
    naz        psi        phi
                          mu_is_nu
"""[1:-1])


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

###
    def test_set_fails(self):
        try:
            self.cm.set('not_a_constraint', object())
            assert False
        except DiffcalcException, e:
            eq_(e.args[0], "Could not set not_a_constraint. This is not an "
                "available constraint.")

        try:
            self.cm.set('delta', object())
            assert False
        except DiffcalcException, e:
            eq_(e.args[0],
                "Could not set delta. This is not currently constrained.")

        self.cm.constrain('a_eq_b')
        try:
            self.cm.set('a_eq_b', object())
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
        eq_(self.cm.set('alpha', 1.), 'alpha : --- --> 1.0')
        eq_(self.cm.set('alpha', 2.), 'alpha : 1.0 --> 2.0')

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
#        self.cm.set('delta', 2.)
#        eq_(self.cm.track('delta'), 'delta : 2.0 ~~> 1.0 (tracking)')
