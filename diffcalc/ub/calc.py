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
    bound, angle_between_vectors, norm3, CoordinateConverter, allnum
from math import acos, cos, sin, pi, atan2
from diffcalc.ub.reference import YouReference
from diffcalc.ub.orientations import OrientationList
from diffcalc import settings
from itertools import product

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

    def __init__(self, persister, strategy, include_sigtau=True, include_reference=True):

        # The diffractometer geometry is required to map the internal angles
        # into those used by this diffractometer (for display only)

        self._persister = persister
        self._strategy = strategy
        self.include_sigtau = include_sigtau
        self.include_reference = include_reference
        try:
            self._tobj = CoordinateConverter(transform=settings.geometry.beamline_axes_transform)
        except AttributeError:
            self._tobj = CoordinateConverter(transform=None)
        self._clear()
        
    def _get_diffractometer_axes_names(self):
        return settings.hardware.get_axes_names()

    def _clear(self, name=None):
        # NOTE the Diffraction calculator is expecting this object to exist in
        # the long run. We can't remove this entire object, and recreate it.
        # It also contains a required link to the angle calculator.
        reflist = ReflectionList(settings.geometry, self._get_diffractometer_axes_names(),
                                 multiplier=settings.hardware.energyScannableMultiplierToGetKeV)
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
                                                                     settings.geometry,
                                                                     self._get_diffractometer_axes_names(),
                                                                     settings.hardware.energyScannableMultiplierToGetKeV)
            self._state.reference.get_UB = self._get_UB
        elif isinstance(self._persister, UBCalculationPersister):
            self._state = state
        else:
            raise DiffcalcException('Unexpected persister type: ' + str(self._persister))
        if self._state.manual_U is not None:
            self._U = self._state.manual_U
            self._UB = self._U * self._state.crystal.B
            self.save()
        elif self._state.manual_UB is not None:
            self._UB = self._state.manual_UB
            self.save()
        elif self._state.is_okay_to_autocalculate_ub:
            try:
                self.calculate_UB(self._state.or0, self._state.or1)
            except Exception, e:
                print e
        else:
            print "Warning: No UB calculation loaded."

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
            lines.extend(self._state.reference.repr_lines(ub_calculated, WIDTH, self._tobj))
        
        lines.append("")
        lines.append(bold("CRYSTAL"))
        lines.append("")
        
        if self._state.crystal is None:
            lines.append("   <<< none specified >>>")
        else:
            lines.extend(self._state.crystal.str_lines(self._tobj))

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
        
        lines.extend(self._state.orientlist.str_lines(self._tobj))
        
        return '\n'.join(lines)

    def str_lines_u(self):
        lines = []
        fmt = "% 9.5f % 9.5f % 9.5f"
        U = self._tobj.transform(self.U, True)
        lines.append("   U matrix:".ljust(WIDTH) +
                     fmt % (z(U[0, 0]), z(U[0, 1]), z(U[0, 2])))
        lines.append(' ' * WIDTH + fmt % (z(U[1, 0]), z(U[1, 1]), z(U[1, 2])))
        lines.append(' ' * WIDTH + fmt % (z(U[2, 0]), z(U[2, 1]), z(U[2, 2])))
        return lines

    def str_lines_u_angle_and_axis(self):
        lines = []
        fmt = "% 9.5f % 9.5f % 9.5f"
        y = matrix('0; 0; 1')
        rotation_axis = self._tobj.transform(cross3(y, self.U * y), True)
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
        if self._tobj.R is not None:
            UB = self._tobj.R.I * self.UB
        else:
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
        self._set_lattice_without_saving(name, *shortform)
        self.save()

    def _set_lattice_without_saving(self, name, *shortform):
        """
        Converts a list shortform crystal parameter specification to a six-long
        tuple. See setlat() for a description of the shortforms supported.
        """
        if not shortform:
            raise TypeError("Please specify unit cell parameters.")
        elif allnum(shortform):
            sf = shortform
            if len(sf) == 1:
                system = "Cubic"
            elif len(sf) == 2:
                system = "Tetragonal"
            elif len(sf) == 3:
                system = "Orthorhombic"
            elif len(sf) == 4:
                if abs(sf[0] - sf[1]) < SMALL and sf[3] == 120:
                    system = "Hexagonal"
                else:
                    system = "Monoclinic"
            elif len(sf) == 6:
                system = "Triclinic"
            else:
                raise TypeError("Invalid number of input parameters to set unit lattice.")
            fullform = (system,) + shortform
        else:
            if not isinstance(shortform[0], str):
                raise TypeError("Invalid unit cell parameters specified.")
            fullform = shortform
        self._set_lattice(name, *fullform)

    def _set_lattice(self, name, *args):
        """set lattice parameters in degrees"""
        if self._state.name is None:
            raise DiffcalcException(
                "Cannot set lattice until a UBCalcaluation has been started "
                "with newubcalc")
        self._state.crystal = CrystalUnderTest(name, *args)
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
        self._state.reference.n_phi_configured = self._tobj.transform(n_phi)
        self.save()
        
    def set_n_hkl_configured(self, n_hkl):
        self._state.reference.n_hkl_configured = n_hkl
        self.save()
        
    def print_reference(self):
        print '\n'.join(self._state.reference.repr_lines(self.is_ub_calculated(), WIDTH=9, conv=self._tobj))

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
        if self.get_reference_count() == 2:
            self._autocalculateUbAndReport()
        self.save()

    def edit_reflection(self, idx, h, k, l, position, energy, tag, time):
        """
        edit_reflection(idx, h, k, l, position, tag=None) -- changes a reflection

        position is in degrees and in the systems internal representation.
        """
        if self._state.reflist is None:
            raise DiffcalcException("No UBCalculation loaded")
        num = self.get_tag_refl_num(idx)
        self._state.reflist.edit_reflection(num, h, k, l, position, energy, tag, time)

        # If first or second reflection has been changed and there are at least
        # two reflections then recalculate  UB
        or12 = self.get_ub_references()
        if idx in or12 or num in or12:
            self._autocalculateUbAndReport()
        self.save()

    def get_reflection(self, idx):
        """--> ( [h, k, l], position, energy, tag, time
        position in degrees"""
        return self._state.reflist.getReflection(idx)

    def get_reflection_in_external_angles(self, idx):
        """--> ( [h, k, l], position, energy, tag, time
        position in degrees"""
        return self._state.reflist.get_reflection_in_external_angles(idx)
    
    def get_number_reflections(self):
        try:
            return len(self._state.reflist)
        except TypeError:
            return 0

    def get_tag_refl_num(self, tag):
        if tag is None:
            raise IndexError("Reflection tag is None")
        return self._state.reflist.get_tag_index(tag) + 1

    def del_reflection(self, idx):
        num = self.get_tag_refl_num(idx)
        self._state.reflist.removeReflection(num)
        or12 = self.get_ub_references()
        if ((idx in or12 or num in or12) and
            (self._U is not None)):
            self._autocalculateUbAndReport()
        self.save()

    def swap_reflections(self, idx1, idx2):
        num1 = self.get_tag_refl_num(idx1)
        num2 = self.get_tag_refl_num(idx2)
        self._state.reflist.swap_reflections(num1, num2)
        or12 = self.get_ub_references()
        if ((idx1 in or12 or idx2 in or12 or 
             num1 in or12 or num2 in or12) and
            (self._U is not None)):
            self._autocalculateUbAndReport()
        self.save()

    def _autocalculateUbAndReport(self):
        if self.get_reference_count() < 2:
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
            or12 = self.get_ub_references()
            self.calculate_UB(*or12)

### Orientations ###

    def add_orientation(self, h, k, l, x, y, z, tag, time):
        """add_reflection(h, k, l, x, y, z, tag=None) -- adds a crystal orientation
        """
        if self._state.orientlist is None:
            raise DiffcalcException("No UBCalculation loaded")
        xyz_tr = self._tobj.transform(matrix([[x],[y],[z]]))
        xr, yr, zr = xyz_tr.T.tolist()[0]
        self._state.orientlist.add_orientation(h, k, l, xr, yr, zr, tag, time)
        self.save()  # in case autocalculateUbAndReport fails

        # If second reflection has just been added then calculateUB
        if self.get_reference_count() == 2:
            self._autocalculateUbAndReport()
        self.save()

    def edit_orientation(self, idx, h, k, l, x, y, z, tag, time):
        """
        edit_orientation(idx, h, k, l, x, y, z, tag=None) -- edit a crystal reflection        """
        if self._state.orientlist is None:
            raise DiffcalcException("No UBCalculation loaded")
        num = self.get_tag_orient_num(idx)
        xyz_tr = self._tobj.transform(matrix([[x],[y],[z]]))
        xr, yr, zr = xyz_tr.T.tolist()[0]
        self._state.orientlist.edit_orientation(num, h, k, l, xr, yr, zr, tag, time)

        # If first or second orientation has been changed and there are
        # two orientations then recalculate  UB
        or12 = self.get_ub_references()
        if idx in or12 or num in or12:
            self._autocalculateUbAndReport()
        self.save()

    def get_orientation(self, idx, conv=False):
        """--> ( [h, k, l], [x, y, z], tag, time )"""
        hkl, xyz, tg, tm = self._state.orientlist.getOrientation(idx)
        if conv:
            xyz_rot = self._tobj.transform(matrix([[xyz[0]],[xyz[1]],[xyz[2]]]), True)
            xyz = xyz_rot.T.tolist()[0]
        return hkl, xyz, tg, tm

    def get_number_orientations(self):
        try:
            return len(self._state.orientlist)
        except TypeError:
            return 0

    def get_tag_orient_num(self, tag):
        if tag is None:
            raise IndexError("Orientations tag is None")
        return self._state.orientlist.get_tag_index(tag) + 1

    def del_orientation(self, idx):
        orientationNumber = self.get_tag_orient_num(idx)
        self._state.orientlist.removeOrientation(orientationNumber)
        if ((orientationNumber == 2) and (self._U is not None)):
            self._autocalculateUbAndReport()
        self.save()

    def swap_orientations(self, idx1, idx2):
        num1 = self.get_tag_orient_num(idx1)
        num2 = self.get_tag_orient_num(idx2)
        self._state.orientlist.swap_orientations(num1, num2)
        if ((num1 == 1 or num1 == 2 or num2 == 1 or num2 == 2) and
            (self._U is not None)):
            self._autocalculateUbAndReport()
        self.save()

    def get_ub_references(self):
        return (self._state.or0, self._state.or1)

    def get_reference_count(self):
        n_ref = self.get_number_reflections()
        n_orient = self.get_number_orientations()
        return n_ref + n_orient
#    @property
#    def reflist(self):
#        return self._state.reflist
### Calculations ###

    def set_U_manually(self, m, conv=True):
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
        
        if conv:
            self._U = self._tobj.transform(m)
        else:
            self._U = m
        self._state.configure_calc_type(manual_U=self._U)
        if self._state.crystal is None:
            raise DiffcalcException(
                "A crystal must be specified before manually setting U")
        self._UB = self._U * self._state.crystal.B
        self.save()

    def set_UB_manually(self, m):
        """Manually sets UB. matrix must be 3*3 Jama or python matrix.
        Turns off aution UB calcualtion."""

        # Check matrix is a 3*3 Jama matrix
        if m.__class__ != matrix:
            m = matrix(m)  # assume its a python matrix
        if m.shape[0] != 3 or m.shape[1] != 3:
            raise  ValueError("Expects 3*3 matrix")

        if self._tobj.R is not None:
            self._UB = self._tobj.R * m
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

        def normalise(m):
            d = norm(m)
            if d < SMALL:
                raise DiffcalcException("Invalid UB reference data. Please check that the specified "
                                        "reference reflections/orientations are not parallel.")
            return m / d

        t1c = normalise(t1c)
        t2c = normalise(t2c)
        t3c = normalise(t3c)

        t1p = normalise(t1p)
        t2p = normalise(t2p)
        t3p = normalise(t3p)

        Tc = hstack([t1c, t2c, t3c])
        Tp = hstack([t1p, t2p, t3p])
        self._U = Tp * Tc.I
        self._UB = self._U * B

    def calculate_UB(self, idx1=None, idx2=None):
        """
        Calculate orientation matrix.
        Default: use first two orientation reflections
        as in Busang and Levy, but for the diffractometer in Lohmeier and
        Vlieg.
        """

        # Major variables:
        # h1, h2: user input reciprocal lattice vectors of the two reflections
        # h1c, h2c: user input vectors in cartesian crystal plane
        # pos1, pos2: measured diffractometer positions of the two reflections
        # u1a, u2a: measured reflection vectors in alpha frame
        # u1p, u2p: measured reflection vectors in phi frame

        # Get hkl and angle values for the first two reflections
        if self._state.reflist is None and self._state.orientlist is None:
            raise DiffcalcException("Cannot calculate a U matrix until a "
                                    "UBCalculation has been started with "
                                    "'newub'")
        if idx1 is not None and idx2 is None:
            self.calculate_UB_from_primary_only(idx1)
            return
        elif idx1 is None and idx2 is None:
            ref_data = []
            for func, idx in product((self.get_reflection, self.get_orientation), (1, 2)):
                try:
                    ref_data.append(func(idx)[:2])
                except Exception:
                    pass
            try:
                (h1, pos1), (h2, pos2) = ref_data[:2]
            except ValueError:
                raise DiffcalcException("Cannot find calculate a U matrix. Please add "
                                        "reference reflection and/or orientation data.")
        else:
            try:
                h1, pos1 = self.get_reflection(idx1)[:2]
            except Exception:
                try:
                    h1, pos1 = self.get_orientation(idx1)[:2]
                except Exception:
                    raise DiffcalcException(
                        "Cannot find first reflection or orientation with index %s" % str(idx1))
            try:
                h2, pos2 = self.get_reflection(idx2)[:2]
            except Exception:
                try:
                    h2, pos2 = self.get_orientation(idx2)[:2]
                except Exception:
                    raise DiffcalcException(
                        "Cannot find second reflection or orientation with index %s" % str(idx2))
        h1 = matrix([h1]).T  # row->column
        h2 = matrix([h2]).T

        # Compute the two reflections' reciprocal lattice vectors in the
        # cartesian crystal frame
        try:
            pos1.changeToRadians()
            u1p = self._strategy.calculate_q_phi(pos1)
        except AttributeError:
            u1p = matrix([pos1]).T
        try:
            pos2.changeToRadians()
            u2p = self._strategy.calculate_q_phi(pos2)
        except AttributeError:
            u2p = matrix([pos2]).T

        self._calc_UB(h1, h2, u1p, u2p)

        self._state.configure_calc_type(or0=idx1, or1=idx2)
        self.save()

    def calculate_UB_from_primary_only(self, idx=1):
        """
        Calculate orientation matrix with the shortest absolute angle change.
        Default: use first reflection.
        """

        # Algorithm from http://www.j3d.org/matrix_faq/matrfaq_latest.html

        # Get hkl and angle values for the first two reflections
        if self._state.reflist is None:
            raise DiffcalcException(
                "Cannot calculate a u matrix until a UBCalcaluation has been "
                "started with newub")
        try:
            (h, pos, _, _, _) = self.get_reflection(idx)
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

        self._U = matrix(m)
        self._UB = self._U * B

        self._state.configure_calc_type(manual_U=self._U, or0=idx)
        self.save()

    def fit_ub_matrix(self, *args):
        if args is None:
            raise DiffcalcException("Please specify list of reference reflection indices.")
        if len(args) < 3:
            raise DiffcalcException("Need at least 3 reference reflections to fit UB matrix.")

        x = []
        y = []
        for idx in args:
            try:
                hkl_vals, pos, en, _, _ = self.get_reflection(idx)
            except IndexError:
                raise DiffcalcException("Cannot read reflection data for index %s" % str(idx))
            pos.changeToRadians()
            x.append(hkl_vals)
            wl = 12.3984 / en
            y_tmp = self._strategy.calculate_q_phi(pos) * 2.* pi / wl
            y.append(y_tmp.T.tolist()[0])

        xm = matrix(x)
        ym = matrix(y)
        b = (xm.T * xm).I * xm.T * ym

        b1, b2, b3 = matrix(b.tolist()[0]), matrix(b.tolist()[1]), matrix(b.tolist()[2])
        e1 = b1 / norm(b1)
        e2 = b2 - e1 * dot3(b2.T, e1.T)
        e2 = e2 / norm(e2)
        e3 = b3 - e1 * dot3(b3.T, e1.T) - e2 * dot3(b3.T, e2.T)
        e3 = e3 / norm(e3)

        new_umatrix = matrix(e1.tolist() +
                             e2.tolist() +
                             e3.tolist()).T

        V = dot3(cross3(b1.T, b2.T), b3.T)
        a1 = cross3(b2.T, b3.T) * 2 * pi / V
        a2 = cross3(b3.T, b1.T) * 2 * pi / V
        a3 = cross3(b1.T, b2.T) * 2 * pi / V
        ax, bx, cx = norm(a1), norm(a2), norm(a3)
        alpha = acos(dot3(a2, a3)/(bx * cx)) *TODEG
        beta = acos(dot3(a1, a3)/(ax * cx)) *TODEG
        gamma = acos(dot3(a1, a2)/(ax * bx)) *TODEG

        lattice_name = self._state.crystal.getLattice()[0]
        return new_umatrix, (lattice_name, ax, bx, cx, alpha, beta, gamma)

    def set_miscut(self, xyz, angle, add_miscut=False):
        """Calculate U matrix using a miscut axis and an angle"""
        if xyz is None:
            rot_matrix = xyz_rotation([0, 1, 0], angle)
        else:
            rot_matrix = self._tobj.transform(xyz_rotation(xyz, angle))
        if self.is_ub_calculated() and add_miscut:
            new_U = rot_matrix * self._U
        else:
            new_U = rot_matrix
        self.set_U_manually(new_U, False)
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
        q_hkl = norm(q_vec) / settings.hardware.get_wavelength()
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
        axis = self._tobj.transform(cross3(q_vec, hkl_nphi), True)
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
