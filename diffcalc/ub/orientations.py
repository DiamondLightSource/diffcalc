###
# Copyright 2008-2017 Diamond Light Source Ltd.
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

from copy import deepcopy
import datetime  # @UnusedImport for the eval below
from diffcalc.hkl.you.geometry import YouPosition

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.util import DiffcalcException, bold


class _Orientation:
    """A orientation"""
    def __init__(self, h, k, l, x, y, z, position, tag, time):

        self.h = float(h)
        self.k = float(k)
        self.l = float(l)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.pos = position
        self.tag = tag
        self.time = time  # Saved as e.g. repr(datetime.now())

    def __str__(self):
        return ("h=%-4.2f k=%-4.2f l=%-4.2f  x=%-4.2f "
                "y=%-4.2f z=%-4.2  mu=%-8.4f "
                "delta=%-8.4f nu=%-8.4f eta=%-8.4f chi=%-8.4f "
                "phi=%-8.4f  %-s %s" % (self.h, self.k, self.l,
                self.x, self.y, self.z,
                self.pos.mu, self.pos.delta, self.pos.nu, self.pos.eta,
                self.pos.chi, self.pos.phi, self.tag, self.time))


class OrientationList:

    def __init__(self, geometry, externalAngleNames, orientations=None):
        self._geometry = geometry
        self._externalAngleNames = externalAngleNames
        self._orientlist = orientations if orientations else []

    def get_tag_index(self, idx):
        _tag_list = [ornt.tag for ornt in self._orientlist]
        try:
            num  = _tag_list.index(idx)
        except ValueError:
            if isinstance(idx, int):
                if idx < 1 or idx > len(self._orientlist):
                    raise IndexError("Orientation index is out of range")
                else:
                    num = idx - 1
            else:
                raise IndexError("Orientation index not found")
        return num

    def add_orientation(self, h, k, l, x, y, z, position, tag, time):
        """adds a crystal orientation
        """
        if type(position) in (list, tuple):
            try:
                position = self._geometry.create_position(*position)
            except AttributeError:
                position = YouPosition(*position)
        self._orientlist += [_Orientation(h, k, l, x, y, z, position, tag,
                                     time.__repr__())]

    def edit_orientation(self, idx, h, k, l, x, y, z, position, tag, time):
        """num starts at 1"""
        try:
            num = self.get_tag_index(idx)
        except IndexError:
            raise DiffcalcException("There is no orientation " + repr(idx)
                                     + " to edit.")
        if type(position) in (list, tuple):
            position = YouPosition(*position)
        self._orientlist[num] = _Orientation(h, k, l, x, y, z, position, tag, time.__repr__())

    def getOrientation(self, idx):
        """
        getOrientation(idx) --> ( [h, k, l], [x, y, z], pos, tag, time ) --
        idx refers to an orientation index (starts at 1) or a tag
        """
        num = self.get_tag_index(idx)
        r = deepcopy(self._orientlist[num])  # for convenience
        return [r.h, r.k, r.l], [r.x, r.y, r.z], deepcopy(r.pos), r.tag, eval(r.time)

    def get_orientation_in_external_angles(self, idx):
        """
        get_orientation_in_external_angles(idx) --> ( [h, k, l], [x, y, z], pos, tag, time ) --
        idx refers to an orientation index (starts at 1) or a tag
        """
        num = self.get_tag_index(idx)
        r = deepcopy(self._orientlist[num])  # for convenience
        externalAngles = self._geometry.internal_position_to_physical_angles(r.pos)
        result = [r.h, r.k, r.l], [r.x, r.y, r.z], externalAngles, r.tag, eval(r.time)
        return result

    def removeOrientation(self, idx):
        num = self.get_tag_index(idx)
        del self._orientlist[num]

    def swap_orientations(self, idx1, idx2):
        num1 = self.get_tag_index(idx1)
        num2 = self.get_tag_index(idx2)
        orig1 = self._orientlist[num1]
        self._orientlist[num1] = self._orientlist[num2]
        self._orientlist[num2] = orig1

    def __len__(self):
        return len(self._orientlist)

    def __str__(self):
        return '\n'.join(self.str_lines())

    def str_lines(self, conv=None):
        axes = tuple(s.upper() for s in self._externalAngleNames)
        if not self._orientlist:
            return ["   <<< none specified >>>"]

        lines = []

        str_format = ("     %5s %5s %5s   %5s %5s %5s  " + "%8s " * len(axes) + " TAG")
        values = ('H', 'K', 'L', 'X', 'Y', 'Z') + axes
        lines.append(bold(str_format % values))

        for n in range(1, len(self._orientlist) + 1):
            orient_tuple = self.get_orientation_in_external_angles(n)
            [h, k, l], [x, y, z], externalAngles, tag, _ = orient_tuple
            try:
                xyz_rot = conv.transform(matrix([[x],[y],[z]]), True)
                xr, yr, zr = xyz_rot.T.tolist()[0]
            except AttributeError:
                xr, yr, zr = x ,y ,z
            if tag is None:
                tag = ""
            str_format = ("  %2d % 4.2f % 4.2f % 4.2f  " +
                      "% 4.2f % 4.2f % 4.2f  " + "% 8.4f " * len(axes) + " %s")
            values = (n, h, k, l, xr, yr, zr) + externalAngles + (tag,)
            lines.append(str_format % values)
        return lines
