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

from diffcalc.util import DiffcalcException, differ

TORAD = pi / 180
TODEG = 180 / pi


class HklCalculatorBase(object):

    def __init__(self, ubcalc, geometry, hardware,
                 raiseExceptionsIfAnglesDoNotMapBackToHkl=False):

        self._ubcalc = ubcalc  # to get the UBMatrix, tau and sigma
        self._geometry = geometry   # to access information about the
                                    # diffractometer geometry and mode_selector
        self._hardware = hardware  # Used for tracking parameters only
        self.raiseExceptionsIfAnglesDoNotMapBackToHkl = \
            raiseExceptionsIfAnglesDoNotMapBackToHkl

    def anglesToHkl(self, pos, wavelength):
        """
        Return hkl tuple and dictionary of all virtual angles in degrees from
        Position in degrees and wavelength in Angstroms.
        """

        h, k, l = self._anglesToHkl(pos.inRadians(), wavelength)
        paramDict = self.anglesToVirtualAngles(pos, wavelength)
        return ((h, k, l), paramDict)

    def anglesToVirtualAngles(self, pos, wavelength):
        """
        Return dictionary of all virtual angles in degrees from Position object
        in degrees and wavelength in Angstroms.
        """
        anglesDict = self._anglesToVirtualAngles(pos.inRadians(), wavelength)
        for name in anglesDict:
            anglesDict[name] = anglesDict[name] * TODEG
        return anglesDict

    def hklToAngles(self, h, k, l, wavelength):
        """
        Return verified Position and all virtual angles in degrees from
        h, k & l and wavelength in Angstroms.

        The calculated Position is verified by checking that it maps back using
        anglesToHkl() to the requested hkl value.

        Those virtual angles fixed or generated while calculating the position
        are verified by by checking that they map back using
        anglesToVirtualAngles to the virtual angles for the given position.

        Throws a DiffcalcException if either check fails and
        raiseExceptionsIfAnglesDoNotMapBackToHkl is True, otherwise displays a
        warning.
        """

        # Update tracked parameters. During this calculation parameter values
        # will be read directly from self._parameters instead of via
        # self.getParameter which would trigger another potentially time-costly
        # position update.
        self.parameter_manager.update_tracked()

        pos, virtualAngles = self._hklToAngles(h, k, l, wavelength)  # in rad

        # to degrees:
        pos.changeToDegrees()
        
        for key, val in virtualAngles.items():
            if val is not None:
                virtualAngles[key] = val * TODEG

        self._verify_pos_map_to_hkl(h, k, l, wavelength, pos)

        virtualAnglesReadback = self._verify_virtual_angles(h, k, l, wavelength, pos, virtualAngles)

        return pos, virtualAnglesReadback

    def _verify_pos_map_to_hkl(self, h, k, l, wavelength, pos):
        hkl, _ = self.anglesToHkl(pos, wavelength)
        e = 0.001
        if ((abs(hkl[0] - h) > e) or (abs(hkl[1] - k) > e) or 
            (abs(hkl[2] - l) > e)):
            s = "ERROR: The angles calculated for hkl=(%f,%f,%f) were %s.\n" % (h, k, l, str(pos))
            s += "Converting these angles back to hkl resulted in hkl="\
            "(%f,%f,%f)" % (hkl[0], hkl[1], hkl[2])
            if self.raiseExceptionsIfAnglesDoNotMapBackToHkl:
                raise DiffcalcException(s)
            else:
                print s

    def _verify_virtual_angles(self, h, k, l, wavelength, pos, virtualAngles):
        # Check that the virtual angles calculated/fixed during the hklToAngles
    # those read back from pos using anglesToVirtualAngles
        virtualAnglesReadback = self.anglesToVirtualAngles(pos, wavelength)
        for key, val in virtualAngles.items():
            if val != None: # Some values calculated in some mode_selector
                r = virtualAnglesReadback[key]
                if ((differ(val, r, .00001) and differ(val, r + 360, .00001) and differ(val, r - 360, .00001))):
                    s = "ERROR: The angles calculated for hkl=(%f,%f,%f) with"\
                    " mode=%s were %s.\n" % (h, k, l, self.repr_mode(), str(pos))
                    s += "During verification the virtual angle %s resulting "\
                    "from (or set for) this calculation of %f" % (key, val)
                    s += "did not match that calculated by "\
                    "anglesToVirtualAngles of %f" % virtualAnglesReadback[key]
                    if self.raiseExceptionsIfAnglesDoNotMapBackToHkl:
                        raise DiffcalcException(s)
                    else:
                        print s
        
        return virtualAnglesReadback

    def repr_mode(self):
        pass

### Collect all math access to context here

    def _getUBMatrix(self):
        return self._ubcalc.UB

    def _getMode(self):
        return self.mode_selector.getMode()

    def _getSigma(self):
        return self._ubcalc.sigma

    def _getTau(self):
        return self._ubcalc.tau

    def _getParameter(self, name):
        # Does not use context.getParameter as this will trigger a costly
        # parameter collection
        pm = self.parameter_manager
        return pm.getParameterWithoutUpdatingTrackedParemeters(name)

    def _getGammaParameterName(self):
        return self._gammaParameterName
