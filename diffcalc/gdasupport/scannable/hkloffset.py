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
import platform

DEBUG = False

try:
    from gda.device.scannable.scannablegroup import \
        ScannableMotionWithScannableFieldsBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import \
        ScannableMotionWithScannableFieldsBase

from diffcalc.util import getMessageFromException, DiffcalcException, TODEG,\
    TORAD


class _DynamicDocstringMetaclass(type):

    def _get_doc(self):
        return HklOffset.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment


class HklOffset(ScannableMotionWithScannableFieldsBase):
    
    if platform.system() != 'Java':
        __metaclass__ = _DynamicDocstringMetaclass  # TODO: Removed to fix Jython

    dynamic_docstring = 'Hkl Offset Scannable'

    def _get_doc(self):
        return HklOffset.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment

    def __init__(self, name, diffractometerObject, diffcalcObject,
                 virtualAnglesToReport=None):
        self.diffhw = diffractometerObject
        self._diffcalc = diffcalcObject
        if type(virtualAnglesToReport) is str:
            virtualAnglesToReport = (virtualAnglesToReport,)
        self.vAngleNames = virtualAnglesToReport
        self._hkl_reference = [0, 0, 0]

        self.setName(name)
        self.setInputNames(['h', 'k', 'l', 'polar', 'azimuthal'])
        self.setOutputFormat(['%7.5f'] * 5)
        if self.vAngleNames:
            self.setExtraNames(self.vAngleNames)
            self.setOutputFormat(['%7.5f'] * (5 + len(self.vAngleNames)))

        self.completeInstantiation()
        self.setAutoCompletePartialMoveToTargets(True)
        self.dynamic_class_doc = 'Hkl Offset Scannable xyz'

    def rawAsynchronousMoveTo(self, hkl):
        if len(hkl) != 5: raise ValueError('Hkl Offset device expects five inputs')
        try:
            self._hkl_reference = hkl[:3]
            pol, az = hkl[-2] * TORAD, hkl[-1] * TORAD
            hkl_offset = self._diffcalc._ub.ubcalc.calc_hkl_offset(*self._hkl_reference, pol=pol, az=az)
            (pos, _) = self._diffcalc.hkl_to_angles(*hkl_offset)
        except DiffcalcException, e:
            if DEBUG:
                raise
            else:
                raise DiffcalcException(e.message)
        self.diffhw.asynchronousMoveTo(pos)

    def rawGetPosition(self):
        pos = self.diffhw.getPosition()  # a tuple
        (hkl_pos , params) = self._diffcalc.angles_to_hkl(pos)
        result = list(self._hkl_reference)
        pol, az = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(hkl_pos, self._hkl_reference)
        result.extend([pol * TODEG, az * TODEG])
        if self.vAngleNames:
            for vAngleName in self.vAngleNames:
                result.append(params[vAngleName])
        return result

    def getFieldPosition(self, i):
        return self.getPosition()[i]

    def isBusy(self):
        return self.diffhw.isBusy()

    def waitWhileBusy(self):
        return self.diffhw.waitWhileBusy()

    def simulateMoveTo(self, hkl):
        if type(hkl) not in (list, tuple):
            raise ValueError('Hkl Offset device expects five inputs')
        if len(hkl) != 5:
            raise ValueError('Hkl Offset device expects five inputs')
        pol, az = hkl[-2] * TORAD, hkl[-1] * TORAD
        hkl_offset = self._diffcalc._ub.ubcalc.calc_hkl_offset(*hkl[:3], pol=pol, az=az)
        (pos, params) = self._diffcalc.hkl_to_angles(*hkl_offset)

        width = max(len(k) for k in (params.keys() + list(self.diffhw.getInputNames())))
        fmt = '  %' + str(width) + 's : % 9.4f'

        lines = ['simulated hkl: %9.4f  %.4f  %.4f' % (hkl_offset[0],hkl_offset[1],hkl_offset[2]),
                 self.diffhw.getName() + ' would move to:']
        for idx, name in enumerate(self.diffhw.getInputNames()):
            lines.append(fmt % (name, pos[idx]))
        lines[-1] = lines[-1] + '\n'
        for k in sorted(params):
            lines.append(fmt % (k, params[k]))
        return '\n'.join(lines)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        lines = ['hkloffset:']
        pos = self.diffhw.getPosition()
        try:
            (hkl_pos, params) = self._diffcalc.angles_to_hkl(pos)
            pol, az = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(hkl_pos, self._hkl_reference)
        except Exception, e:
            return "<hkloffser: %s>" % getMessageFromException(e)

        width = max(len(k) for k in params)
        lines.append('  ' + 'hkloffset'.rjust(width) + ' : %9.4f  %.4f  %.4f  %.4f  %.4f' % (self._hkl_reference[0],
                                                                                       self._hkl_reference[1],
                                                                                       self._hkl_reference[2],
                                                                                       pol * TODEG, az * TODEG))
        lines[-1] = lines[-1] + '\n'
        fmt = '  %' + str(width) + 's : % 9.4f'
        for k in sorted(params):
            lines.append(fmt % (k, params[k]))
        return '\n'.join(lines)
