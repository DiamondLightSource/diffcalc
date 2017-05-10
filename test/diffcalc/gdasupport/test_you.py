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
from nose.tools import eq_, raises  # @UnresolvedImport
from nose.plugins.skip import Skip, SkipTest  # @UnresolvedImport
from diffcalc.hardware import ScannableHardwareAdapter
from diffcalc.gdasupport.minigda.scannable import SingleFieldDummyScannable,\
    ScannableGroup
from diffcalc.hkl.you.geometry import SixCircle
from diffcalc.ub.persistence import UbCalculationNonPersister

import diffcalc.util  # @UnusedImport

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

import diffcalc.gdasupport.minigda.command
from test.tools import mneq_

from diffcalc import settings
import diffcalc.hkl.you.calc
diffcalc.gdasupport.minigda.command.ROOT_NAMESPACE_DICT = globals()
pos = diffcalc.gdasupport.minigda.command.Pos()

en = SingleFieldDummyScannable('en')  # keV
mu = SingleFieldDummyScannable('mu')
delta = SingleFieldDummyScannable('delta')
gam = SingleFieldDummyScannable('gam')
eta = SingleFieldDummyScannable('eta')
chi = SingleFieldDummyScannable('chi')
phi = SingleFieldDummyScannable('phi')
sixc_group = ScannableGroup('sixc', (mu, delta, gam, eta, chi, phi))

ubcalc_no = 1

you = None
def setup_module():
    global you
    settings.hardware = ScannableHardwareAdapter(sixc_group, en)
    settings.geometry = SixCircle()
    settings.ubcalc_persister = UbCalculationNonPersister()
    settings.axes_scannable_group = sixc_group
    settings.energy_scannable = en
    settings.ubcalc_strategy = diffcalc.hkl.you.calc.YouUbCalcStrategy()
    settings.angles_to_hkl_function = diffcalc.hkl.you.calc.youAnglesToHkl

    from diffcalc.gdasupport import you
    reload(you)


"""
All the components used here are well tested. This integration test is
mainly to get output for the manual, to help when tweaking the user
interface, and to make sure it all works together.
"""
# 
# PRINT_WITH_USER_SYNTAX = True
# for name, obj in self.objects.iteritems():
#     if inspect.ismethod(obj):
#         globals()[name] = wrap_command_to_print_calls(
#                               obj, PRINT_WITH_USER_SYNTAX)
#     else:
#         globals()[name] = obj
# pos = wrap_command_to_print_calls(Pos(globals()), PRINT_WITH_USER_SYNTAX)


def call_scannable(scn):
    print '\n>>> %s' % scn.name
    print scn.__str__()






def test_help_visually():
    print "\n>>> help ub"
    help(you.ub)
    print "\n>>> help hkl"
    help(you.hkl)
    print "\n>>> help newub"
    help(you.newub)

def test_axes():
    call_scannable(you.sixc)  # @UndefinedVariable
    call_scannable(phi)

def test_with_no_ubcalc():
    you.ub()
    you.showref()
    call_scannable(you.hkl)

def _orient():
    global ubcalc_no
    pos(you.wl, 1)
    call_scannable(en)  # like typing en (or en())
    you.newub('test' + str(ubcalc_no))
    ubcalc_no += 1
    you.setlat('cubic', 1, 1, 1, 90, 90, 90)

    you.c2th([1, 0, 0])
    pos(you.sixc, [0, 60, 0, 30, 0, 0])  # @UndefinedVariable
    you.addref([1, 0, 0], 'ref1')

    you.c2th([0, 1, 0])
    pos(phi, 90)
    you.addref([0, 1, 0], 'ref2')

def test__orientation_phase():
    _orient()
    you.ub()
    you.checkub()
    you.showref()

    U = matrix('1 0 0; 0 1 0; 0 0 1')
    UB = U * 2 * pi
    mneq_(you.ubcalc.U, U)
    mneq_(you.ubcalc.UB, UB)

def test_hkl_read():
    _orient()
    call_scannable(you.hkl)

def test_help_con():
    help(you.con)

def test_constraint_mgmt():
    diffcalc.util.DEBUG = True
    you.con()  # TODO: show constrained values underneath

def test_hkl_move_no_constraints():
    raise SkipTest()
    _orient()
    pos(you.hkl, [1, 0, 0])

def test_hkl_move_no_values():
    raise SkipTest()
    _orient()
    you.con(mu)
    you.con(gam)
    you.con('a_eq_b')
    you.con('a_eq_b')
    pos(you.hkl, [1, 0, 0])

def test_hkl_move_okay():
    _orient()
    you.ub()
    you.con(mu)
    you.con(gam)
    you.con('a_eq_b')
    pos(you.mu_con, 0)
    pos(you.gam_con, 0)  # TODO: Fails with qaz=90
    pos(you.hkl, [1, 1, 0])  # TODO: prints DEGENERATE. necessary?
    call_scannable(you.sixc)  # @UndefinedVariable

@raises(TypeError)
def test_usage_error_signature():
    you.c2th('wrong arg', 'wrong arg')

@raises(TypeError)
def test_usage_error_inside():
    you.setlat('wrong arg', 'wrong arg')