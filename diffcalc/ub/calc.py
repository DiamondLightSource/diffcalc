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

from diffcalc.ub.calcstate import UBCalcState
from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.ub.reflections import ReflectionList
from diffcalc.ub.persistence import UBCalculationJSONPersister, UBCalculationPersister
from diffcalc.util import DiffcalcException, cross3, dot3, bold, xyz_rotation,\
    bound, angle_between_vectors, norm3
from math import acos, cos, sin, pi, atan2
from diffcalc.ub.reference import YouReference
from diffcalc.ub.orientations import OrientationList

try:
    from numpy import matrix, hstack
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix, hstack
    from numjy.linalg import norm

SMALL = 1e-7
TODEG = 180 / pi

WIDTH = 13

def z(num):
    """Round to zero if small. This is useful to get rid of erroneous
    minus signs resulting from float representation close to zero.
    """
    if abs(num) < SMALL:
        num = 0
    return num

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

    def __init__(self, hardware, diffractometerPluginObject,
                 persister, strategy, include_sigtau=True, include_reference=True):

        # The diffractometer geometry is required to map the internal angles
        # into those used by this diffractometer (for display only)

        self._hardware = hardware
        self._geometry = diffractometerPluginObject
        self._persister = persister
        self._strategy = strategy
        self.include_sigtau = include_sigtau
        self.include_reference = include_reference
        try:
            self._ROT = diffractometerPluginObject.beamline_axes_transform
        except AttributeError:
            self._ROT = None
        self._clear()
        
    def _get_diffractometer_axes_names(self):
        return self._hardware.get_axes_names()

    def _clear(self, name=None):
        # NOTE the Diffraction calculator is expecting this object to exist in
        # the long run. We can't remove this entire object, and recreate it.
        # It also contains a required link to the angle calculator.
        reflist = ReflectionList(self._geometry, self._get_diffractometer_axes_names(),
                                 multiplier=self._hardware.energyScannableMultiplierToGetKeV)
        orientlist = OrientationList()
        reference = YouReference(self._get_UB)
        self._state = UBCalcState(name=name, reflist=reflist, orientlist=orientlist, reference=reference)
        self._U = None
        self._UB = None
        self._state.configure_calc_type()

### State ###
    def start_new(self, name):
        """start_new(name) --- creates a new blank ub calculation"""
        # Create storage object if name does not exist (TODO)
        self._clear(name)
        self.save()

    def load(self, name):
        state = self._persister.load(name)
        if isinstance(self._persister, UBCalculationJSONPersister):
            self._state = self._persister.encoder.decode_ubcalcstate(state,
                                                                     self._geometry,
                                                                     self._get_diffractometer_axes_names(),
                                                                     self._hardware.energyScannableMultiplierToGetKeV)
            self._state.reference.get_UB = self._get_UB
        elif isinstance(self._persister, UBCalculationPersister):
            self._state = state
        else:
            raise Exception('Unexpected persister type: ' + str(self._persister))
        if self._state.manual_U is not None:
            self._U = self._state.manual_U
            self._UB = self._U * self._state.crystal.B
            self.save()
        elif self._state.manual_UB is not None:
            self._UB = self._state.manual_UB
            self.save()
        elif self._state.or0 is not None:
            if self._state.or1 is None:
                try:
                    self.calculate_UB_from_primary_only()
                except DiffcalcException, e:
                    print e
            else:
                if self._state.reflist:
                    try:
                        self.calculate_UB()
                    except DiffcalcException, e:
                        print e
                elif self._state.orientlist:
                    try:
                        self.calculate_UB_from_orientation()
                    except DiffcalcException, e:
                        print e
                else:
                    pass
        else:
            pass
    
    def save(self):
        if self._state.name:
            self.saveas(self._state.name)
        else:
            print "Warning: No UB calculation defined."

    def saveas(self, name):
        self._state.name = name
        self._persister.save(self._state, name)

    def listub(self):
        return self._persister.list()
    
    def listub_metadata(self):
        return self._persister.list_metadata()

    def remove(self, name):
        self._persister.remove(name)
        if self._state.name == name:
            self._clear()

    def getState(self):
        return self._state.getState()

    def __str__(self):

        if self._state.name is None:
            return "<<< No UB calculation started >>>"
        lines = []
        lines.append(bold("UBCALC"))
        lines.append("")
        lines.append(
            "   name:".ljust(WIDTH) + self._state.name.rjust(9))
        
        if self.include_sigtau:
            lines.append("")
            lines.append(
                "   sigma:".ljust(WIDTH) + ("% 9.5f" % self._state.sigma).rjust(9))
            lines.append(
                "   tau:".ljust(WIDTH) + ("% 9.5f" % self._state.tau).rjust(9))

        if self.include_reference:
            lines.append("")
            ub_calculated = self._UB is not None
            lines.extend(self._state.reference.repr_lines(ub_calculated, WIDTH, self._ROT))
        
        lines.append("")
        lines.append(bold("CRYSTAL"))
        lines.append("")
        
        if self._state.crystal is None:
            lines.append("   <<< none specified >>>")
        else:
            lines.extend(self._state.crystal.str_lines())

        lines.append("")
        lines.append(bold("UB MATRIX"))
        lines.append("")
        
        if self._UB is None:
            lines.append("   <<< none calculated >>>")
        else:
            lines.extend(self.str_lines_u())
            lines.append("")
            lines.extend(self.str_lines_u_angle_and_axis())
            lines.append("")
            lines.extend(self.str_lines_ub())

        lines.append("")
        lines.append(bold("REFLECTIONS"))
        lines.append("")
        
        lines.extend(self._state.reflist.str_lines())
        
        lines.append("")
        lines.append(bold("CRYSTAL ORIENTATIONS"))
        lines.append("")
        
        lines.extend(self._state.orientlist.str_lines(R=self._ROT))
        
        return '\n'.join(lines)

    def str_lines_u(self):
        lines = []
        fmt = "% 9.5f % 9.5f % 9.5f"
        try:
            U = self._ROT.I * self.U * self._ROT
        except AttributeError:
            U = self.U
        lines.append("   U matrix:".ljust(WIDTH) +
                     fmt % (z(U[0, 0]), z(U[0, 1]), z(U[0, 2])))
        lines.append(' ' * WIDTH + fmt % (z(U[1, 0]), z(U[1, 1]), z(U[1, 2])))
        lines.append(' ' * WIDTH + fmt % (z(U[2, 0]), z(U[2, 1]), z(U[2, 2])))
        return lines

    def str_lines_u_angle_and_axis(self):
        lines = []
        fmt = "% 9.5f % 9.5f % 9.5f"
        y = matrix('0; 0; 1')
        try:
            rotation_axis = cross3(self._ROT * y, self._ROT * self.U * y)
        except TypeError:
            rotation_axis = cross3(y, self.U * y)
        if abs(norm(rotation_axis)) < SMALL:
            lines.append("   miscut angle:".ljust(WIDTH) + "  0")
        else:
            rotation_axis = rotation_axis * (1 / norm(rotation_axis))
            cos_rotation_angle = dot3(y, self.U * y)
            rotation_angle = acos(cos_rotation_angle)

            lines.append("   miscut:")
            lines.append("      angle:".ljust(WIDTH) + "% 9.5f" % (rotation_angle * TODEG))
            lines.append("       axis:".ljust(WIDTH) + fmt % tuple((rotation_axis.T).tolist()[0]))
 
        return lines

    def str_lines_ub(self):
        lines = []
        fmt = "% 9.5f % 9.5f % 9.5f"
        try:
            RI = self._ROT.I
            B = self._state.crystal.B
            UB = RI * self.UB * B.I * self._ROT * B
        except AttributeError:
            UB = self.UB
        lines.append("   UB matrix:".ljust(WIDTH) +
                     fmt % (z(UB[0, 0]), z(UB[0, 1]), z(UB[0, 2])))
        lines.append(' ' * WIDTH + fmt % (z(UB[1, 0]), z(UB[1, 1]), z(UB[1, 2])))
        lines.append(' ' * WIDTH + fmt % (z(UB[2, 0]), z(UB[2, 1]), z(UB[2, 2])))
        return lines

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
        if self._U is not None:  # (UB will also exist)
            print "Warning: the old UB calculation has been cleared."
            print "         Use 'calcub' to recalculate with old reflections or"
            print "         'orientub' to recalculate with old orientations."

### Surface normal stuff ###

    def _gettau(self):
        """
        Returns tau (in degrees): the (minus) ammount of phi axis rotation ,
        that together with some chi axis rotation (minus sigma) brings the
        optical surface normal parallel to the omega axis.
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
        optical surface normal parallel to the omega axis.
        """
        return self._state.sigma

    def _setsigma(self, sigma):
        self.state._sigma = sigma
        self.save()

    sigma = property(_getsigma, _setsigma)


### Reference vector ###

    def _get_n_hkl(self):
        return self._state.reference.n_hkl
    
    def _get_n_phi(self):
        return self._state.reference.n_phi
    
    n_hkl = property(_get_n_hkl)
    n_phi = property(_get_n_phi)
    
    def set_n_phi_configured(self, n_phi):
        try:
            self._state.reference.n_phi_configured = self._ROT.I * n_phi
        except AttributeError:
            self._state.reference.n_phi_configured = n_phi
        self.save()
        
    def set_n_hkl_configured(self, n_hkl):
        self._state.reference.n_hkl_configured = n_hkl
        self.save()
        
    def print_reference(self):
        print '\n'.join(self._state.reference.repr_lines(self.is_ub_calculated(), R=self._ROT.I))

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
            (self._U is not None)):
            self._autocalculateUbAndReport()
        self.save()

    def swap_reflections(self, num1, num2):
        self._state.reflist.swap_reflections(num1, num2)
        if ((num1 == 1 or num1 == 2 or num2 == 1 or num2 == 2) and
            (self._U is not None)):
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

### Orientations ###

    def add_orientation(self, h, k, l, x, y, z, tag, time):
        """add_reflection(h, k, l, x, y, z, tag=None) -- adds a crystal orientation
        """
        if self._state.orientlist is None:
            raise DiffcalcException("No UBCalculation loaded")
        try:
            xyz_rot = self._ROT * matrix([[x],[y],[z]])
            xr, yr, zr = xyz_rot.T.tolist()[0]
            self._state.orientlist.add_orientation(h, k, l, xr, yr, zr, tag, time)
        except TypeError:
            self._state.orientlist.add_orientation(h, k, l, x, y, z, tag, time)
        self.save()  # incase autocalculateUbAndReport fails

        # If second reflection has just been added then calculateUB
        if len(self._state.orientlist) == 2:
            self._autocalculateOrientationUbAndReport()
        self.save()

    def edit_orientation(self, num, h, k, l, x, y, z, tag, time):
        """
        edit_orientation(num, h, k, l, x, y, z, tag=None) -- edit a crystal reflection        """
        if self._state.orientlist is None:
            raise DiffcalcException("No UBCalculation loaded")
        try:
            xyz_rot = self._ROT * matrix([[x],[y],[z]])
            xr, yr, zr = xyz_rot.T.tolist()[0]
            self._state.orientlist.edit_orientation(num, h, k, l, xr, yr, zr, tag, time)
        except TypeError:
            self._state.orientlist.edit_orientation(num, h, k, l, x, y, z, tag, time)

        # If first or second orientation has been changed and there are
        # two orientations then recalculate  UB
        if (num == 1 or num == 2) and len(self._state.orientlist) == 2:
            self._autocalculateOrientationUbAndReport()
        self.save()

    def get_orientation(self, num):
        """--> ( [h, k, l], [x, y, z], tag, time )
        num starts at 1"""
        try:
            hkl, xyz, tg, tm = self._state.orientlist.getOrientation(num)
            xyz_rot = self._ROT.I * matrix([[xyz[0]],[xyz[1]],[xyz[2]]])
            xyz_lst = xyz_rot.T.tolist()[0]
            return hkl, xyz_lst, tg, tm
        except AttributeError:
            return self._state.orientlist.getOrientation(num)


    def get_number_orientations(self):
        return 0 if self._state.orientlist is None else len(self._state.reflist)

    def del_orientation(self, orientationNumber):
        self._state.orientlist.removeOrientation(orientationNumber)
        if ((orientationNumber == 2) and (self._U is not None)):
            self._autocalculateOrientationUbAndReport()
        self.save()

    def swap_orientations(self, num1, num2):
        self._state.orientlist.swap_orientations(num1, num2)
        if ((num1 == 2 or num2 == 2) and
            (self._U is not None)):
            self._autocalculateOrientationUbAndReport()
        self.save()

    def _autocalculateOrientationUbAndReport(self):
        if len(self._state.orientlist) < 2:
            pass
        elif self._state.crystal is None:
            print ("Not calculating UB matrix as no lattice parameters have "
                   "been specified.")
        elif not self._state.is_okay_to_autocalculate_ub:
            print ("Not calculating UB matrix as it has been manually set. "
                   "Use 'orientub' to explicitly recalculate it.")
        else:  # okay to autocalculate
            if self._UB is None:
                print "Calculating UB matrix."
            else:
                print "Recalculating UB matrix."
            self.calculate_UB_from_orientation()

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

        if self._ROT is not None:
            self._U = self._ROT * m * self._ROT.I
        else:
            self._U = m
        self._state.configure_calc_type(manual_U=self._U)
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

        if self._ROT is not None:
            self._UB = self._ROT * m
        else:
            self._UB = m
        self._state.configure_calc_type(manual_UB=self._UB)
        self.save()

    @property
    def U(self):
        if self._U is None:
            raise DiffcalcException(
                "No U matrix has been calculated during this ub calculation")
        return self._U

    @property
    def UB(self):
        return self._get_UB()
    
    def is_ub_calculated(self):
        return self._UB is not None

    def _get_UB(self):
        if not self.is_ub_calculated():
            raise DiffcalcException(
                "No UB matrix has been calculated during this ub calculation")
        else:
            return self._UB

    def _calc_UB(self, h1, h2, u1p, u2p):
        B = self._state.crystal.B
        h1c = B * h1
        h2c = B * h2

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
                "Two reflections are required to calculate a U matrix")
        h1 = matrix([h1]).T  # row->column
        h2 = matrix([h2]).T
        pos1.changeToRadians()
        pos2.changeToRadians()

        # Compute the two reflections' reciprical lattice vectors in the
        # cartesian crystal frame
        u1p = self._strategy.calculate_q_phi(pos1)
        u2p = self._strategy.calculate_q_phi(pos2)
        
        self._calc_UB(h1, h2, u1p, u2p)

    def calculate_UB_from_orientation(self):
        """
        Calculate orientation matrix. Uses first two crystal orientations.
        """

        # Major variables:
        # h1, h2: user input reciprical lattice vectors of the two reflections
        # h1c, h2c: user input vectors in cartesian crystal plane
        # pos1, pos2: measured diffractometer positions of the two reflections
        # u1a, u2a: measured reflection vectors in alpha frame
        # u1p, u2p: measured reflection vectors in phi frame


        # Get hkl and angle values for the first two crystal orientations
        if self._state.orientlist is None:
            raise DiffcalcException("Cannot calculate a U matrix until a "
                                    "UBCalculation has been started with "
                                    "'newub'")
        try:
            (h1, x1, _, _) = self._state.orientlist.getOrientation(1)
            (h2, x2, _, _) = self._state.orientlist.getOrientation(2)
        except IndexError:
            raise DiffcalcException(
                "Two crystal orientations are required to calculate a U matrix")
        h1 = matrix([h1]).T  # row->column
        h2 = matrix([h2]).T
        u1p = matrix([x1]).T
        u2p = matrix([x2]).T

        self._calc_UB(h1, h2, u1p, u2p)

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

    def set_miscut(self, xyz, angle, add_miscut=False):
        """Calculate U matrix using a miscut axis and an angle"""
        if xyz is None:
            rot_matrix = xyz_rotation([0, 1, 0], angle)
            if self.is_ub_calculated() and add_miscut:
                self._U = rot_matrix * self._U
            else:
                self._U = rot_matrix
        else:
            rot_matrix = xyz_rotation(xyz, angle)
            try:
                rot_matrix =  self._ROT * rot_matrix * self._ROT.I
            except TypeError:
                pass
            if self.is_ub_calculated() and add_miscut:
                self._U = rot_matrix * self._U
            else:
                self._U = rot_matrix
        self._state.configure_calc_type(manual_U=self._U)
        self._UB = self._U * self._state.crystal.B
        self.print_reference()
        self.save()

    def get_hkl_plane_distance(self, hkl):
        """Calculates and returns the distance between planes"""
        return self._state.crystal.get_hkl_plane_distance(hkl)

    def get_hkl_plane_angle(self, hkl1, hkl2):
        """Calculates and returns the angle between planes"""
        return self._state.crystal.get_hkl_plane_angle(hkl1, hkl2)

    def rescale_unit_cell(self, h, k, l, pos):
        """
        Calculate unit cell scaling parameter that matches
        given hkl position and diffractometer angles
        """
        q_vec = self._strategy.calculate_q_phi(pos)
        q_hkl = norm(q_vec) / self._hardware.get_wavelength()
        d_hkl = self._state.crystal.get_hkl_plane_distance([h, k, l])
        sc = 1/ (q_hkl * d_hkl)
        name, a1, a2, a3, alpha1, alpha2, alpha3 = self._state.crystal.getLattice()
        if abs(sc - 1.) < SMALL:
            return None, None
        ref_a1 = sc * a1 if abs(h) > SMALL else a1
        ref_a2 = sc * a2 if abs(k) > SMALL else a2
        ref_a3 = sc * a3 if abs(l) > SMALL else a3
        return sc, (name, ref_a1, ref_a2, ref_a3, alpha1, alpha2, alpha3)

    def calc_miscut(self, h, k, l, pos):
        """
        Calculate miscut angle and axis that matches
        given hkl position and diffractometer angles
        """
        q_vec = self._strategy.calculate_q_phi(pos)
        hkl_nphi = self._UB * matrix([[h], [k], [l]])
        try:
            axis = cross3(self._ROT.I * q_vec, self._ROT.I * hkl_nphi)
        except AttributeError:
            axis = cross3(q_vec, hkl_nphi)
        norm_axis = norm(axis)
        if norm_axis < SMALL:
            return None, None
        axis = axis / norm(axis)
        try:
            miscut = acos(bound(dot3(q_vec, hkl_nphi) / (norm(q_vec) * norm(hkl_nphi)))) * TODEG
        except AssertionError:
            return None, None
        return miscut, axis.T.tolist()[0]

    def calc_hkl_offset(self, h, k, l, pol, az):
        """
        Calculate hkl orientation values that are related to
        the input hkl values by rotation with a given polar
        and azimuthal angles
        """
        hkl_nphi = self._UB * matrix([[h], [k], [l]])
        y_axis = cross3(hkl_nphi, matrix('0; 1; 0'))
        if norm3(y_axis) < SMALL:
            y_axis = cross3(hkl_nphi, matrix('0; 0; 1'))
        rot_polar = xyz_rotation(y_axis.T.tolist()[0], pol)
        rot_azimuthal = xyz_rotation(hkl_nphi.T.tolist()[0], az)
        hklrot_nphi = rot_azimuthal * rot_polar * hkl_nphi
        hklrot = self._UB.I * hklrot_nphi
        hkl_list = hklrot.T.tolist()[0]
        return hkl_list

    def calc_offset_for_hkl(self, hkl_offset, hkl_ref):
        """
        Calculate polar and azimuthal angles and scaling factor
        relating offset and reference hkl values
        """
        d_ref = self._state.crystal.get_hkl_plane_distance(hkl_ref)
        hklref_nphi = self._UB * matrix([[hkl_ref[0]], [hkl_ref[1]], [hkl_ref[2]]])
        d_offset = self._state.crystal.get_hkl_plane_distance(hkl_offset)
        hkloff_nphi = self._UB * matrix([[hkl_offset[0]], [hkl_offset[1]], [hkl_offset[2]]])
        sc = d_ref / d_offset
        par_ref_off = cross3(hklref_nphi, hkloff_nphi)
        if norm3(par_ref_off) < SMALL:
            return 0, float('nan'), sc
        y_axis = cross3(hklref_nphi, matrix('0; 1; 0'))
        if norm3(y_axis) < SMALL:
            y_axis = cross3(hklref_nphi, matrix('0; 0; 1'))
        x_axis = cross3(y_axis, hklref_nphi)
        x_coord = cos(angle_between_vectors(hkloff_nphi, x_axis))
        y_coord = cos(angle_between_vectors(hkloff_nphi, y_axis))
        pol = angle_between_vectors(hklref_nphi, hkloff_nphi)
        if abs(y_coord) < SMALL and abs(x_coord) < SMALL:
            # Set azimuthal rotation matrix to identity
            az = 0
        else:
            az = atan2(y_coord, x_coord)
        return pol, az, sc
