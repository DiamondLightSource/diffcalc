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
from math import pi, sqrt, acos, cos
try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

DEBUG = False

try:
    from gda.device.scannable.scannablegroup import \
        ScannableMotionBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import \
        ScannableMotionBase

from diffcalc.util import DiffcalcException, bound, SMALL, dot3


class _DynamicDocstringMetaclass(type):

    def _get_doc(self):
        return Qtrans.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment


class Qtrans(ScannableMotionBase):

    if platform.system() != 'Java':
        __metaclass__ = _DynamicDocstringMetaclass  # TODO: Removed to fix Jython

    dynamic_docstring = 'qtrans scannable'


    def _get_doc(self):
        return Qtrans.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment


    def __init__(self, name, diffractometerObject, diffcalcObject):
        self.diffhw = diffractometerObject
        self._diffcalc = diffcalcObject

        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(['%7.5f'])

        self.dynamic_class_doc = 'qtrans scannable'


    def asynchronousMoveTo(self, newpos):

        pos = self.diffhw.getPosition()  # a tuple
        (hkl_pos , _) = self._diffcalc.angles_to_hkl(pos)

        nref_hkl = [i[0] for i in self._diffcalc._ub.ubcalc.n_hkl.tolist()]
        pol, az_nref, sc = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(hkl_pos, nref_hkl)
        if pol < SMALL:
            az_nref = 0
        sc_nref_hkl = [sc * v for v in nref_hkl]

        _ubm = self._diffcalc._ub.ubcalc._get_UB()
        qvec = _ubm * matrix(hkl_pos).T
        qvec_rlu = sqrt(dot3(qvec, qvec)) * self._diffcalc._ub.ubcalc.get_hkl_plane_distance(nref_hkl) / (2.*pi)

        try:
            newpol = acos(bound(newpos / qvec_rlu))
        except AssertionError:
            raise DiffcalcException("Scattering vector projection value of %.5f r.l.u. unreachable." % newpos)

        try:
            hkl_offset = self._diffcalc._ub.ubcalc.calc_hkl_offset(*sc_nref_hkl, pol=newpol, az=az_nref)
            (pos, _) = self._diffcalc.hkl_to_angles(*hkl_offset)
        except DiffcalcException, e:
            if DEBUG:
                raise
            else:
                raise DiffcalcException(e.message)

        self.diffhw.asynchronousMoveTo(pos)


    def getPosition(self):
        pos = self.diffhw.getPosition()  # a tuple
        (hkl_pos , _) = self._diffcalc.angles_to_hkl(pos)
        nref_hkl = [i[0] for i in self._diffcalc._ub.ubcalc.n_hkl.tolist()]
        pol = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(hkl_pos, nref_hkl)[0]
        _ubm = self._diffcalc._ub.ubcalc._get_UB()
        qvec = _ubm * matrix(hkl_pos).T
        sc = sqrt(dot3(qvec, qvec)) * self._diffcalc._ub.ubcalc.get_hkl_plane_distance(nref_hkl) / (2.*pi)
        res = sc * cos(pol)
        return res

    def isBusy(self):
        return self.diffhw.isBusy()

    def waitWhileBusy(self):
        return self.diffhw.waitWhileBusy()

    def simulateMoveTo(self, newpos):

        pos = self.diffhw.getPosition()  # a tuple
        (hkl_pos , _) = self._diffcalc.angles_to_hkl(pos)

        nref_hkl = [i[0] for i in self._diffcalc._ub.ubcalc.n_hkl.tolist()]
        pol, az_nref, sc = self._diffcalc._ub.ubcalc.calc_offset_for_hkl(hkl_pos, nref_hkl)
        if pol < SMALL:
            az_nref = 0
        sc_nref_hkl = [sc * v for v in nref_hkl]

        _ubm = self._diffcalc._ub.ubcalc._get_UB()
        qvec = _ubm * matrix(hkl_pos).T
        qvec_rlu = sqrt(dot3(qvec, qvec)) * self._diffcalc._ub.ubcalc.get_hkl_plane_distance(nref_hkl) / (2.*pi)

        try:
            newpol = acos(bound(newpos / qvec_rlu))
        except AssertionError:
            raise DiffcalcException("Scattering vector projection value  of %.5f r.l.u. unreachable." % newpos)

        try:
            hkl_offset = self._diffcalc._ub.ubcalc.calc_hkl_offset(*sc_nref_hkl, pol=newpol, az=az_nref)
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

