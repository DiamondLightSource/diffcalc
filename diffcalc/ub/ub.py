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

from math import asin, pi
from datetime import datetime

from diffcalc.util import getInputWithDefault as promptForInput, \
    promptForNumber, promptForList, allnum, isnum
from diffcalc.util import command

TORAD = pi / 180
TODEG = 180 / pi




class UbCommands(object):

    def __init__(self, hardware, geometry, ubcalc, include_sigtau=True):
        self._hardware = hardware
        self._geometry = geometry
        self._ubcalc = ubcalc
        self.commands = ['State',
                         self.newub,
                         self.loadub,
                         self.listub,
                         self.saveubas,
                         self.ub,
                         'Lattice',
                         self.setlat,
                         self.c2th,
                         'Surface',
                         self.sigtau,
                         'Reflections',
                         self.showref,
                         self.addref,
                         self.editref,
                         self.delref,
                         self.swapref,
                         'ub',
                         self.setu,
                         self.setub,
                         self.calcub,
                         self.trialub]
        if not include_sigtau:
            self.commands.remove('Surface')
            self.commands.remove(self.sigtau)

    def __str__(self):
        return self._ubcalc.__str__()

### UB state ###

    @command
    def newub(self, name=None):
        """newub {'name'} -- start a new ub calculation name
        """
        if name is None:
            # interactive
            name = promptForInput('calculation name')
            self._ubcalc.start_new(name)
            self.setlat()
        elif isinstance(name, str):
            # just trying might cause confusion here
            self._ubcalc.start_new(name)
        else:
            raise TypeError()

    @command
    def loadub(self, name_or_num):
        """loadub {'name'|num} -- load an existing ub calculation
        """
        if isinstance(name_or_num, str):
            self._ubcalc.load(name_or_num)
        self._ubcalc.load(self._ubcalc.listub()[int(name_or_num)])

    @command
    def listub(self):
        """listub -- list the ub calculations available to load.
        """
        print "UB calculations in cross-visit database:"
        for n, name in enumerate(self._ubcalc.listub()):
            print "%2i) %s" % (n, name)

    @command
    def saveubas(self, name):
        """saveubas 'name' -- save the ub calculation with a new name
        """
        if isinstance(name, str):
            # just trying might cause confusion here
            self._ubcalc.saveas(name)
        else:
            raise TypeError()

    @command
    def ub(self):
        """ub -- show the complete state of the ub calculation
        """
        #wavelength = float(self._hardware.get_wavelength())
        #energy = float(self._hardware.get_energy())
        print self._ubcalc.__str__()

### UB lattice ###

    @command
    def setlat(self, name=None, *args):
        """
        setlat  -- interactively enter lattice parameters (Angstroms and Deg)
        setlat name a -- assumes cubic
        setlat name a b -- assumes tetragonal
        setlat name a b c -- assumes ortho
        setlat name a b c gamma -- assumes mon/hex with gam not equal to 90
        setlat name a b c alpha beta gamma -- arbitrary
        """

        if name is None:  # Interactive
            name = promptForInput("crystal name")
            a = promptForNumber('    a', 1)
            b = promptForNumber('    b', a)
            c = promptForNumber('    c', a)
            alpha = promptForNumber('alpha', 90)
            beta = promptForNumber('beta', 90)
            gamma = promptForNumber('gamma', 90)
            self._ubcalc.set_lattice(name, a, b, c, alpha, beta, gamma)

        elif (isinstance(name, str) and
              len(args) in (1, 2, 3, 4, 6) and
              allnum(args)):
            # first arg is string and rest are numbers
            self._ubcalc.set_lattice(name, *args)
        else:
            raise TypeError()

    @command
    def c2th(self, hkl, en=None):
        """
        c2th [h k l]  -- calculate two-theta angle for reflection
        """
        if en is None:
            wl = self._hardware.get_wavelength()
        else:
            wl = 12.39842 / en
        d = self._ubcalc.get_hkl_plane_distance(hkl)
        return 2.0 * asin(wl / (d * 2)) * TODEG

### Surface stuff ###

    @command
    def sigtau(self, sigma=None, tau=None):
        """sigtau {sigma tau} -- sets or displays sigma and tau"""
        if sigma is None and tau is None:
            chi = self._hardware.get_position_by_name('chi')
            phi = self._hardware.get_position_by_name('phi')
            _sigma, _tau = self._ubcalc.sigma, self._ubcalc.tau
            print "sigma, tau = %f, %f" % (_sigma, _tau)
            print "  chi, phi = %f, %f" % (chi, phi)
            sigma = promptForInput("sigma", -chi)
            tau = promptForInput("  tau", -phi)
            self._ubcalc.sigma = sigma
            self._ubcalc.tau = tau
        else:
            self._ubcalc.sigma = float(sigma)
            self._ubcalc.tau = float(tau)

### UB refelections ###

    @command
    def showref(self):
        """showref -- shows full reflection list"""
        if self._ubcalc._state.reflist:
            print '\n'.join(self._ubcalc._state.reflist.str_lines())
        else:
            print "<<< No UB calculation started >>>"

    @command
    def addref(self, *args):
        """
        addref -- add reflection interactively
        addref [h k l] {'tag'} -- add reflection with current position and energy
        addref [h k l] (p1,p2...pN) energy {'tag'} -- add arbitrary reflection
        """

        if len(args) == 0:
            h = promptForNumber('h', 0.)
            k = promptForNumber('k', 0.)
            l = promptForNumber('l', 0.)
            if None in (h, k, l):
                self.handleInputError("h,k and l must all be numbers")
            reply = promptForInput('current pos', 'y')
            if reply in ('y', 'Y', 'yes'):
                positionList = self._hardware.get_position()
                energy = self._hardware.get_energy()
            else:
                currentPos = self._hardware.get_position()
                positionList = []
                names = self._hardware.get_axes_names()
                for i, angleName in enumerate(names):
                    val = promptForNumber(angleName.rjust(7), currentPos[i])
                    if val is None:
                        self.handleInputError("Please enter a number, or press"
                                              " Return to accept default!")
                        return
                    positionList.append(val)
                energy = promptForNumber('energy', self._hardware.get_energy())
                if val is None:
                    self.handleInputError("Please enter a number, or press "
                                          "Return to accept default!")
                    return
                muliplier = self._hardware.energyScannableMultiplierToGetKeV
                energy = energy * muliplier
            tag = promptForInput("tag")
            if tag == '':
                tag = None
            pos = self._geometry.physical_angles_to_internal_position(positionList)
            self._ubcalc.add_reflection(h, k, l, pos, energy, tag,
                                       datetime.now())
        elif len(args) in (1, 2, 3, 4):
            args = list(args)
            h, k, l = args.pop(0)
            if not (isnum(h) and isnum(k) and isnum(l)):
                raise TypeError()
            if len(args) >= 2:
                pos = self._geometry.physical_angles_to_internal_position(
                    args.pop(0))
                energy = args.pop(0)
                if not isnum(energy):
                    raise TypeError()
            else:
                pos = self._geometry.physical_angles_to_internal_position(
                    self._hardware.get_position())
                energy = self._hardware.get_energy()
            if len(args) == 1:
                tag = args.pop(0)
                if not isinstance(tag, str):
                    raise TypeError()
            else:
                tag = None
            self._ubcalc.add_reflection(h, k, l, pos, energy, tag,
                                       datetime.now())
        else:
            raise TypeError()

    @command
    def editref(self, num):
        """editref num -- interactively edit a reflection.
        """
        num = int(num)

        # Get old reflection values
        [oldh, oldk, oldl], oldExternalAngles, oldEnergy, oldTag, oldT = \
            self._ubcalc.get_reflection_in_external_angles(num)
        del oldT  # current time will be used.

        h = promptForNumber('h', oldh)
        k = promptForNumber('k', oldk)
        l = promptForNumber('l', oldl)
        if None in (h, k, l):
            self.handleInputError("h,k and l must all be numbers")
        reply = promptForInput('update position with current hardware setting',
                               'n')
        if reply in ('y', 'Y', 'yes'):
            positionList = self._hardware.get_position()
            energy = self._hardware.get_energy()
        else:
            positionList = []
            names = self._hardware.get_axes_names()
            for i, angleName in enumerate(names):
                val = promptForNumber(angleName.rjust(7), oldExternalAngles[i])
                if val is None:
                    self.handleInputError("Please enter a number, or press "
                                          "Return to accept default!")
                    return
                positionList.append(val)
            energy = promptForNumber('energy', oldEnergy)
            if val is None:
                self.handleInputError("Please enter a number, or press Return "
                                      "to accept default!")
                return
            energy = energy * self._hardware.energyScannableMultiplierToGetKeV
        tag = promptForInput("tag", oldTag)
        if tag == '':
            tag = None
        pos = self._geometry.physical_angles_to_internal_position(positionList)
        self._ubcalc.edit_reflection(num, h, k, l, pos, energy, tag,
                                    datetime.now())

    @command
    def delref(self, num):
        """delref num -- deletes a reflection (numbered from 1)
        """
        self._ubcalc.del_reflection(int(num))

    @command
    def swapref(self, num1=None, num2=None):
        """
        swapref -- swaps first two reflections used for calulating U matrix
        swapref num1 num2 -- swaps two reflections (numbered from 1)
        """
        if num1 is None and num2 is None:
            self._ubcalc.swap_reflections(1, 2)
        elif isinstance(num1, int) and isinstance(num2, int):
            self._ubcalc.swap_reflections(num1, num2)
        else:
            raise TypeError()

### UB calculations ###

    @command
    def setu(self, U=None):
        """setu {((,,),(,,),(,,))} -- manually set u matrix
        """
        if U is None:
            U = self._promptFor3x3MatrixDefaultingToIdentity()
            if U is None:
                return  # an error will have been printed or thrown
        if self._is3x3TupleOrList(U):
            self._ubcalc.set_U_manually(U)
        else:
            raise TypeError("U must be given as 3x3 list or tuple")

    @command
    def setub(self, UB=None):
        """setub {((,,),(,,),(,,))} -- manually set ub matrix"""
        if UB is None:
            UB = self._promptFor3x3MatrixDefaultingToIdentity()
            if UB is None:
                return  # an error will have been printed or thrown
        if self._is3x3TupleOrList(UB):
            self._ubcalc.set_UB_manually(UB)
        else:
            raise TypeError("UB must be given as 3x3 list or tuple")

    def _promptFor3x3MatrixDefaultingToIdentity(self):
        estring = "Please enter a number, or press Return to accept default!"
        row1 = promptForList("row1", (1, 0, 0))
        if row1 is None:
            self.handleInputError(estring)
            return None
        row2 = promptForList("row2", (0, 1, 0))
        if row2 is None:
            self.handleInputError(estring)
            return None
        row3 = promptForList("row3", (0, 0, 1))
        if row3 is None:
            self.handleInputError(estring)
            return None
        return [row1, row2, row3]

    @command
    def calcub(self):
        """calcub -- (re)calculate u matrix from ref1 and ref2.
        """
        self._ubcalc.calculate_UB()

    @command
    def trialub(self):
        """trialub -- (re)calculate u matrix from ref1 only (check carefully).
        """
        self._ubcalc.calculate_UB_from_primary_only()

    def _is3x3TupleOrList(self, m):
        if type(m) not in (list, tuple):
            return False
        if len(m) != 3:
            return False
        for mrow in m:
            if type(mrow) not in (list, tuple):
                return False
            if len(mrow) != 3:
                return False
        return True
