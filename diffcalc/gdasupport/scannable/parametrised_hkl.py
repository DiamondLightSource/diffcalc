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
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc import settings
from diffcalc.util import getMessageFromException


class ParametrisedHKLScannable(Hkl):

    def __init__(self, name, inputNames, num_cached_params=0):

        from diffcalc.dc import dcyou as _dc
        Hkl.__init__(self, name, settings.axes_scannable_group, _dc, None)

        self.setName(name)
        self.setInputNames(inputNames)
        self.setOutputFormat(['%7.5f'] * len(inputNames))

        self.parameter_to_hkl = self._diffcalc.angles_to_hkl
        self.hkl_to_parameter = self._diffcalc.hkl_to_angles
        self.num_cached_params = num_cached_params
        self.cached_params = None

        self.completeInstantiation()
        self.setAutoCompletePartialMoveToTargets(True)
        self.dynamic_class_doc = 'Generic Hkl Scannable'


    def rawAsynchronousMoveTo(self, pos):
        self.cached_params = pos[-self.num_cached_params:]
        hkl = self.parameter_to_hkl(pos)
        if isinstance(hkl[0], (int, float)):
            Hkl.rawAsynchronousMoveTo(self, hkl)
        elif isinstance(hkl[0], (tuple, list)):
            (pos, _) = self._diffcalc.hkl_list_to_angles(hkl)
            self.diffhw.asynchronousMoveTo(pos)


    def rawGetPosition(self):
        pos = self.diffhw.getPosition()  # a tuple
        hkl, _ = self._diffcalc.angles_to_hkl(pos)
        pos = self.hkl_to_parameter(list(hkl))
        return pos


    def simulateMoveTo(self, pos):
        lines = ['%s:' % self.name]
        hkl = self.parameter_to_hkl(pos)
        if isinstance(hkl[0], (tuple, list)):
            (angles, _) = self._diffcalc.hkl_list_to_angles(hkl)
            hkl, _ = self._diffcalc.angles_to_hkl(angles)
        #fmt_scn_params = '  '.join([' : %9.4f'] + ['%.4f'] * (len(pos) - 1))
        #lines.append('  ' + self.name + fmt_scn_params % tuple(pos))
        width = max(len(k) for k in self.inputNames)
        fmt = '  %' + str(width) + 's : % 9.4f'
        for idx, k in enumerate(self.inputNames):
            lines.append(fmt % (k, pos[idx]))
        lines.append('\n  ' + 'hkl'.rjust(width) + ' : %9.4f  %.4f  %.4f' % (hkl[0], hkl[1], hkl[2]))
        res = Hkl.simulateMoveTo(self, hkl)
        lines.append(res)
        return '\n'.join(lines)


    def __repr__(self):
        lines = ['%s:' % self.name]
        pos = self.diffhw.getPosition()
        try:
            (hkl, params) = self._diffcalc.angles_to_hkl(pos)
            scn_params = self.hkl_to_parameter(list(hkl))
        except Exception, e:
            return "<%s: %s>" % (self.name, getMessageFromException(e))

        width = max(len(k) for k in params)
        fmt_scn_params = '  '.join([' : %9.4f'] + ['%.4f'] * (len(scn_params) - 1))
        lines.append('  ' + self.name.rjust(width) + fmt_scn_params % scn_params)
        lines.append('  ' + 'hkl'.rjust(width) + ' : %9.4f  %.4f  %.4f' % (hkl[0], hkl[1], hkl[2]))
        lines[-1] = lines[-1] + '\n'
        fmt = '  %' + str(width) + 's : % 9.4f'
        for k in sorted(params):
            lines.append(fmt % (k, params[k]))
        return '\n'.join(lines)
