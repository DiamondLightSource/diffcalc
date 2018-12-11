###
# Copyright 2008-2018 Diamond Light Source Ltd.
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
from math import pi, asin, sin, isnan
from diffcalc.hkl.you.calc import cut_at_minus_pi
from diffcalc.hardware import cut_angle_at

DEBUG = False

try:
    from gda.device.scannable.scannablegroup import \
        ScannableMotionWithScannableFieldsBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import \
        ScannableMotionWithScannableFieldsBase

from diffcalc.util import getMessageFromException, DiffcalcException, TODEG,\
    TORAD, bound, cross3, SMALL


class _DynamicDocstringMetaclass(type):

    def _get_doc(self):
        return Qtrans.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment


def _simulateMoveFieldTo(obj, index, val):
    print "Index: %d   Value: %f" % (index, val)
    pos = [None] * len(obj.getParent().getInputNames())
    pos[index] = val
    obj.getParent().simulateMoveTo(pos)


class Qtrans(ScannableMotionWithScannableFieldsBase):

    if platform.system() != 'Java':
        __metaclass__ = _DynamicDocstringMetaclass  # TODO: Removed to fix Jython

    dynamic_docstring = 'qtrans scannable'


    def _get_doc(self):
        return Qtrans.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment


    def __init__(self, name, diffractometerObject, diffcalcObject):
        self.diffhw = diffractometerObject
        self._diffcalc = diffcalcObject
        self._hkl_reference = [0, 0, 0]
        self._az = 0 # Disambiguate 

        self.setName(name)
        self.setInputNames(['h', 'k', 'l', 'qpar', 'azimuthal'])
        self.setOutputFormat(['%7.5f'] * 5)

        self.completeInstantiation()
        self.setAutoCompletePartialMoveToTargets(True)
        self.dynamic_class_doc = 'qtrans scannable'

        for name in self.getInputNames():
            sc = self.getPart(name)
            sc.simulateMoveTo = _simulateMoveFieldTo


    def rawAsynchronousMoveTo(self, hkl):
        if type(hkl) not in (list, tuple): raise ValueError('Invalid input type for qtrans scannable')
        if len(hkl)!=5: raise ValueError('qtrans device expects five inputs')

        _h = self._hkl_reference[0] if hkl[0] is None else hkl[0]
        _k = self._hkl_reference[1] if hkl[1] is None else hkl[1]
        _l = self._hkl_reference[2] if hkl[2] is None else hkl[2]

        if None in hkl[-2:]:
            pos = self.diffhw.getPosition()  # a tuple
            (hkl_pos , _) = self._diffcalc.angles_to_hkl(pos)
            pol_pos, az_pos, _ = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(hkl_pos, self._hkl_reference)
            if isnan(az_pos):
                az_pos = self._az

        if hkl[3] is None:
            pol = pol_pos
        else:
            if hkl[3] < 0  or hkl[3] > 1: raise ValueError('Invalid input value %f for q-vector projection length in r.l.u.' % hkl[3])
            pol = asin(hkl[3])

        nref_hkl = [i[0] for i in self._diffcalc._ub.ubcalc.n_hkl.tolist()]
        _, az_ref, _ = self._diffcalc._ub.ubcalc.calc_offset_for_hkl([_h, _k, _l], nref_hkl)
        if not az_ref:
            raise DiffcalcException("Cannot define azimuthal direction. Reference vector and scattering vector are parallel.")
        if hkl[4] is None:
            az = az_pos
        else:
            az = hkl[4] * TORAD
        az_ref += az

        try:
            hkl_offset = self._diffcalc._ub.ubcalc.calc_hkl_offset(_h, _k, _l, pol=pol, az=az_ref)
            (pos, _) = self._diffcalc.hkl_to_angles(*hkl_offset)
        except DiffcalcException, e:
            if DEBUG:
                raise
            else:
                raise DiffcalcException(e.message)

        self.diffhw.asynchronousMoveTo(pos)
        self._hkl_reference = [_h, _k, _l]
        self._az = az


    def rawGetPosition(self):
        pos = self.diffhw.getPosition()  # a tuple
        (hkl_pos , _) = self._diffcalc.angles_to_hkl(pos)
        result = list(self._hkl_reference)
        pol, az, _ = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(hkl_pos, self._hkl_reference)
        if pol < SMALL:
            result.extend([0, cut_angle_at(self._az * TODEG, 0)])
        else:
            nref_hkl = [i[0] for i in self._diffcalc._ub.ubcalc.n_hkl.tolist()]
            _, az_ref, _ = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(self._hkl_reference, nref_hkl)
            az -= az_ref
            qtrans = sin(abs(pol))
            result.extend([qtrans,  cut_angle_at(az * TODEG, 0)])
        return result

    def getFieldPosition(self, i):
        return self.getPosition()[i]

    def isBusy(self):
        return self.diffhw.isBusy()

    def waitWhileBusy(self):
        return self.diffhw.waitWhileBusy()

    def simulateMoveTo(self, hkl):
        if type(hkl) not in (list, tuple): raise ValueError('Invalid input type for qtrans scannable')
        if len(hkl) > 5 or len(hkl) < 4: raise ValueError('qtrans device expects five inputs')
        if hkl[3] < 0 or hkl[3] > 1: raise ValueError('Invalid input value %f for q-vector projection length in r.l.u.' % hkl[3])

        _h = self._hkl_reference[0] if hkl[0] is None else hkl[0]
        _k = self._hkl_reference[1] if hkl[1] is None else hkl[1]
        _l = self._hkl_reference[2] if hkl[2] is None else hkl[2]
        _hkl = [_h, _k, _l]

        if None in hkl[-2:]:
            pos = self.diffhw.getPosition()  # a tuple
            (hkl_pos , _) = self._diffcalc.angles_to_hkl(pos)
            pol_pos, az_pos, _ = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(hkl_pos, self._hkl_reference)

        if hkl[3] is None:
            pol = pol_pos
        else:
            if hkl[3] < 0  or hkl[3] > 1: raise ValueError('Invalid input value %f for q-vector projection length in r.l.u.' % hkl[3])
            pol = asin(hkl[3])

        if hkl[4] is None:
            az_ref = az_pos
        else:
            nref_hkl = [i[0] for i in self._diffcalc._ub.ubcalc.n_hkl.tolist()]
            az = hkl[4] * TORAD
            _, az_ref, _ = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(self._hkl_reference, nref_hkl)
            if not az_ref:
                raise DiffcalcException("Cannot define azimuthal direction. Reference vector and scattering vector are parallel.")
            az_ref += az

        try:
            hkl_offset = self._diffcalc._ub.ubcalc.calc_hkl_offset(*_hkl, pol=pol, az=az_ref)
            (pos, params) = self._diffcalc.hkl_to_angles(*hkl_offset)
        except DiffcalcException, e:
            if DEBUG:
                raise
            else:
                raise DiffcalcException(e.message)

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

