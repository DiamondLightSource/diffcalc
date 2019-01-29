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

from diffcalc import settings
from diffcalc.ub.calc import UBCalculation

from math import asin, pi
from datetime import datetime

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix


from diffcalc.util import getInputWithDefault as promptForInput, \
    promptForNumber, promptForList, isnum, bold
from diffcalc.util import command

TORAD = pi / 180
TODEG = 180 / pi


# When using ipython magic, these functions must not be imported to the top
# level namespace. Doing so will stop them from being called with magic.

__all__ = ['addorient', 'addref', 'c2th', 'hklangle', 'calcub', 'delorient', 'delref', 'editorient',
           'editref', 'listub', 'loadub', 'newub', 'orientub', 'saveubas', 'setlat',
           'addmiscut', 'setmiscut', 'setu', 'setub', 'showorient', 'showref', 'swaporient',
           'swapref', 'trialub', 'fitub', 'checkub', 'ub', 'ubcalc', 'rmub', 'clearorient',
           'clearref', 'lastub', 'refineub']

if settings.include_sigtau:
    __all__.append('sigtau')

if settings.include_reference:
    __all__.append('setnphi')
    __all__.append('setnhkl')


ubcalc = UBCalculation(settings.hardware,
                       settings.geometry,
                       settings.ubcalc_persister,
                       settings.ubcalc_strategy,
                       settings.include_sigtau,
                       settings.include_reference)



### UB state ###

@command
def newub(name=None):
    """newub {'name'} -- start a new ub calculation name
    """
    if name is None:
        # interactive
        name = promptForInput('calculation name')
        ubcalc.start_new(name)
        setlat()
    elif isinstance(name, str):
        if name in ubcalc._persister.list():
            print ("No UB calculation started: There is already a calculation "
                    "called: " + name)
            reply = promptForInput("Load the existing UB calculation '%s'? " % name, 'y')
            if reply in ('y', 'Y', 'yes'):
                loadub(name)
                return
            else:
                reply = promptForInput("Overwrite the existing UB calculation '%s'? " % name, 'y')
                if reply in ('y', 'Y', 'yes'):
                    ubcalc.start_new(name)
                    setlat()
                else:
                    print ("Aborting")
        else:
            # just trying might cause confusion here
            ubcalc.start_new(name)
    else:
        raise TypeError()

@command
def loadub(name_or_num):
    """loadub 'name' | num -- load an existing ub calculation
    """
    if isinstance(name_or_num, str):
        ubcalc.load(name_or_num)
    else:
        ubcalc.load(ubcalc.listub()[int(name_or_num)])

@command
def lastub():
    """lastub -- load the last used ub calculation
    """
    try:
        lastub_name = ubcalc.listub()[0]
        print "Loading ub calculation: '%s'" % lastub_name
        loadub(0)
    except IndexError:
        print "WARNING: There is no record of the last ub calculation used"

@command
def rmub(name_or_num):
    """rmub 'name'|num -- remove existing ub calculation
    """
    if isinstance(name_or_num, str):
        ubcalc.remove(name_or_num)
    else:
        ubcalc.remove(ubcalc.listub()[int(name_or_num)])

@command
def listub():
    """listub -- list the ub calculations available to load.
    """
    if hasattr(ubcalc._persister, 'description'):
        print "UB calculations in: " + ubcalc._persister.description
    else:
        print "UB calculations:"
    print
    ubnames = ubcalc.listub()
    # TODO: whole mechanism of making two calls is messy
    try:
        ub_metadata = ubcalc.listub_metadata()
    except AttributeError:
        ub_metadata = [''] * len(ubnames)
    
    for n, name, data in zip(range(len(ubnames)), ubnames, ub_metadata):
        print "%2i) %-15s %s" % (n, name, data)

@command
def saveubas(name):
    """saveubas 'name' -- save the ub calculation with a new name
    """
    if isinstance(name, str):
        # just trying might cause confusion here
        ubcalc.saveas(name)
    else:
        raise TypeError()

@command
def ub():
    """ub -- show the complete state of the ub calculation
    """
    #wavelength = float(hardware.get_wavelength())
    #energy = float(hardware.get_energy())
    print ubcalc.__str__()

@command
def refineub(*args):
    """
    refineub {[h k l]} {pos} -- refine unit cell dimensions and U matrix to match diffractometer angles for a given hkl value
    """
    if len(args) > 0:
        args = list(args)
        h, k, l = args.pop(0)
        if not (isnum(h) and isnum(k) and isnum(l)):
            raise TypeError()
    else:
        h = promptForNumber('h', 0.)
        k = promptForNumber('k', 0.)
        l = promptForNumber('l', 0.)
        if None in (h, k, l):
            _handleInputError("h,k and l must all be numbers")
    if len(args) == 1:
        pos = settings.geometry.physical_angles_to_internal_position(  # @UndefinedVariable
                args.pop(0))
    elif len(args) == 0:
        reply = promptForInput('current pos', 'y')
        if reply in ('y', 'Y', 'yes'):
            positionList = settings.hardware.get_position()  # @UndefinedVariable
        else:
            currentPos = settings.hardware.get_position()  # @UndefinedVariable
            positionList = []
            names = settings.hardware.get_axes_names()  # @UndefinedVariable
            for i, angleName in enumerate(names):
                val = promptForNumber(angleName.rjust(7), currentPos[i])
                if val is None:
                    _handleInputError("Please enter a number, or press"
                                          " Return to accept default!")
                    return
                positionList.append(val)
        pos = settings.geometry.physical_angles_to_internal_position(positionList)  # @UndefinedVariable
    else:
        raise TypeError()
    
    pos.changeToRadians()
    scale, lat = ubcalc.rescale_unit_cell(h, k, l, pos)
    if scale:
        lines = ["Unit cell scaling factor:".ljust(9) +
                         "% 9.5f" % scale]
        lines.append("Refined crystal lattice:")
        lines.append("   a, b, c:".ljust(9) +
                         "% 9.5f % 9.5f % 9.5f" % (lat[1:4]))
        lines.append(" " * 12 +
                         "% 9.5f % 9.5f % 9.5f" % (lat[4:]))
        lines.append("")
        print '\n'.join(lines)
        reply = promptForInput('Update crystal settings?', 'y')
        if reply in ('y', 'Y', 'yes'):
            ubcalc.set_lattice(*lat)
    else:
        print "No unit cell mismatch detected"
    mc_angle, mc_axis = ubcalc.calc_miscut(h, k, l, pos)
    if mc_angle:
        lines = ["Miscut parameters:",]
        lines.append("      angle:".ljust(9) + "% 9.5f" % mc_angle)
        lines.append("       axis:".ljust(9) + "% 9.5f % 9.5f % 9.5f" % tuple(mc_axis))
        print '\n'.join(lines)
        reply = promptForInput('Apply miscut parameters?', 'y')
        if reply in ('y', 'Y', 'yes'):
            ubcalc.set_miscut(mc_axis, -mc_angle * TORAD, True)
    else:
        print "No miscut detected for the given settings"
        ubcalc.set_miscut(None, 0, True)

### UB lattice ###

@command
def setlat(name=None, *args):
    """
    setlat  -- interactively enter lattice parameters (Angstroms and Deg)

    setlat name 'Cubic' a -- sets Cubic system
    setlat name 'Tetragonal' a c -- sets Tetragonal system
    setlat name 'Hexagonal' a c -- sets Hexagonal system
    setlat name 'Orthorhombic' a b c -- sets Orthorombic system
    setlat name 'Rhombohedral' a alpha -- sets Rhombohedral system
    setlat name 'Monoclinic' a b c beta -- sets Monoclinic system
    setlat name 'Triclinic' a b c alpha beta gamma -- sets Triclinic system

    setlat name a -- assumes Cubic system
    setlat name a b -- assumes Tetragonal system
    setlat name a b c -- assumes Orthorombic system
    setlat name a b c angle -- assumes Monoclinic system with beta not equal to 90 or
                                       Hexagonal system if a = b and gamma = 120
    setlat name a b c alpha beta gamma -- sets Triclinic system
    """

    if name is None:  # Interactive
        name = promptForInput("crystal name")
        system = None
        systen_dict = {1: "Triclinic",
                       2: "Monoclinic",
                       3: "Orthorhombic",
                       4: "Tetragonal",
                       5: "Rhombohedral",
                       6: "Hexagonal",
                       7: "Cubic"}
        while system is None:
            system_fmt = "\n".join(["crystal system",] + 
                                   ["%d) %s" % (k, v) 
                                    for (k, v) in systen_dict.items()] +
                                   ['',])
            system = promptForNumber(system_fmt, 1)
            if system not in systen_dict.keys():
                print "Invalid crystal system index selection.\n"
                print "Please select vale between 1 and 7."
                system = None
        a = promptForNumber('    a', 1)
        args = (a,)
        if system in (1, 2, 3):
            b = promptForNumber('    b', a)
            args += (b,)
        if system in (1, 2, 3, 4, 6):
            c = promptForNumber('    c', a)
            args += (c,)
        if system in (1, 5):
            alpha = promptForNumber('alpha', 90)
            args += (alpha,)
        if system in (1, 2):
            beta = promptForNumber('beta', 90)
            args += (beta,)
        if system in (1,):
            gamma = promptForNumber('gamma', 90)
            args += (gamma,)
        args = (systen_dict[system],) + args
    elif not isinstance(name, str):
        raise TypeError("Invalid crystal name.")
    ubcalc.set_lattice(name, *args)


@command
def c2th(hkl, en=None):
    """
    c2th [h k l]  -- calculate two-theta angle for reflection
    """
    if en is None:
        wl = settings.hardware.get_wavelength()  # @UndefinedVariable
    else:
        wl = 12.39842 / en
    d = ubcalc.get_hkl_plane_distance(hkl)
    if wl > (2 * d):
        raise ValueError(
            'Reflection un-reachable as wavelength (%f) is more than twice\n'
            'the plane distance (%f)' % (wl, d))
    try:
        return 2.0 * asin(wl / (d * 2)) * TODEG
    except ValueError as e:
        raise ValueError('asin(wl / (d * 2) with wl=%f and d=%f: ' %(wl, d) + e.args[0])
    

@command
def hklangle(hkl1, hkl2):
    """
    hklangle [h1 k1 l1] [h2 k2 l2]  -- calculate angle between [h1 k1 l1] and [h2 k2 l2] planes
    """
    return ubcalc.get_hkl_plane_angle(hkl1, hkl2) * TODEG

### Surface and reference vector stuff ###

@command
def sigtau(sigma=None, tau=None):
    """sigtau {sigma tau} -- sets or displays sigma and tau"""
    if sigma is None and tau is None:
        chi = settings.hardware.get_position_by_name('chi')  # @UndefinedVariable
        phi = settings.hardware.get_position_by_name('phi')  # @UndefinedVariable
        _sigma, _tau = ubcalc.sigma, ubcalc.tau
        print "sigma, tau = %f, %f" % (_sigma, _tau)
        print "  chi, phi = %f, %f" % (chi, phi)
        sigma = promptForInput("sigma", -chi)
        tau = promptForInput("  tau", -phi)
        ubcalc.sigma = sigma
        ubcalc.tau = tau
    else:
        ubcalc.sigma = float(sigma)
        ubcalc.tau = float(tau)


@command
def setnphi(xyz=None):
    """setnphi {[x y z]} -- sets or displays n_phi reference"""
    if xyz is None:
        ubcalc.print_reference()
    else:
        ubcalc.set_n_phi_configured(_to_column_vector_triple(xyz))
        ubcalc.print_reference()

@command
def setnhkl(hkl=None):
    """setnhkl {[h k l]} -- sets or displays n_hkl reference"""
    if hkl is None:
        ubcalc.print_reference()
    else:
        ubcalc.set_n_hkl_configured(_to_column_vector_triple(hkl))
        ubcalc.print_reference()
 
 
def _to_column_vector_triple(o):
    m = matrix(o)
    if m.shape == (1, 3):
        return m.T
    elif m.shape == (3, 1):
        return m
    else:
        raise ValueError("Unexpected shape matrix: " + m)
    
### UB refelections ###

@command
def showref():
    """showref -- shows full reflection list"""
    if ubcalc._state.reflist:
        print '\n'.join(ubcalc._state.reflist.str_lines())
    else:
        print "<<< No reflections stored >>>"

@command
def addref(*args):
    """
    addref -- add reflection interactively
    addref [h k l] {'tag'} -- add reflection with current position and energy
    addref [h k l] (p1, .., pN) energy {'tag'} -- add arbitrary reflection
    """

    multiplier = settings.hardware.energyScannableMultiplierToGetKeV
    if len(args) == 0:
        h = promptForNumber('h', 0.)
        k = promptForNumber('k', 0.)
        l = promptForNumber('l', 0.)
        if None in (h, k, l):
            _handleInputError("h,k and l must all be numbers")
        reply = promptForInput('current pos', 'y')
        if reply in ('y', 'Y', 'yes'):
            positionList = settings.hardware.get_position()  # @UndefinedVariable
            energy = settings.hardware.get_energy()  # @UndefinedVariable
        else:
            currentPos = settings.hardware.get_position()  # @UndefinedVariable
            positionList = []
            names = settings.hardware.get_axes_names()  # @UndefinedVariable
            for i, angleName in enumerate(names):
                val = promptForNumber(angleName.rjust(7), currentPos[i])
                if val is None:
                    _handleInputError("Please enter a number, or press"
                                          " Return to accept default!")
                    return
                positionList.append(val)
            energy = promptForNumber('energy', settings.hardware.get_energy() / multiplier)  # @UndefinedVariable
            if val is None:
                _handleInputError("Please enter a number, or press "
                                      "Return to accept default!")
                return
            energy *= multiplier
        tag = promptForInput("tag")
        if tag == '':
            tag = None
        pos = settings.geometry.physical_angles_to_internal_position(positionList)  # @UndefinedVariable
        ubcalc.add_reflection(h, k, l, pos, energy, tag,
                                   datetime.now())
    elif len(args) in (1, 2, 3, 4):
        args = list(args)
        h, k, l = args.pop(0)
        if not (isnum(h) and isnum(k) and isnum(l)):
            raise TypeError("h,k and l must all be numbers")
        if len(args) >= 2:
            pos = settings.geometry.physical_angles_to_internal_position(  # @UndefinedVariable
                args.pop(0))
            energy = args.pop(0) * multiplier
            if not isnum(energy):
                raise TypeError("Energy value must be a number")
        else:
            pos = settings.geometry.physical_angles_to_internal_position(  # @UndefinedVariable
                settings.hardware.get_position())  # @UndefinedVariable
            energy = settings.hardware.get_energy()  # @UndefinedVariable
        if len(args) == 1:
            tag = args.pop(0)
            if not isinstance(tag, str):
                raise TypeError("Tag value must be a string")
            if tag == '':
                tag = None
        else:
            tag = None
        ubcalc.add_reflection(h, k, l, pos, energy, tag,
                                   datetime.now())
    else:
        raise TypeError("Too many parameters specified for addref command.")

@command
def editref(idx):
    """editref {num | 'tag'} -- interactively edit a reflection.
    """

    # Get old reflection values
    [oldh, oldk, oldl], oldExternalAngles, oldEnergy, oldTag, oldT = \
        ubcalc.get_reflection_in_external_angles(idx)
    del oldT  # current time will be used.

    h = promptForNumber('h', oldh)
    k = promptForNumber('k', oldk)
    l = promptForNumber('l', oldl)
    if None in (h, k, l):
        _handleInputError("h,k and l must all be numbers")
    reply = promptForInput('update position with current hardware setting',
                           'n')
    if reply in ('y', 'Y', 'yes'):
        positionList = settings.hardware.get_position()  # @UndefinedVariable
        energy = settings.hardware.get_energy()  # @UndefinedVariable
    else:
        positionList = []
        names = settings.hardware.get_axes_names()  # @UndefinedVariable
        for i, angleName in enumerate(names):
            val = promptForNumber(angleName.rjust(7), oldExternalAngles[i])
            if val is None:
                _handleInputError("Please enter a number, or press "
                                      "Return to accept default!")
                return
            positionList.append(val)
        muliplier = settings.hardware.energyScannableMultiplierToGetKeV  # @UndefinedVariable
        energy = promptForNumber('energy', oldEnergy / muliplier)
        if val is None:
            _handleInputError("Please enter a number, or press Return "
                                  "to accept default!")
            return
        energy = energy * muliplier
    tag = promptForInput("tag", oldTag)
    if tag == '':
        tag = None
    pos = settings.geometry.physical_angles_to_internal_position(positionList)  # @UndefinedVariable
    ubcalc.edit_reflection(idx, h, k, l, pos, energy, tag,
                                datetime.now())

@command
def delref(idx):
    """delref {num | 'tag'} -- deletes a reflection
    """
    ubcalc.del_reflection(idx)
    
@command
def clearref():
    """clearref -- deletes all the reflections
    """
    while ubcalc.get_number_reflections():
        ubcalc.del_reflection(1)   

@command
def swapref(idx1=None, idx2=None):
    """
    swapref -- swaps first two reflections used for calculating U matrix
    swapref {num1 | 'tag1'} {num2 | 'tag2'} -- swaps two reflections
    """
    if idx1 is None and idx2 is None:
        ubcalc.swap_reflections(1, 2)
    elif idx1 is None or idx2 is None:
        raise TypeError("Please specify two reflection references to swap")
    else:
        ubcalc.swap_reflections(idx1, idx2)

### U calculation from crystal orientation
@command
def showorient():
    """showorient -- shows full list of crystal orientations"""
    if ubcalc._state.orientlist:
        print '\n'.join(ubcalc._state.orientlist.str_lines())
    else:
        print "<<< No crystal orientations stored >>>"

@command
def addorient(*args):
    """
    addorient -- add crystal orientation interactively
    addorient [h k l] [x y z] {'tag'} -- add crystal orientation in laboratory frame
    """

    if len(args) == 0:
        h = promptForNumber('h', 0.)
        k = promptForNumber('k', 0.)
        l = promptForNumber('l', 0.)
        if None in (h, k, l):
            _handleInputError("h,k and l must all be numbers")

        x = promptForNumber('x', 0.)
        y = promptForNumber('y', 0.)
        z = promptForNumber('z', 0.)
        if None in (x, y, z):
            _handleInputError("x,y and z must all be numbers")

        tag = promptForInput("tag")
        if tag == '':
            tag = None
        ubcalc.add_orientation(h, k, l, x , y, z, tag,
                                   datetime.now())
    elif len(args) in (1, 2, 3):
        args = list(args)
        h, k, l = args.pop(0)
        if not (isnum(h) and isnum(k) and isnum(l)):
            raise TypeError("h,k and l must all be numbers")
        x, y, z = args.pop(0)
        if not (isnum(x) and isnum(y) and isnum(z)):
            raise TypeError("x,y and z must all be numbers")
        if len(args) == 1:
            tag = args.pop(0)
            if not isinstance(tag, str):
                raise TypeError("Tag value must be a string.")
            if tag == '':
                tag = None
        else:
            tag = None
        ubcalc.add_orientation(h, k, l, x, y ,z, tag,
                                   datetime.now())
    else:
        raise TypeError("Too many parameters specified for addorient command.")

@command
def editorient(idx):
    """editorient num | 'tag' -- interactively edit a crystal orientation.
    """

    # Get old reflection values
    [oldh, oldk, oldl], [oldx, oldy, oldz], oldTag, oldT = \
        ubcalc.get_orientation(idx, True)
    del oldT  # current time will be used.

    h = promptForNumber('h', oldh)
    k = promptForNumber('k', oldk)
    l = promptForNumber('l', oldl)
    if None in (h, k, l):
        _handleInputError("h,k and l must all be numbers")
    x = promptForNumber('x', oldx)
    y = promptForNumber('y', oldy)
    z = promptForNumber('z', oldz)
    if None in (x, y, z):
        _handleInputError("x,y and z must all be numbers")
    tag = promptForInput("tag", oldTag)
    if tag == '':
        tag = None
    ubcalc.edit_orientation(idx, h, k, l, x, y, z, tag,
                                datetime.now())

@command
def delorient(idx):
    """delorient num | 'tag' -- deletes a crystal orientation
    """
    ubcalc.del_orientation(idx)
    
@command
def clearorient():
    """clearorient -- deletes all the crystal orientations
    """
    while ubcalc.get_number_orientations():
        ubcalc.del_orientation(1)

@command
def swaporient(idx1=None, idx2=None):
    """
    swaporient -- swaps first two crystal orientations used for calculating U matrix
    swaporient {num1 | 'tag1'} {num2 | 'tag2'} -- swaps two crystal orientations
    """
    if idx1 is None and idx2 is None:
        ubcalc.swap_orientations(1, 2)
    elif idx1 is None or idx2 is None:
        raise TypeError("Please specify two orientation references to swap")
    else:
        ubcalc.swap_orientations(idx1, idx2)


### UB calculations ###

@command
def setu(U=None):
    """setu {[[..][..][..]]} -- manually set U matrix
    """
    if U is None:
        U = _promptFor3x3MatrixDefaultingToIdentity()
        if U is None:
            return  # an error will have been printed or thrown
    if _is3x3TupleOrList(U) or _is3x3Matrix(U):
        ubcalc.set_U_manually(U)
    else:
        raise TypeError("U must be given as 3x3 list or tuple")

@command
def setub(UB=None):
    """setub {[[..][..][..]]} -- manually set UB matrix"""
    if UB is None:
        UB = _promptFor3x3MatrixDefaultingToIdentity()
        if UB is None:
            return  # an error will have been printed or thrown
    if _is3x3TupleOrList(UB):
        ubcalc.set_UB_manually(UB)
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
def calcub(idx1=None, idx2=None):
    """
    calcub -- (re)calculate U matrix from the first two reflections and/or orientations.
    calcub idx1 idx2 -- (re)calculate U matrix from reflections and/or orientations referred by indices and/or tags idx1 and idx2.
    """
    ubcalc.calculate_UB(idx1, idx2)

@command
def trialub(idx=1):
    """trialub -- (re)calculate U matrix from reflection with index or tag idx only (check carefully). Default: use first reflection.
    """
    ubcalc.calculate_UB(idx)

@command
def orientub(idx1=None, idx2=None):
    """
    DEPRECATED. Please use 'calcub' command.
    orientub -- (re)calculate U matrix from the first two reflections and/or orientations.
    orientub idx1 idx2 -- (re)calculate U matrix from reflections and/or orientations referred by indices and/or tags idx1 and idx2.
    """
    ubcalc.calculate_UB(idx1, idx2)

@command
def fitub(*args):
    """fitub ref1, ref2, ref3... -- fit UB matrix to match list of provided reference reflections."""
    new_umatrix, new_lattice = ubcalc.fit_ub_matrix(*args)
    ubcalc.set_lattice(*new_lattice)
    ubcalc.set_U_manually(new_umatrix, False)

    # This command requires the ubcalc

def checkub():
    """checkub -- show calculated and entered hkl values for reflections.
    """

    s = "\n    %7s  %4s  %4s  %4s    %6s   %6s   %6s     TAG\n" % \
    ('ENERGY', 'H', 'K', 'L', 'H_COMP', 'K_COMP', 'L_COMP')
    s = bold(s)
    nref = ubcalc.get_number_reflections()
    if not nref:
        s += "<<empty>>"
    for n in range(nref):
        hklguess, pos, energy, tag, _ = ubcalc.get_reflection(n + 1)
        wavelength = 12.39842 / energy
        hkl = settings.angles_to_hkl_function(pos.inRadians(), wavelength, ubcalc.UB)
        h, k, l = hkl
        if tag is None:
            tag = ""
        s += ("% 2d % 6.4f % 4.2f % 4.2f % 4.2f   % 6.4f  % 6.4f  "
              "% 6.4f  %6s\n" % (n + 1, energy, hklguess[0],
              hklguess[1], hklguess[2], h, k, l, tag))
    print s


@command
def addmiscut(*args):
    """addmiscut angle {[x y z]} -- apply miscut to U matrix using a specified miscut angle in degrees and a rotation axis"""
    
    if len(args) == 0:
        _handleInputError("Please specify a miscut angle in degrees "
                          "and, optionally, a rotation axis (default: [0 1 0])")
    else:
        args=list(args)
        angle = args.pop(0)
        rad_angle = float(angle) * TORAD
        if len(args) == 0:
            xyz = None
        else:
            xyz = args.pop(0)
        ubcalc.set_miscut(xyz, rad_angle, True)

@command
def setmiscut(*args):
    """setmiscut angle {[x y z]} -- manually set U matrix using a specified miscut angle in degrees and a rotation axis (default: [0 1 0])"""
    
    if len(args) == 0:
        _handleInputError("Please specify a miscut angle in degrees "
                          "and, optionally, a rotation axis (default: [0 1 0])")
    else:
        args=list(args)
        angle = args.pop(0)
        rad_angle = float(angle) * TORAD
        if len(args) == 0:
            xyz = None
        else:
            xyz = args.pop(0)
        ubcalc.set_miscut(xyz, rad_angle, False)

commands_for_help = ['State',
                     newub,
                     loadub,
                     lastub,
                     listub,
                     rmub,
                     saveubas,
                     ub,
                     'Lattice',
                     setlat,
                     c2th,
                     hklangle]

if ubcalc.include_reference:
    commands_for_help.extend([
                     'Reference (surface)',
                     setnphi,
                     setnhkl])

if ubcalc.include_sigtau:
    commands_for_help.extend([
                     'Surface',
                     sigtau])

commands_for_help.extend([
                     'Reflections',
                     showref,
                     addref,
                     editref,
                     delref,
                     clearref,
                     swapref,
                     'Orientations',
                     showorient,
                     addorient,
                     editorient,
                     delorient,
                     clearorient,
                     swaporient,
                     'UB matrix',
                     fitub,
                     checkub,
                     setu,
                     setub,
                     calcub,
                     orientub,
                     trialub,
                     refineub,
                     addmiscut,
                     setmiscut])



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


def _is3x3Matrix(m):
    return isinstance(m, matrix) and tuple(m.shape) == (3, 3)
        

def _handleInputError(msg):
    raise TypeError(msg)