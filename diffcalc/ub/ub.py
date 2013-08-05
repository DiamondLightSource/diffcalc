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

from diffcalc.conf import settings
from diffcalc.ub.calc import UBCalculation

from math import asin, pi
from datetime import datetime

from diffcalc.util import getInputWithDefault as promptForInput, \
    promptForNumber, promptForList, allnum, isnum
from diffcalc.util import command

TORAD = pi / 180
TODEG = 180 / pi



_ubcalc = UBCalculation(settings.HARDWARE.get_axes_names(),  # @UndefinedVariable
                        settings.GEOMETRY,
                        settings.UBCALC_PERSISTER,
                        settings.UBCALC_STRATEGY)

HARDWARE = settings.HARDWARE

GEOMETRY = settings.GEOMETRY


### UB state ###

@command
def newub(name=None):
    """newub {'name'} -- start a new ub calculation name
    """
    if name is None:
        # interactive
        name = promptForInput('calculation name')
        _ubcalc.start_new(name)
        setlat()
    elif isinstance(name, str):
        # just trying might cause confusion here
        _ubcalc.start_new(name)
    else:
        raise TypeError()

@command
def loadub(name_or_num):
    """loadub {'name'|num} -- load an existing ub calculation
    """
    if isinstance(name_or_num, str):
        _ubcalc.load(name_or_num)
    _ubcalc.load(_ubcalc.listub()[int(name_or_num)])

@command
def listub():
    """listub -- list the ub calculations available to load.
    """
    print "UB calculations in cross-visit database:"
    for n, name in enumerate(_ubcalc.listub()):
        print "%2i) %s" % (n, name)

@command
def saveubas(name):
    """saveubas 'name' -- save the ub calculation with a new name
    """
    if isinstance(name, str):
        # just trying might cause confusion here
        _ubcalc.saveas(name)
    else:
        raise TypeError()

@command
def ub():
    """ub -- show the complete state of the ub calculation
    """
    #wavelength = float(HARDWARE.get_wavelength())
    #energy = float(HARDWARE.get_energy())
    print _ubcalc.__str__()

### UB lattice ###

@command
def setlat(name=None, *args):
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
        _ubcalc.set_lattice(name, a, b, c, alpha, beta, gamma)

    elif (isinstance(name, str) and
          len(args) in (1, 2, 3, 4, 6) and
          allnum(args)):
        # first arg is string and rest are numbers
        _ubcalc.set_lattice(name, *args)
    else:
        raise TypeError()

@command
def c2th(hkl, en=None):
    """
    c2th [h k l]  -- calculate two-theta angle for reflection
    """
    if en is None:
        wl = HARDWARE.get_wavelength()
    else:
        wl = 12.39842 / en
    d = _ubcalc.get_hkl_plane_distance(hkl)
    return 2.0 * asin(wl / (d * 2)) * TODEG

### Surface stuff ###

@command
def sigtau(sigma=None, tau=None):
    """sigtau {sigma tau} -- sets or displays sigma and tau"""
    if sigma is None and tau is None:
        chi = HARDWARE.get_position_by_name('chi')
        phi = HARDWARE.get_position_by_name('phi')
        _sigma, _tau = _ubcalc.sigma, _ubcalc.tau
        print "sigma, tau = %f, %f" % (_sigma, _tau)
        print "  chi, phi = %f, %f" % (chi, phi)
        sigma = promptForInput("sigma", -chi)
        tau = promptForInput("  tau", -phi)
        _ubcalc.sigma = sigma
        _ubcalc.tau = tau
    else:
        _ubcalc.sigma = float(sigma)
        _ubcalc.tau = float(tau)

### UB refelections ###

@command
def showref():
    """showref -- shows full reflection list"""
    if _ubcalc._state.reflist:
        print '\n'.join(_ubcalc._state.reflist.str_lines())
    else:
        print "<<< No UB calculation started >>>"

@command
def addref(*args):
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
            _handleInputError("h,k and l must all be numbers")
        reply = promptForInput('current pos', 'y')
        if reply in ('y', 'Y', 'yes'):
            positionList = HARDWARE.get_position()
            energy = HARDWARE.get_energy()
        else:
            currentPos = HARDWARE.get_position()
            positionList = []
            names = HARDWARE.get_axes_names()
            for i, angleName in enumerate(names):
                val = promptForNumber(angleName.rjust(7), currentPos[i])
                if val is None:
                    _handleInputError("Please enter a number, or press"
                                          " Return to accept default!")
                    return
                positionList.append(val)
            energy = promptForNumber('energy', HARDWARE.get_energy())
            if val is None:
                _handleInputError("Please enter a number, or press "
                                      "Return to accept default!")
                return
            muliplier = HARDWARE.energyScannableMultiplierToGetKeV
            energy = energy * muliplier
        tag = promptForInput("tag")
        if tag == '':
            tag = None
        pos = GEOMETRY.physical_angles_to_internal_position(positionList)
        _ubcalc.add_reflection(h, k, l, pos, energy, tag,
                                   datetime.now())
    elif len(args) in (1, 2, 3, 4):
        args = list(args)
        h, k, l = args.pop(0)
        if not (isnum(h) and isnum(k) and isnum(l)):
            raise TypeError()
        if len(args) >= 2:
            pos = GEOMETRY.physical_angles_to_internal_position(
                args.pop(0))
            energy = args.pop(0)
            if not isnum(energy):
                raise TypeError()
        else:
            pos = GEOMETRY.physical_angles_to_internal_position(
                HARDWARE.get_position())
            energy = HARDWARE.get_energy()
        if len(args) == 1:
            tag = args.pop(0)
            if not isinstance(tag, str):
                raise TypeError()
        else:
            tag = None
        _ubcalc.add_reflection(h, k, l, pos, energy, tag,
                                   datetime.now())
    else:
        raise TypeError()

@command
def editref(num):
    """editref num -- interactively edit a reflection.
    """
    num = int(num)

    # Get old reflection values
    [oldh, oldk, oldl], oldExternalAngles, oldEnergy, oldTag, oldT = \
        _ubcalc.get_reflection_in_external_angles(num)
    del oldT  # current time will be used.

    h = promptForNumber('h', oldh)
    k = promptForNumber('k', oldk)
    l = promptForNumber('l', oldl)
    if None in (h, k, l):
        _handleInputError("h,k and l must all be numbers")
    reply = promptForInput('update position with current hardware setting',
                           'n')
    if reply in ('y', 'Y', 'yes'):
        positionList = HARDWARE.get_position()
        energy = HARDWARE.get_energy()
    else:
        positionList = []
        names = HARDWARE.get_axes_names()
        for i, angleName in enumerate(names):
            val = promptForNumber(angleName.rjust(7), oldExternalAngles[i])
            if val is None:
                _handleInputError("Please enter a number, or press "
                                      "Return to accept default!")
                return
            positionList.append(val)
        energy = promptForNumber('energy', oldEnergy)
        if val is None:
            _handleInputError("Please enter a number, or press Return "
                                  "to accept default!")
            return
        energy = energy * HARDWARE.energyScannableMultiplierToGetKeV
    tag = promptForInput("tag", oldTag)
    if tag == '':
        tag = None
    pos = GEOMETRY.physical_angles_to_internal_position(positionList)
    _ubcalc.edit_reflection(num, h, k, l, pos, energy, tag,
                                datetime.now())

@command
def delref(num):
    """delref num -- deletes a reflection (numbered from 1)
    """
    _ubcalc.del_reflection(int(num))

@command
def swapref(num1=None, num2=None):
    """
    swapref -- swaps first two reflections used for calulating U matrix
    swapref num1 num2 -- swaps two reflections (numbered from 1)
    """
    if num1 is None and num2 is None:
        _ubcalc.swap_reflections(1, 2)
    elif isinstance(num1, int) and isinstance(num2, int):
        _ubcalc.swap_reflections(num1, num2)
    else:
        raise TypeError()

### UB calculations ###

@command
def setu(U=None):
    """setu {((,,),(,,),(,,))} -- manually set u matrix
    """
    if U is None:
        U = _promptFor3x3MatrixDefaultingToIdentity()
        if U is None:
            return  # an error will have been printed or thrown
    if _is3x3TupleOrList(U):
        _ubcalc.set_U_manually(U)
    else:
        raise TypeError("U must be given as 3x3 list or tuple")

@command
def setub(UB=None):
    """setub {((,,),(,,),(,,))} -- manually set ub matrix"""
    if UB is None:
        UB = _promptFor3x3MatrixDefaultingToIdentity()
        if UB is None:
            return  # an error will have been printed or thrown
    if _is3x3TupleOrList(UB):
        _ubcalc.set_UB_manually(UB)
    else:
        raise TypeError("UB must be given as 3x3 list or tuple")

def _promptFor3x3MatrixDefaultingToIdentity():
    estring = "Please enter a number, or press Return to accept default!"
    row1 = promptForList("row1", (1, 0, 0))
    if row1 is None:
        _handleInputError(estring)
        return None
    row2 = promptForList("row2", (0, 1, 0))
    if row2 is None:
        _handleInputError(estring)
        return None
    row3 = promptForList("row3", (0, 0, 1))
    if row3 is None:
        _handleInputError(estring)
        return None
    return [row1, row2, row3]

@command
def calcub():
    """calcub -- (re)calculate u matrix from ref1 and ref2.
    """
    _ubcalc.calculate_UB()

@command
def trialub():
    """trialub -- (re)calculate u matrix from ref1 only (check carefully).
    """
    _ubcalc.calculate_UB_from_primary_only()

def _is3x3TupleOrList(m):
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

def _handleInputError(msg):
    raise TypeError(msg)