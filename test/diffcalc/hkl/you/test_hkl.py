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


from mock import Mock, call
from diffcalc import settings

import diffcalc
from test.diffcalc.test_hardware import SimpleHardwareAdapter
from diffcalc.hkl.you.geometry import SixCircle
diffcalc.util.DEBUG = True


hkl = None
def setup_module():
    global hkl
    settings.hardware=SimpleHardwareAdapter([])
    settings.geometry=SixCircle()
    settings.angles_to_hkl_function=Mock()
    settings.ubcalc_strategy=Mock()
    settings.geometry.fixed_constraints = {}
    
    from diffcalc.hkl.you import hkl
    reload(hkl)
    
    hkl.hklcalc = Mock()
    hkl.hklcalc.constraints.report_constraints_lines.return_value = ['report1', 'report2']


def test_con_with_1_constraint():
    hkl.con('cona')
    hkl.hklcalc.constraints.constrain.assert_called_with('cona')

def test_con_with_1_constraint_with_value():
    hkl.con('cona', 123)
    hkl.hklcalc.constraints.constrain.assert_called_with('cona')
    hkl.hklcalc.constraints.set_constraint.assert_called_with('cona', 123)

def test_con_with_3_constraints():
    hkl.con('cona', 'conb', 'conc')
    hkl.hklcalc.constraints.clear_constraints.assert_called()
    calls = [call('cona'), call('conb'), call('conc')]
    hkl.hklcalc.constraints.constrain.assert_has_calls(calls)

def test_con_with_3_constraints_first_val():
    hkl.con('cona', 1, 'conb', 'conc')
    hkl.hklcalc.constraints.clear_constraints.assert_called()
    calls = [call('cona'), call('conb'), call('conc')]
    hkl.hklcalc.constraints.constrain.assert_has_calls(calls)
    hkl.hklcalc.constraints.set_constraint.assert_called_with('cona', 1)

def test_con_with_3_constraints_second_val():
    hkl.con('cona', 'conb', 2, 'conc')
    hkl.hklcalc.constraints.clear_constraints.assert_called()
    calls = [call('cona'), call('conb'), call('conc')]
    hkl.hklcalc.constraints.constrain.assert_has_calls(calls)
    hkl.hklcalc.constraints.set_constraint.assert_called_with('conb', 2)
    
def test_con_with_3_constraints_third_val():
    hkl.con('cona', 'conb', 'conc', 3)
    hkl.hklcalc.constraints.clear_constraints.assert_called()
    calls = [call('cona'), call('conb'), call('conc')]
    hkl.hklcalc.constraints.constrain.assert_has_calls(calls)
    hkl.hklcalc.constraints.set_constraint.assert_called_with('conc', 3)
    
def test_con_with_3_constraints_all_vals():
    hkl.con('cona', 1, 'conb', 2, 'conc', 3)
    hkl.hklcalc.constraints.clear_constraints.assert_called()
    calls = [call('cona'), call('conb'), call('conc')]
    hkl.hklcalc.constraints.constrain.assert_has_calls(calls)
    calls = [call('cona', 1), call('conb', 2), call('conc', 3)]
    hkl.hklcalc.constraints.set_constraint.assert_has_calls(calls)
    
def test_con_messages_and_help_visually():
    hkl.con()
    print "**"
    print hkl.con.__doc__
    
def test_con_message_display_whenn_selecting_an_unimplmented_mode():
    hkl.hklcalc.constraints.is_fully_constrained.return_value = True
    hkl.hklcalc.constraints.is_current_mode_implemented.return_value = False
    hkl.con('phi', 'chi', 'eta')
