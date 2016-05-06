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
from __future__ import absolute_import

from diffcalc.gdasupport.factory import \
    create_objects, add_objects_to_namespace
from diffcalc.gdasupport.minigda.scannable import SingleFieldDummyScannable

#_demo = []
#_demo.append("pos wl 1")
#_demo.append("en")
#_demo.append("newub 'test'")
#_demo.append("setlat 'cubic' 1 1 1 90 90 90")
#_demo.append("c2th [1 0 0]")
#_demo.append("pos sixc [0 60 0 30 0 0]")
#_demo.append("addref 1 0 0 'ref1'")
#_demo.append("c2th [0 1 0]")
#_demo.append("pos phi 90")
#_demo.append("addref 0 1 0 'ref2'")
#_demo.append("checkub")


print '=' * 80
print "Creating dummy scannables:"
print "   mu, delta, gam, eta, chi, phi and en"
mu = SingleFieldDummyScannable('mu')
delta = SingleFieldDummyScannable('delta')
gam = SingleFieldDummyScannable('gam')
eta = SingleFieldDummyScannable('eta')
chi = SingleFieldDummyScannable('chi')
phi = SingleFieldDummyScannable('phi')

en = SingleFieldDummyScannable('en')
en.level = 3

virtual_angles = ('theta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta')
_objects = create_objects(
    engine_name='you',
    geometry='sixc',
    axis_scannable_list=(mu, delta, gam, eta, chi, phi),
    energy_scannable=en,
    hklverbose_virtual_angles_to_report=virtual_angles,
    simulated_crystal_counter_name='ct',
#    demo_commands=_demo
    )

#_objects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(_objects, globals())

from diffcalc.gdasupport.minigda import command
pos = command.Pos(globals())
scan = command.Scan(command.ScanDataPrinter())
print '=' * 80

#def help_hkl():
#    print hkl.__doc__
#
#alias('help_hkl')


def demo_all():

    print "ORIENT\n"
    demo_orient()

    print "CONSTRAIN\n"
    demo_constrain()


def echo(cmd):
    print "\n>>> " + str(cmd)


def demo_orient():
    echo("help(ub)")
    print ub.__doc__   # @UndefinedVariable

    echo("pos(wl, 1)")
    print pos(wl, 1)  # @UndefinedVariable

    echo("newub('test')")
    print newub('test')  # @UndefinedVariable

    echo("setlat('cubic', 1, 1, 1, 90, 90, 90)")
    setlat('cubic', 1, 1, 1, 90, 90, 90)  # @UndefinedVariable

    echo("ub()")
    ub()  # @UndefinedVariable

    # add 1st reflection
    echo("c2th([1, 0, 0])                            # energy from hardware")
    print c2th([1, 0, 0])  # @UndefinedVariable

    echo("pos(sixc, [0, 60, 0, 30, 0, 0])")
    pos(sixc, [0, 60, 0, 30, 0, 0])  # @UndefinedVariable

    echo("addref([1, 0, 0])                          # energy from hardware")
    addref([1, 0, 0])  # @UndefinedVariable

    # ad 2nd reflection
    echo("c2th([0, 1, 0])                            # energy from hardware")
    print c2th([0, 1, 0])  # @UndefinedVariable

    echo("pos(chi, 90)")
    print pos(phi, 90)  # @UndefinedVariable

    echo("addref([0, 1, 0])")
    addref([0, 1, 0])  # @UndefinedVariable

    echo("ub()")
    ub()  # @UndefinedVariable

    echo("dc.checkub()")
    checkub()  # @UndefinedVariable


def demo_constrain():
    echo("help(dc.hkl)")
    print hkl.__doc__  # @UndefinedVariable

    echo("con('qaz', 90)")
    con('qaz', 90)  # @UndefinedVariable

    echo("con('a_eq_b')")
    con('a_eq_b')  # @UndefinedVariable

    echo("con('mu', 0)")
    con('mu', 0)  # @UndefinedVariable

    echo("con()")
    con()  # @UndefinedVariable

    echo("setmin(delta, 0)")
    setmin(delta, 0)  # @UndefinedVariable

    echo("setmin(chi, 0)")
    setmin(chi, 0)  # @UndefinedVariable


def demo_scan():

    echo("pos(hkl, [1, 0, 0])")
    pos(hkl, [1, 0, 0])  # @UndefinedVariable
    echo("scan(delta, 40, 80, 10, hkl, ct, 1)")
    scan(delta, 40, 80, 10, hkl, ct, 1)  # @UndefinedVariable

    echo("pos(hkl, [0, 1, 0])")
    pos(hkl, [0, 1, 0])  # @UndefinedVariable
    echo("can(h, 0, 1, .2, k, l, sixc, ct, 1)")
    scan(h, 0, 1, .2, k, l, sixc, ct, 1)  # @UndefinedVariable

    echo("con(psi)")
    con(psi)  # @UndefinedVariable
    echo("scan(psi, 0, 90, 10, hkl, [1, 0, 1], eta, chi, phi, ct, .1)")
    scan(psi, 0, 90, 10, hkl, [1, 0, 1], eta, chi, phi, ct, .1)  # @UndefinedVariable
