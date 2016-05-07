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

# to quieten syntax checkers:
hardware = None
dc = None
en = None


def demo_all():

    print "SETUP\n"
    demo_setup()

    print "HARDWARE\n"
    demo_hardware()

    print "ORIENT\n"
    demo_orient()

    print "READ\n"
    demo_read()

    print "CONSTRAIN\n"
    demo_constrain()

    print "CALC\n"
    demo_calc()


def demo_setup():
    global hardware, dc
    print "\n>>> from diffcalc.hkl.you.geometry import SixCircle"
    from diffcalc.hkl.you.geometry import SixCircle
    print "\n>>> from diffcalc.hardware import DummyHardwareAdapter"
    from diffcalc.hardware import DummyHardwareAdapter
    print "\n>>> from diffcalc.diffcalc_ import create_diffcalc"
    from diffcalc.diffcalc_ import create_diffcalc

    print "\n>>> hardware = DummyHardwareAdapter(('mu', 'delta', 'gam', 'eta', 'chi', 'phi'))"
    hardware = DummyHardwareAdapter(('mu', 'delta', 'gam', 'eta', 'chi', 'phi'))
    print "\n>>> dc = create_diffcalc('you', SixCircle(), hardware)"
    dc = create_diffcalc('you', SixCircle(), hardware)


def demo_hardware():
    global en
    print "\n>>> hardware.wavelength = 1"
    hardware.wavelength = 1
    print "\n>>> en = hardware.energy"
    en = hardware.energy
    print "\n>>> print hardware"
    print hardware


def demo_orient():
    print "\n>>> help(dc.ub)"
    print dc.ub.__doc__

    print "\n>>> dc.ub.newub('test')"
    print dc.ub.newub('test')

    print "\n>>> dc.ub.setlat('cubic', 1, 1, 1, 90, 90, 90)"
    dc.ub.setlat('cubic', 1, 1, 1, 90, 90, 90)

    print "\n>>> dc.ub.ub()"
    dc.ub.ub()

    # add 1st reflection
    print "\n>>> dc.ub.c2th([1, 0, 0])                            # energy from hardware"
    print dc.ub.c2th([1, 0, 0])

    print "\n>>> hardware.position = 0, 60, 0, 30, 0, 0           # mu del gam eta chi phi"
    hardware.position = 0, 60, 0, 30, 0, 0

    print "\n>>> dc.ub.addref([1, 0, 0])                          # energy from hardware"
    dc.ub.addref([1, 0, 0])

    # ad 2nd reflection
    print "\n>>> dc.ub.c2th([0, 1, 0])                            # energy from hardware"
    print dc.ub.c2th([0, 1, 0])

    print "\n>>> dc.ub.addref([0, 1, 0], [0, 60, 0, 30, 0, 90], en)"
    dc.ub.addref([0, 1, 0], [0, 60, 0, 30, 0, 90], en)

    print "\n>>> dc.ub.ub()"
    dc.ub.ub()

    print "\n>>> dc.checkub()"
    dc.checkub()


def demo_read():
    ### Read up hkl ###

    print "\n>>> dc.angles_to_hkl((0., 60., 0., 30., 0., 0.))     # energy from hardware"
    print dc.angles_to_hkl((0., 60., 0., 30., 0., 0.))

    print "\n>>> dc.angles_to_hkl((0.0, 90.0, 0.0, 45.0, 0.0, 45.0), en)"
    print dc.angles_to_hkl((0.0, 90.0, 0.0, 45.0, 0.0, 45.0), en)

### Move to hkl ###


def demo_constrain():
    print "\n >>>help(dc.hkl)"
    print dc.hkl.__doc__

    print "\n >>> dc.hkl.con('qaz', 90)"
    dc.hkl.con('qaz', 90)

    print "\n >>> dc.hkl.con('a_eq_b')"
    dc.hkl.con('a_eq_b')

    print "\n >>> dc.hkl.con('mu', 0)"
    dc.hkl.con('mu', 0)

    print "\n >>> dc.hkl.con()"
    dc.hkl.con()

    print "\n >>> hardware.set_lower_limit('delta', 0)"
    hardware.set_lower_limit('delta', 0)


def demo_calc():
    print "\n >>> dc.hkl_to_angles(1, 0, 0)                        # energy from hardware"
    print dc.hkl_to_angles(1, 0, 0)

    print "\n >>> dc.hkl_to_angles(1, 1, 0, en)"
    print dc.hkl_to_angles(1, 1, 0, en)

    print "\n >>> from math import cos, sin, pi"
    from math import cos, sin, pi

    print "\n >>> TORAD = pi / 180"
    TORAD = pi / 180

    print "\n >>> hkl = cos(10 * TORAD), sin(10 * TORAD), 0"
    hkl = cos(10 * TORAD), sin(10 * TORAD), 0

    print "\n >>> dc.hkl_to_angles(*hkl)                           # energy from hardware"
    print dc.hkl_to_angles(*hkl)
