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

from math import pi
import inspect
from nose.tools import eq_, raises
from nose.plugins.skip import Skip, SkipTest

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.gdasupport.factory import create_objects
import diffcalc.gdasupport.factory  # @UnusedImport for VERBOSE
from diffcalc.gdasupport.minigda.command import Pos, Scan
from test.tools import wrap_command_to_print_calls, mneq_, aneq_,\
    assert_dict_almost_equal


EXPECTED_OBJECTS = set(['delref', 'en', 'uncon', 'showref', 'l',
                    'hardware', 'checkub', 'listub', 'mu_par', 'saveubas',
                    'eta_par', 'ct', 'setmin', 'ub', 'setcut', 'chi', 'setlat',
                    'qaz', 'addref', 'swapref', 'newub', 'naz', 'sixc', 'gam',
                    'sim', 'phi', 'psi', 'wl',
                    'setmax', 'dc', 'loadub', 'beta', 'hkl', 'delta', 'alpha',
                    'gam_par', 'trialub', 'delta_par', 'h', 'k', 'phi_par',
                     'a_eq_b', 'mu', 'setu', 'eta', 'editref', 'con', 'setub', 'c2th',
                    'calcub', 'chi_par', 'hklverbose', 'allhkl'])

# Placeholders for names to be added to globals (for benefit of IDE)
delref = en = uncon = showref = l = hardware = checkub = listub = None
mu_par = saveubas = eta_par = ct = setmin = ub = setcut = chi = setlat = None
qaz = addref = swapref = newub = naz = sixc = gam = sim = None
phi = psi = sigtau = wl = setmax = dc = loadub = beta = hkl = delta = None
alpha = gam_par = trialub = delta_par = h = k = phi_par = a_eq_b = mu = setu = eta = None
editref = con = setub = c2th = calcub = chi_par = hklverbose = None


PRINT_WITH_USER_SYNTAX = True
diffcalc.gdasupport.factory.VERBOSE = False

pos = wrap_command_to_print_calls(Pos(globals()), PRINT_WITH_USER_SYNTAX)


def call_scannable(scn):
    print '\n>>> %s' % scn.name
    print scn.__str__()


class TestDiffcalcFactorySixc():
    """
    All the components used here are well tested. This integration test is
    mainly to get output for the manual, to help when tweaking the user
    interface, and to make sure it all works together.
    """

    def setup(self):
        axis_names = ('mu', 'delta', 'gam', 'eta', 'chi', 'phi')
        virtual_angles = ('theta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta')
        self.objects = create_objects(
            engine_name='you',
            geometry='sixc',
            dummy_axis_names=axis_names,
            dummy_energy_name='en',
            hklverbose_virtual_angles_to_report=virtual_angles,
            simulated_crystal_counter_name='ct'
            )
        for name, obj in self.objects.iteritems():
            if inspect.ismethod(obj):
                globals()[name] = wrap_command_to_print_calls(
                                      obj, PRINT_WITH_USER_SYNTAX)
            else:
                globals()[name] = obj

    def test_created_objects(self):
        created_objects = set(self.objects.keys())
        print "Unexpected objects:", created_objects.difference(EXPECTED_OBJECTS)
        print "Missing objects:", EXPECTED_OBJECTS.difference(created_objects)
        eq_(created_objects, EXPECTED_OBJECTS)

    def test_help_visually(self):
        print "\n>>> help ub"
        help(ub)
        print "\n>>> help hkl"
        help(hkl)
        print "\n>>> help newub"
        help(newub)

    def test_axes(self):
        call_scannable(sixc)
        call_scannable(phi)

    def test_with_no_ubcalc(self):
        ub()
        showref()
        call_scannable(hkl)

    def _orient(self):
        pos(wl, 1)
        call_scannable(en)  # like typing en (or en())
        newub('test')
        setlat('cubic', 1, 1, 1, 90, 90, 90)

        c2th([1, 0, 0])
        pos(sixc, [0, 60, 0, 30, 0, 0])
        addref([1, 0, 0], 'ref1')

        c2th([0, 1, 0])
        pos(phi, 90)
        addref([0, 1, 0], 'ref2')

    def test_orientation_phase(self):
        self._orient()
        ub()
        checkub()
        showref()

        U = matrix('1 0 0; 0 1 0; 0 0 1')
        UB = U * 2 * pi
        mneq_(dc.ub._ubcalc.U, U)
        mneq_(dc.ub._ubcalc.UB, UB)

    def test_hkl_read(self):
        self._orient()
        call_scannable(hkl)

    def test_help_con(self):
        help(con)

    def test_constraint_mgmt(self):
        diffcalc.util.DEBUG = True
        con()  # TODO: show constrained values underneath

    def test_hkl_move_no_constraints(self):
        raise SkipTest()
        self._orient()
        pos(hkl, [1, 0, 0])

    def test_hkl_move_no_values(self):
        raise SkipTest()
        self._orient()
        con(mu)
        con(gam)
        con('a_eq_b')
        con('a_eq_b')
        pos(hkl, [1, 0, 0])

    def test_hkl_move_okay(self):
        self._orient()
        con(mu)
        con(gam)
        con('a_eq_b')
        pos(mu_par, 0)
        pos(gam_par, 0)  # TODO: Fails with qaz=90
        pos(hkl, [1, 1, 0])  # TODO: prints DEGENERATE. necessary?
        call_scannable(sixc)

    @raises(TypeError)
    def test_usage_error_signature(self):
        c2th('wrong arg', 'wrong arg')

    @raises(TypeError)
    def test_usage_error_inside(self):
        setlat('wrong arg', 'wrong arg')