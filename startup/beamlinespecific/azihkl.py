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
from diffcalc.util import DiffcalcException

DEBUG = False

try:
    from gda.device.scannable import ScannableBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import ScannableBase

from diffcalc.ub.ub import ubcalc, _to_column_vector_triple


class _DynamicDocstringMetaclass(type):

    def _get_doc(self):
        return AzihklClass.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment


class AzihklClass(ScannableBase):
    'Azimuthal reference reciprocal lattice vector'

    if platform.system() != 'Java':
        __metaclass__ = _DynamicDocstringMetaclass  # TODO: Removed to fix Jython

    dynamic_docstring = 'Azimuthal reference reciprocal lattice vector'

    def _get_doc(self):
        return AzihklClass.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment

    def __init__(self,name):
        self.setName(name)
        self.setLevel(3)
        self.setInputNames(['azih','azik','azil'])
        self.setOutputFormat(['%4.4f', '%4.4f','%4.4f'])

    def asynchronousMoveTo(self,new_position):
        ref_matrix = _to_column_vector_triple(new_position)
        ubcalc.set_n_hkl_configured(ref_matrix)

    def isBusy(self):
        return 0

    def getPosition(self):
        try:
            ref_matrix = ubcalc.n_hkl
            return ref_matrix.T.tolist()[0]
        except DiffcalcException, e:
            print e
