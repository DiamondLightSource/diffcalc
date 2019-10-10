###
# Copyright 2008-2019 Diamond Light Source Ltd.
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

try:
    from gda.device.scannable.scannablegroup import ScannableGroup
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import ScannableGroup

from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup
from diffcalc.settings import NUNAME
from diffcalc.hkl.you.geometry import YouRemappedGeometry


class FourCircleI21(YouRemappedGeometry):
    """For a diffractometer with angles:
          delta, eta, chi, phi
    """
    def __init__(self, beamline_axes_transform=None, delta_offset=0):
        self._delta_offset = delta_offset
        YouRemappedGeometry.__init__(self, 'fourc', {'eta': 0, 'delta': 0}, beamline_axes_transform)

        # Order should match scannable order in _fourc group for mapping to work correctly
        self._scn_mapping_to_int = ((NUNAME, lambda x: x + self._delta_offset),
                                    ('mu',   lambda x: x),
                                    ('chi',  lambda x: x),
                                    ('phi',  lambda x: -x))
        self._scn_mapping_to_ext = ((NUNAME, lambda x: x - self._delta_offset),
                                    ('mu',   lambda x: x),
                                    ('chi',  lambda x: x),
                                    ('phi',  lambda x: -x))

class TPScannableGroup(ScannableGroup):

    def asynchronousMoveTo(self, position):
        # if input has any Nones, then replace these with the current positions
        if None in position:
            position = list(position)
            current = self.getPosition()
            for idx, val in enumerate(position):
                if val is None:
                    position[idx] = current[idx]

        for scn, pos in zip(self.getGroupMembers(), position):
            scn.asynchronousMoveTo(pos)
            scn.waitWhileBusy()

class DiffractometerTPScannableGroup(DiffractometerScannableGroup):

    def asynchronousMoveTo(self, position):
        # if input has any Nones, then replace these with the current positions
        if None in position:
            position = list(position)
            current = self.getPosition()
            for idx, val in enumerate(position):
                if val is None:
                    position[idx] = current[idx]

        for scn, pos in zip(self.__motors, position):
            scn.asynchronousMoveTo(pos)
            scn.waitWhileBusy()

        