# ##
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
# ##

from diffcalc.diffcalc_ import create_diffcalc
from diffcalc.hardware import DummyHardwareAdapter
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.util import format_command_help
import diffcalc.hkl.you.geometry

import diffcalc.util
diffcalc.util.DEBUG = True


class TestDiffcalcYouSixc():
    """
    All the components used here are well tested. This integration test is
    mainly to get output for the manual, to help when tweaking the user
    interface, and to make sure it all works together.
    """

    def setup(self):
        axis_names = ('mu', 'delta', 'nu', 'eta', 'chi', 'phi')
#        virtual_angles = ('theta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta')
        hardware = DummyHardwareAdapter(axis_names)
        geometry = diffcalc.hkl.you.geometry.SixCircle()
        self.dc = create_diffcalc(engine_name='you',
                                  geometry=geometry,
                                  hardware=hardware,
                                  raise_exceptions_for_all_errors=True,
                                  ub_persister=UbCalculationNonPersister())


    def test_ub_help_visually(self):
        print "-" * 80 + "\nub:"
        print format_command_help(self.dc.ub.commands)

    def test_hkl_help_visually(self):
        print "-" * 80 + "\nhkl:"
        print format_command_help(self.dc.hkl.commands)

