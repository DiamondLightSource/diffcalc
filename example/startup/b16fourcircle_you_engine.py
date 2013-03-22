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

"""
This script is referenced by b16 directly
"""

import diffcalc
#####

del alpha
from diffcalc.gdasupport.factory import create_objects, add_objects_to_namespace

demoCommands = []

diffcalcObjects = create_objects(
	#axisScannableList = (alpha, delta, omega, chi, phi), #@UndefinedVariable
	axes_group_scannable = _fourc, #@UndefinedVariable
	energy_scannable = energy, #@UndefinedVariable
	energy_scannable_multiplier_to_get_KeV = 0.001,
	geometry = diffcalc.hkl.you.geometry.FourCircle(),
	hklverbose_virtual_angles_to_report=('theta','alpha','beta','psi'),
	demo_commands = demoCommands,
	engine_name = 'you',
	simulated_crystal_counter_name = 'ct'
)

#diffcalcObjects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(diffcalcObjects, globals())

# does not work yet:
diffcalc.gdasupport.factory.override_gda_help_command(globals())
alias('help')

#demoCommands.append( "newub 'cubic'" )
#demoCommands.append( "setlat 'cubic' 1 1 1 90 90 90" )
#demoCommands.append( "pos wl 1" )
#demoCommands.append( "pos fivec [0 60 30 1 0]" )
#demoCommands.append( "addref 1 0 0" )
#demoCommands.append( "pos chi 91" )
#demoCommands.append( "addref 0 0 1" )
#demoCommands.append( "checkub" )
#demoCommands.append( "ub" )
#demoCommands.append( "hklmode" )