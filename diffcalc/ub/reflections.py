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

from copy import deepcopy
import datetime  # @UnusedImport for the eval below
from diffcalc.util import DiffcalcException, bold
from diffcalc.hkl.you.geometry import YouPosition


class _Reflection:
    """A reflection"""
    def __init__(self, h, k, l, position, energy, tag, time):

        self.h = float(h)
        self.k = float(k)
        self.l = float(l)
        self.pos = position
        self.tag = tag
        self.energy = float(energy)      # energy=12.39842/lambda
        self.wavelength = 12.3984 / self.energy
        self.time = time  # Saved as e.g. repr(datetime.now())

    def __str__(self):
        return ("energy=%-6.3f h=%-4.2f k=%-4.2f l=%-4.2f  mu=%-8.4f "
                "delta=%-8.4f nu=%-8.4f eta=%-8.4f chi=%-8.4f "
                "phi=%-8.4f  %-s %s" % (self.energy, self.h, self.k, self.l,
                self.pos.mu, self.pos.delta, self.pos.nu, self.pos.eta,
                self.pos.chi, self.pos.phi, self.tag, self.time))


class ReflectionList:

    def __init__(self, geometry, externalAngleNames, reflections=None, multiplier=1):
        self._geometry = geometry
        self._externalAngleNames = externalAngleNames
        self._reflist = reflections if reflections else []
        self._multiplier = multiplier

    def get_tag_index(self, idx):
        _tag_list = [ref.tag for ref in self._reflist]
        try:
            num  = _tag_list.index(idx)
        except ValueError:
            if isinstance(idx, int):
                if idx < 1 or idx > len(self._reflist):
                    raise IndexError("Reflection index is out of range")
                else:
                    num = idx - 1
            else:
                raise IndexError("Reflection index not found")
        return num

    def add_reflection(self, h, k, l, position, energy, tag, time):
        """adds a reflection, position in degrees
        """
        if type(position) in (list, tuple):
            try:
                position = self._geometry.create_position(*position)
            except AttributeError:
                position = YouPosition(*position)
        self._reflist += [_Reflection(h, k, l, position, energy, tag, time.__repr__())]

    def edit_reflection(self, idx, h, k, l, position, energy, tag, time):
        """num starts at 1"""
        try:
            num = self.get_tag_index(idx)
        except IndexError:
            raise DiffcalcException("There is no reflection " + repr(idx)
                                     + " to edit.")
        if type(position) in (list, tuple):
            position = YouPosition(*position)
        self._reflist[num] = _Reflection(h, k, l, position, energy, tag, time.__repr__())

    def getReflection(self, idx):
        """
        getReflection(idx) --> ( [h, k, l], position, energy, tag, time ) --
        position in degrees
        """
        num = self.get_tag_index(idx)
        r = deepcopy(self._reflist[num])  # for convenience
        return [r.h, r.k, r.l], deepcopy(r.pos), r.energy, r.tag, eval(r.time)

    def get_reflection_in_external_angles(self, idx):
        """getReflection(num) --> ( [h, k, l], (angle1...angleN), energy, tag )
        -- position in degrees"""
        num = self.get_tag_index(idx)
        r = deepcopy(self._reflist[num])  # for convenience
        externalAngles = self._geometry.internal_position_to_physical_angles(r.pos)
        result = [r.h, r.k, r.l], externalAngles, r.energy, r.tag, eval(r.time)
        return result

    def removeReflection(self, idx):
        num = self.get_tag_index(idx)
        del self._reflist[num]

    def swap_reflections(self, idx1, idx2):
        num1 = self.get_tag_index(idx1)
        num2 = self.get_tag_index(idx2)
        orig1 = self._reflist[num1]
        self._reflist[num1] = self._reflist[num2]
        self._reflist[num2] = orig1

    def __len__(self):
        return len(self._reflist)

    def __str__(self):
        return '\n'.join(self.str_lines())

    def str_lines(self):
        axes = tuple(s.upper() for s in self._externalAngleNames)
        if not self._reflist:
            return ["   <<< none specified >>>"]

        lines = []

        format = ("     %6s %5s %5s %5s  " + "%8s " * len(axes) + " TAG")
        values = ('ENERGY', 'H', 'K', 'L') + axes
        lines.append(bold(format % values))

        for n in range(1, len(self._reflist) + 1):
            ref_tuple = self.get_reflection_in_external_angles(n)
            [h, k, l], externalAngles, energy, tag, _ = ref_tuple
            if tag is None:
                tag = ""
            format = ("  %2d %6.3f % 4.2f % 4.2f % 4.2f  " +
                      "% 8.4f " * len(axes) + " %s")
            values = (n, energy / self._multiplier, h, k, l) + externalAngles + (tag,)
            lines.append(format % values)
        return lines
