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

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.util import DiffcalcException, bold


class _Orientation:
    """A orientation"""
    def __init__(self, h, k, l, x, y, z, tag, time):

        self.h = float(h)
        self.k = float(k)
        self.l = float(l)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.tag = tag
        self.time = time  # Saved as e.g. repr(datetime.now())

    def __str__(self):
        return ("h=%-4.2f k=%-4.2f l=%-4.2f  x=%-4.2f "
                "y=%-4.2f z=%-4.2 "
                "  %-s %s" % (self.h, self.k, self.l,
                self.x, self.y, self.z,
                self.tag, self.time))


class OrientationList:

    def __init__(self, orientations=None):
        self._orientlist = orientations if orientations else []
            

    def add_orientation(self, h, k, l, x, y, z, tag, time):
        """adds a crystal orientation
        """
        self._orientlist += [_Orientation(h, k, l, x, y, z, tag,
                                     time.__repr__())]

    def edit_orientation(self, num, h, k, l, x, y, z, tag, time):
        """num starts at 1"""
        try:
            self._orientlist[num - 1] = _Orientation(h, k, l, x, y, z, tag,
                                                time.__repr__())
        except IndexError:
            raise DiffcalcException("There is no orientation " + repr(num)
                                     + " to edit.")

    def getOrientation(self, num):
        """
        getOrientation(num) --> ( [h, k, l], [x, y, z], tag, time ) --
        num starts at 1
        """
        r = deepcopy(self._orientlist[num - 1])  # for convenience
        return [r.h, r.k, r.l], [r.x, r.y, r.z], r.tag, eval(r.time)

    def removeOrientation(self, num):
        del self._orientlist[num - 1]

    def swap_orientations(self, num1, num2):
        orig1 = self._orientlist[num1 - 1]
        self._orientlist[num1 - 1] = self._orientlist[num2 - 1]
        self._orientlist[num2 - 1] = orig1

    def __len__(self):
        return len(self._orientlist)

    def __str__(self):
        return '\n'.join(self.str_lines())

    def str_lines(self, R=None):
        if not self._orientlist:
            return ["   <<< none specified >>>"]

        lines = []

        str_format = ("     %5s %5s %5s   %5s %5s %5s  TAG")
        values = ('H', 'K', 'L', 'X', 'Y', 'Z')
        lines.append(bold(str_format % values))

        for n in range(len(self._orientlist)):
            orient_tuple = self.getOrientation(n + 1)
            [h, k, l], [x, y, z], tag, _ = orient_tuple
            try:
                xyz_rot = R.I * matrix([[x],[y],[z]])
                xr, yr, zr = xyz_rot.T.tolist()[0]
            except AttributeError:
                xr, yr, zr = x ,y ,z
            if tag is None:
                tag = ""
            str_format = ("  %2d % 4.2f % 4.2f % 4.2f  " +
                      "% 4.2f % 4.2f % 4.2f  %s")
            values = (n + 1, h, k, l, xr, yr, zr, tag)
            lines.append(str_format % values)
        return lines
