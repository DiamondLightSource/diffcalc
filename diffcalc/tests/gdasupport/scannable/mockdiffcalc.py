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

class MockParameterManager:

    def __init__(self):
        self.params = {}

    def set_constraint(self, name, value):
        self.params[name] = value

    def get_constraint(self, name):
        return self.params[name]


class MockDiffcalc:

    def __init__(self, numberAngles):
        self.numberAngles = numberAngles
        self.parameter_manager = MockParameterManager()

    def hkl_to_angles(self, h, k, l):
        params = {}
        params['theta'] = 1.
        params['2theta'] = 12.
        params['Bin'] = 123.
        params['Bout'] = 1234.
        params['azimuth'] = 12345.
        return ([h] * self.numberAngles, params)

    def angles_to_hkl(self, pos):
        if len(pos) != self.numberAngles: raise ValueError
        params = {}
        params['theta'] = 1.
        params['2theta'] = 12.
        params['Bin'] = 123.
        params['Bout'] = 1234.
        params['azimuth'] = 12345.
        return ([pos[0]] * 3, params)

