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

from diffcalc.ub.calcstate import decode_ubcalcstate
from diffcalc.ub.calcstate import UBCalcState
from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.ub.reflections import ReflectionList
from diffcalc.util import DiffcalcException, cross3, dot3
from math import acos, cos, sin, pi
from diffcalc.ub.reference import YouReference

try:
    from numpy import matrix, hstack
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix, hstack
    from numjy.linalg import norm

from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.ub.reflections import ReflectionList
from diffcalc.util import DiffcalcException, cross3, dot3

SMALL = 1e-7
TODEG = 180 / pi


#The UB matrix is used to find or set the orientation of a set of
#planes described by an hkl vector. The U matrix can be used to find
#or set the orientation of the crystal lattices' y axis. If there is
#crystal miscut the crystal lattices y axis is not parallel to the
#crystals optical surface normal. For surface diffraction experiments,
#where not only the crystal lattice must be oriented appropriately but
#so must the crystal's optical surface, two angles tau and sigma are
#used to describe the difference between the two. Sigma is (minus) the
#ammount of chi axis rotation and tau (minus) the ammount of phi axis
#rotation needed to move the surface normal into the direction of the


class PaperSpecificUbCalcStrategy(object):

    def calculate_q_phi(self, pos):
        """Calculate hkl in the phi frame in units of 2 * pi / lambda from
        pos object in radians"""
        raise NotImplementedError()


class UBCalculation:
    """A UB matrix calculation for an experiment.

    Contains the parameters for the _crystal under test, a list of measured
    reflections and, if its been calculated, a UB matrix to be used by the rest
    of the code.
    """

    def __init__(self, diffractometer_axes_names, diffractometerPluginObject,
                 persister, strategy, include_sigtau=True):

        # The diffractometer geometry is required to map the internal angles
        # into those used by this diffractometer (for display only)

        self._diffractometer_axes_names = diffractometer_axes_names
        self._geometry = diffractometerPluginObject
        self._persister = persister
        self._strategy = strategy
        self._include_sigtau = include_sigtau
        self.reference = YouReference(self)  # TODO: move into _state and persist
        self._clear()

    def _clear(self, name=None):
        # NOTE the Diffraction calculator is expecting this object to exist in
        # the long run. We can't remove this entire object, and recreate it.
        # It also contains a required link to the angle calculator.
        reflist = ReflectionList(self._geometry, self._diffractometer_axes_names)
        self._state = UBCalcState(name=name, reflist=reflist)
        self._U = None
        self._UB = None
        self._state.configure_calc_type()

### State ###
    def start_new(self, name):
        """start_new(name) --- creates a new blank ub calculation"""
        # Create storage object if name does not exist (TODO)
        if name in self._persister.list():
            print ("No UBCalculation started: There is already a calculation "
                   "called: " + name)
            print "Saved calculations: " + repr(self._persister.list())
            return
        self._clear(name)
        self.save()

    def load(self, name):
        state = self._persister.load(name)
        self._state = decode_ubcalcstate(state, self._geometry, self._diffractometer_axes_names)
        if self._state.manual_U is not None:
            self.set_U_manually(self._state.manual_U)
        elif self._state.manual_UB is not None:
            self.set_UB_manually(self._state.manual_UB)
        elif self._state.or0 is not None:
            if self._state.or1 is None:
                self.calculate_UB_from_primary_only()
            else:
                self.calculate_UB()
        else:
            pass
    def save(self):
        self.saveas(self._state.name)

    def saveas(self, name):
        self._state.name = name
        self._persister.save(self._state, name)

    def listub(self):
        return self._persister.list()

    def remove(self, name):
        self._persister.remove(name)

    def getState(self):
        return self._state.getState()

    def __str__(self):
        WIDTH = 13

        if self._state.name is None:
            return "<<< No UB calculation started >>>"
        lines = []
        lines.append("UBCALC")
        lines.append("")
        lines.append(
            "   name:".ljust(WIDTH) + self._state.name.rjust(9))
        if self._include_sigtau:
            lines.append(
                "   sigma:".ljust(WIDTH) + ("% 9.5f" % self._state.sigma).rjust(9))
            lines.append(
                "   tau:".ljust(WIDTH) + ("% 9.5f" % self._state.tau).rjust(9))

        lines.append("")
        lines.append("CRYSTAL")
        lines.append("")
        if self._state.crystal is None:
            lines.append("   <<< none specified >>>")
        else:
            lines.extend(self._state.crystal.str_lines())

        lines.append("")
        lines.append("UB MATRIX")
        lines.append("")
        if self._UB is None:
            lines.append("   <<< none calculated >>>")
        else:
            fmt = "% 9.5f % 9.5f % 9.5f"
            U = self.U
            UB = self.UB
            lines.append("   U matrix:".ljust(WIDTH) +
                         fmt % (U[0, 0], U[0, 1], U[0, 2]))
            lines.append(' ' * WIDTH + fmt % (U[1, 0], U[1, 1], U[1, 2]))
            lines.append(' ' * WIDTH + fmt % (U[2, 0], U[2, 1], U[2, 2]))
            lines.append("")

            lines.append("   UB matrix:".ljust(WIDTH) +
                         fmt % (UB[0, 0], UB[0, 1], UB[0, 2]))
            lines.append(' ' * WIDTH + fmt % (UB[1, 0], UB[1, 1], UB[1, 2]))
            lines.append(' ' * WIDTH + fmt % (UB[2, 0], UB[2, 1], UB[2, 2]))

        lines.append("")
        lines.append("REFLECTIONS")
        lines.append("")
        lines.extend(self._state.reflist.str_lines())
        return '\n'.join(lines)

    @property
    def name(self):
        return self._state.name
### Lattice ###

    def set_lattice(self, name, *shortform):
        """
        Converts a list shortform crystal parameter specification to a six-long
        tuple returned as . Returns None if wrong number of input args. See
        set_lattice() for a description of the shortforms supported.

        shortformLattice -- a tuple as follows:
             [a]         - assumes cubic
           [a,b])       - assumes tetragonal
           [a,b,c])     - assumes ortho
           [a,b,c,gam]) - assumes mon/hex gam different from 90.
           [a,b,c,alp,bet,gam]) - for arbitrary
           where all measurements in angstroms and angles in degrees
        """
        self._set_lattice_without_saving(name, *shortform)
        self.save()

    def _set_lattice_without_saving(self, name, *shortform):
        sf = shortform
        if len(sf) == 1:
            fullform = (sf[0], sf[0], sf[0], 90., 90., 90.)  # cubic
        elif len(sf) == 2:
            fullform = (sf[0], sf[0], sf[1], 90., 90., 90.)  # tetragonal
        elif len(sf) == 3:
            fullform = (sf[0], sf[1], sf[2], 90., 90., 90.)  # ortho
        elif len(sf) == 4:
            fullform = (sf[0], sf[1], sf[2], 90., 90., sf[3])   # mon/hex gam
                                                                # not 90
        elif len(sf) == 5:
            raise ValueError("wrong length input to set_lattice")
        elif len(sf) == 6:
            fullform = sf  # triclinic/arbitrary
        else:
            raise ValueError("wrong length input to set_lattice")
        self._set_lattice(name, *fullform)

    def _set_lattice(self, name, a, b, c, alpha, beta, gamma):
        """set lattice parameters in degrees"""
        if self._state.name is None:
            raise DiffcalcException(
                "Cannot set lattice until a UBCalcaluation has been started "
                "with newubcalc")
        self._state.crystal = CrystalUnderTest(name, a, b, c, alpha, beta, gamma)
        # Clear U and UB if these exist
        if self._U != None:  # (UB will also exist)
            self._U = None
            self._UB = None
            print "Warning: the old UB calculation has been cleared."
            print "         Use 'calcub' to recalculate with old reflections."

### Surface normal stuff ###

    def _gettau(self):
        """
        Returns tau (in degrees): the (minus) ammount of phi axis rotation ,
        that together with some chi axis rotation (minus sigma) brings the
        optical surface normal parallelto the omega axis.
        """
        return self._state.tau

    def _settau(self, tau):
        self._state.tau = tau
        self.save()

    tau = property(_gettau, _settau)

    def _getsigma(self):
        """
        Returns sigma (in degrees): the (minus) ammount of phi axis rotation ,
        that together with some phi axis rotation (minus tau) brings the
        optical surface normal parallelto the omega axis.
        """
        return self._state.sigma

    def _setsigma(self, sigma):
        self.state._sigma = sigma
        self.save()

    sigma = property(_getsigma, _setsigma)

### Reflections ###

    def add_reflection(self, h, k, l, position, energy, tag, time):
        """add_reflection(h, k, l, position, tag=None) -- adds a reflection

        position is in degrees and in the systems internal representation.
        """
        if self._state.reflist is None:
            raise DiffcalcException("No UBCalculation loaded")
        self._state.reflist.add_reflection(h, k, l, position, energy, tag, time)
        self.save()  # incase autocalculateUbAndReport fails

        # If second reflection has just been added then calculateUB
        if len(self._state.reflist) == 2:
            self._autocalculateUbAndReport()
        self.save()

    def edit_reflection(self, num, h, k, l, position, energy, tag, time):
        """
        edit_reflection(num, h, k, l, position, tag=None) -- adds a reflection

        position is in degrees and in the systems internal representation.
        """
        if self._state.reflist is None:
            raise DiffcalcException("No UBCalculation loaded")
        self._state.reflist.edit_reflection(num, h, k, l, position, energy, tag, time)

        # If first or second reflection has been changed and there are at least
        # two reflections then recalculate  UB
        if (num == 1 or num == 2) and len(self._state.reflist) >= 2:
            self._autocalculateUbAndReport()
        self.save()

    def get_reflection(self, num):
        """--> ( [h, k, l], position, energy, tag, time
        num starts at 1, position in degrees"""
        return self._state.reflist.getReflection(num)

    def get_reflection_in_external_angles(self, num):
        """--> ( [h, k, l], position, energy, tag, time
        num starts at 1, position in degrees"""
        return self._state.reflist.get_reflection_in_external_angles(num)
    
    def get_number_reflections(self):
        return 0 if self._state.reflist is None else len(self._state.reflist)

    def del_reflection(self, reflectionNumber):
        self._state.reflist.removeReflection(reflectionNumber)
        if ((reflectionNumber == 1 or reflectionNumber == 2) and
            (self._U != None)):
            self._autocalculateUbAndReport()
        self.save()

    def swap_reflections(self, num1, num2):
        self._state.reflist.swap_reflections(num1, num2)
        if ((num1 == 1 or num1 == 2 or num2 == 1 or num2 == 2) and
            (self._U != None)):
            self._autocalculateUbAndReport()
        self.save()

    def _autocalculateUbAndReport(self):
        if len(self._state.reflist) < 2:
            pass
        elif self._state.crystal is None:
            print ("Not calculating UB matrix as no lattice parameters have "
                   "been specified.")
        elif not self._state.is_okay_to_autocalculate_ub:
            print ("Not calculating UB matrix as it has been manually set. "
                   "Use 'calcub' to explicitly recalculate it.")
        else:  # okay to autocalculate
            if self._UB is None:
                print "Calculating UB matrix."
            else:
                print "Recalculating UB matrix."
            self.calculate_UB()

#    @property
#    def reflist(self):
#        return self._state.reflist
### Calculations ###

    def set_U_manually(self, m):
        """Manually sets U. matrix must be 3*3 Jama or python matrix.
        Turns off aution UB calcualtion."""

        # Check matrix is a 3*3 Jama matrix
        if m.__class__ != matrix:
            m = matrix(m)  # assume its a python matrix
        if m.shape[0] != 3 or m.shape[1] != 3:
            raise  ValueError("Expects 3*3 matrix")

        if self._UB is None:
            print "Calculating UB matrix."
        else:
            print "Recalculating UB matrix."

        self._state.configure_calc_type(manual_U=m)
        self._U = m
        if self._state.crystal is None:
            raise DiffcalcException(
                "A crystal must be specified before manually setting U")
        self._UB = self._U * self._state.crystal.B
        print ("NOTE: A new UB matrix will not be automatically calculated "
               "when the orientation reflections are modified.")
        self.save()

    def set_UB_manually(self, m):
        """Manually sets UB. matrix must be 3*3 Jama or python matrix.
        Turns off aution UB calcualtion."""

        # Check matrix is a 3*3 Jama matrix
        if m.__class__ != matrix:
            m = matrix(m)  # assume its a python matrix
        if m.shape[0] != 3 or m.shape[1] != 3:
            raise  ValueError("Expects 3*3 matrix")

        self._state.configure_calc_type(manual_UB=m)
        self._UB = m
        self.save()

    @property
    def U(self):
        if self._U is None:
            raise DiffcalcException(
                "No U matrix has been calculated during this ub calculation")
        return self._U

    @property
    def UB(self):
        if self._UB is None:
            raise DiffcalcException(
                "No UB matrix has been calculated during this ub calculation")
        else:
            return self._UB

    def calculate_UB(self):
        """
        Calculate orientation matrix. Uses first two orientation reflections
        as in Busang and Levy, but for the diffractometer in Lohmeier and
        Vlieg.
        """

        # Major variables:
        # h1, h2: user input reciprical lattice vectors of the two reflections
        # h1c, h2c: user input vectors in cartesian crystal plane
        # pos1, pos2: measured diffractometer positions of the two reflections
        # u1a, u2a: measured reflection vectors in alpha frame
        # u1p, u2p: measured reflection vectors in phi frame


        # Get hkl and angle values for the first two refelctions
        if self._state.reflist is None:
            raise DiffcalcException("Cannot calculate a U matrix until a "
                                    "UBCalculation has been started with "
                                    "'newub'")
        try:
            (h1, pos1, _, _, _) = self._state.reflist.getReflection(1)
            (h2, pos2, _, _, _) = self._state.reflist.getReflection(2)
        except IndexError:
            raise DiffcalcException(
                "Two reflections are required to calculate a u matrix")
        h1 = matrix([h1]).T  # row->column
        h2 = matrix([h2]).T
        pos1.changeToRadians()
        pos2.changeToRadians()

        # Compute the two reflections' reciprical lattice vectors in the
        # cartesian crystal frame
        B = self._state.crystal.B
        h1c = B * h1
        h2c = B * h2

        u1p = self._strategy.calculate_q_phi(pos1)
        u2p = self._strategy.calculate_q_phi(pos2)

        # Create modified unit vectors t1, t2 and t3 in crystal and phi systems
        t1c = h1c
        t3c = cross3(h1c, h2c)
        t2c = cross3(t3c, t1c)

        t1p = u1p  # FIXED from h1c 9July08
        t3p = cross3(u1p, u2p)
        t2p = cross3(t3p, t1p)

        # ...and nornmalise and check that the reflections used are appropriate
        SMALL = 1e-4  # Taken from Vlieg's code
        e = DiffcalcException("Invalid orientation reflection(s)")

        def normalise(m):
            d = norm(m)
            if d < SMALL:
                raise e
            return m / d

        t1c = normalise(t1c)
        t2c = normalise(t2c)
        t3c = normalise(t3c)

        t1p = normalise(t1p)
        t2p = normalise(t2p)
        t3p = normalise(t3p)

        Tc = hstack([t1c, t2c, t3c])
        Tp = hstack([t1p, t2p, t3p])
        self._state.configure_calc_type(or0=1, or1=2)
        self._U = Tp * Tc.I
        self._UB = self._U * B
        self.save()

    def calculate_UB_from_primary_only(self):
        """
        Calculate orientation matrix with the shortest absolute angle change.
        Uses first orientation reflection
        """

        # Algorithm from http://www.j3d.org/matrix_faq/matrfaq_latest.html

        # Get hkl and angle values for the first two refelctions
        if self._state.reflist is None:
            raise DiffcalcException(
                "Cannot calculate a u matrix until a UBCalcaluation has been "
                "started with newub")
        try:
            (h, pos, _, _, _) = self._state.reflist.getReflection(1)
        except IndexError:
            raise DiffcalcException(
                "One reflection is required to calculate a u matrix")

        h = matrix([h]).T  # row->column
        pos.changeToRadians()
        B = self._state.crystal.B
        h_crystal = B * h
        h_crystal = h_crystal * (1 / norm(h_crystal))

        q_measured_phi = self._strategy.calculate_q_phi(pos)
        q_measured_phi = q_measured_phi * (1 / norm(q_measured_phi))

        rotation_axis = cross3(h_crystal, q_measured_phi)
        rotation_axis = rotation_axis * (1 / norm(rotation_axis))

        cos_rotation_angle = dot3(h_crystal, q_measured_phi)
        rotation_angle = acos(cos_rotation_angle)

        uvw = rotation_axis.T.tolist()[0]  # TODO: cleanup
        print "resulting U angle: %.5f deg" % (rotation_angle * TODEG)
        u_repr = (', '.join(['% .5f' % el for el in uvw]))
        print "resulting U axis direction: [%s]" % u_repr

        u, v, w = uvw
        rcos = cos(rotation_angle)
        rsin = sin(rotation_angle)
        m = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  # TODO: tidy
        m[0][0] = rcos + u * u * (1 - rcos)
        m[1][0] = w * rsin + v * u * (1 - rcos)
        m[2][0] = -v * rsin + w * u * (1 - rcos)
        m[0][1] = -w * rsin + u * v * (1 - rcos)
        m[1][1] = rcos + v * v * (1 - rcos)
        m[2][1] = u * rsin + w * v * (1 - rcos)
        m[0][2] = v * rsin + u * w * (1 - rcos)
        m[1][2] = -u * rsin + v * w * (1 - rcos)
        m[2][2] = rcos + w * w * (1 - rcos)

        if self._UB is None:
            print "Calculating UB matrix from the first reflection only."
        else:
            print "Recalculating UB matrix from the first reflection only."
        print ("NOTE: A new UB matrix will not be automatically calculated "
               "when the orientation reflections are modified.")

        self._state.configure_calc_type(or0=1)
        
        self._U = matrix(m)
        self._UB = self._U * B

        self.save()

    def get_hkl_plane_distance(self, hkl):
        """Calculates and returns the distance between planes"""
        return self._state.crystal.get_hkl_plane_distance(hkl)
