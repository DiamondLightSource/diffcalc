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
    promptForNumber, promptForList, allnum, isnum, bold, xyz_rotation
from diffcalc.util import command

TORAD = pi / 180
TODEG = 180 / pi


# When using ipython magic, these functions must not be imported to the top
# level namespace. Doing so will stop them from being called with magic.

__all__ = ['addorient', 'addref', 'c2th', 'calcub', 'delorient', 'delref', 'editorient',
           'editref', 'listub', 'loadub', 'newub', 'orientub', 'saveubas', 'setlat',
           'addmiscut', 'setmiscut', 'setu', 'setub', 'showorient', 'showref', 'swaporient',
           'swapref', 'trialub', 'checkub', 'ub', 'ubcalc', 'rmub', 'clearorient',
           'clearref', 'lastub']

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
        ubcalc.set_lattice(name, a, b, c, alpha, beta, gamma)

    elif (isinstance(name, str) and
          len(args) in (1, 2, 3, 4, 6) and
          allnum(args)):
        # first arg is string and rest are numbers
        ubcalc.set_lattice(name, *args)
    else:
        raise TypeError()

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
def setnphi(xyz = None):
    """setnphi {[x y z]} -- sets or displays n_phi reference"""
    if xyz is None:
        ubcalc.print_reference()
    else:
        ubcalc.set_n_phi_configured(_to_column_vector_triple(xyz))
        ubcalc.print_reference()

@command
def setnhkl(hkl):
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
            muliplier = settings.hardware.energyScannableMultiplierToGetKeV  # @UndefinedVariable
            energy = promptForNumber('energy', settings.hardware.get_energy() / muliplier)  # @UndefinedVariable
            if val is None:
                _handleInputError("Please enter a number, or press "
                                      "Return to accept default!")
                return
            energy = energy * muliplier
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
            raise TypeError()
        if len(args) >= 2:
            pos = settings.geometry.physical_angles_to_internal_position(  # @UndefinedVariable
                args.pop(0))
            energy = args.pop(0)
            if not isnum(energy):
                raise TypeError()
        else:
            pos = settings.geometry.physical_angles_to_internal_position(  # @UndefinedVariable
                settings.hardware.get_position())  # @UndefinedVariable
            energy = settings.hardware.get_energy()  # @UndefinedVariable
        if len(args) == 1:
            tag = args.pop(0)
            if not isinstance(tag, str):
                raise TypeError()
        else:
            tag = None
        ubcalc.add_reflection(h, k, l, pos, energy, tag,
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
        ubcalc.get_reflection_in_external_angles(num)
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
    ubcalc.edit_reflection(num, h, k, l, pos, energy, tag,
                                datetime.now())

@command
def delref(num):
    """delref num -- deletes a reflection (numbered from 1)
    """
    ubcalc.del_reflection(int(num))
    
@command
def clearref():
    """clearref -- deletes all the reflections
    """
    while ubcalc.get_number_reflections():
        ubcalc.del_reflection(1)   

@command
def swapref(num1=None, num2=None):
    """
    swapref -- swaps first two reflections used for calulating U matrix
    swapref num1 num2 -- swaps two reflections (numbered from 1)
    """
    if num1 is None and num2 is None:
        ubcalc.swap_reflections(1, 2)
    elif isinstance(num1, int) and isinstance(num2, int):
        ubcalc.swap_reflections(num1, num2)
    else:
        raise TypeError()

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
            raise TypeError()
        x, y, z = args.pop(0)
        if not (isnum(x) and isnum(y) and isnum(z)):
            raise TypeError()
        if len(args) == 1:
            tag = args.pop(0)
            if not isinstance(tag, str):
                raise TypeError()
        else:
            tag = None
        ubcalc.add_orientation(h, k, l, x, y ,z, tag,
                                   datetime.now())
    else:
        raise TypeError()

@command
def editorient(num):
    """editorient num -- interactively edit a crystal orientation.
    """
    num = int(num)

    # Get old reflection values
    [oldh, oldk, oldl], [oldx, oldy, oldz], oldTag, oldT = \
        ubcalc.get_orientation(num)
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
    ubcalc.edit_orientation(num, h, k, l, x, y, z, tag,
                                datetime.now())

@command
def delorient(num):
    """delorient num -- deletes a crystal orientation (numbered from 1)
    """
    ubcalc.del_orientation(int(num))
    
@command
def clearorient():
    """clearorient -- deletes all the crystal orientations
    """
    while ubcalc.get_number_orientations():
        ubcalc.del_orientation(1)

@command
def swaporient(num1=None, num2=None):
    """
    swaporient -- swaps first two crystal orientations used for calulating U matrix
    swaporient num1 num2 -- swaps two crystal orientations (numbered from 1)
    """
    if num1 is None and num2 is None:
        ubcalc.swap_orientations(1, 2)
    elif isinstance(num1, int) and isinstance(num2, int):
        ubcalc.swap_orientations(num1, num2)
    else:
        raise TypeError()


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
def calcub():
    """calcub -- (re)calculate U matrix from ref1 and ref2.
    """
    ubcalc.calculate_UB()

@command
def trialub():
    """trialub -- (re)calculate U matrix from ref1 only (check carefully).
    """
    ubcalc.calculate_UB_from_primary_only()

@command
def orientub():
    """orientub -- (re)calculate U matrix from orient1 and orient2.
    """
    ubcalc.calculate_UB_from_orientation()


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
            xyz =  [0, 1, 0]
        else:
            xyz = args.pop(0)
        rot_matrix = xyz_rotation(xyz, rad_angle)
        if ubcalc.is_ub_calculated():
            ubcalc.set_U_manually(rot_matrix * ubcalc.U)
        else:
            ubcalc.set_U_manually(rot_matrix)
        ubcalc.print_reference()

@command
def setmiscut(*args):
    """setmiscut angle {[x y z]} -- manually set U matrix using a specified miscut angle in degrees and a rotation axis (default: [0 1 0])"""
    
    if len(args) == 0:
        _handleInputError("Please specify a miscut angle in degrees "
                          "and, optionally, a rotation axis (default: [0 1 0])")
    else:
        ubcalc.set_U_manually(matrix('1 0 0; 0 1 0; 0 0 1'))
        addmiscut(*args)

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
                     c2th]

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
                     checkub,
                     setu,
                     setub,
                     calcub,
                     orientub,
                     trialub,
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