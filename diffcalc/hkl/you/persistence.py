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
from diffcalc.ub.calcstate import UBCalcStateEncoder, UBCalcState
from diffcalc.util import DiffcalcException, TODEG


class YouStateEncoder(UBCalcStateEncoder):

    def default(self, obj):

        if isinstance(obj, UBCalcState):
            d = UBCalcStateEncoder.default(self, obj)

            from diffcalc.hkl.you.hkl import constraint_manager
            d['constraints'] = constraint_manager.all
            return d

        return UBCalcStateEncoder.default(self, obj)

    @staticmethod
    def decode_ubcalcstate(state, geometry, diffractometer_axes_names, multiplier):

        # Backwards compatibility code
        try:
            cons_dict = state['constraints']
            from diffcalc.hkl.you.hkl import constraint_manager
            for cons_name, val in cons_dict.iteritems():
                try:
                    constraint_manager.constrain(cons_name)
                    if val is not None:
                        constraint_manager.set_constraint(cons_name, val * TODEG)
                except DiffcalcException:
                    print 'WARNING: Ignoring constraint %s' % cons_name
        except KeyError:
            pass

        return UBCalcStateEncoder.decode_ubcalcstate(state, geometry, diffractometer_axes_names, multiplier)
