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

try:
	import diffcalc
except ImportError:
	from gda.data.PathConstructor import createFromProperty
	import sys
	diffcalc_path = createFromProperty("gda.root").split('/plugins')[0] + '/diffcalc' 
	sys.path = [diffcalc_path] + sys.path
	print diffcalc_path + ' added to GDA Jython path.'
	import diffcalc #@UnusedImport
from diffcalc.gdasupport.factory import create_objects, add_objects_to_namespace
from diffcalc.gdasupport.scannable.vrmlanimator import VrmlModelDriver, LinearProfile, MoveThread
from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter
from socket import gethostname

demoCommands = []
demoCommands.append( "newub 'cubic'" )
demoCommands.append( "setlat 'cubic' 1 1 1 90 90 90" )
demoCommands.append( "pos wl 1" )
demoCommands.append( "pos sixc [0 60 0 30 1 1]" )
demoCommands.append( "addref 1 0 0" )
demoCommands.append( "pos chi 91" )
demoCommands.append( "addref 0 0 1" )
demoCommands.append( "checkub" )
demoCommands.append( "ub" )
demoCommands.append( "hklmode" )


sixcgrp=VrmlModelDriver('sixcgrp',['alpha','delta','gamma', 'omega', 'chi','phi'], speed=30, host='localhost')
alpha = sixcgrp.alpha
delta = sixcgrp.delta
gamma = sixcgrp.gamma
omega = sixcgrp.omega
chi = sixcgrp.chi
phi = sixcgrp.phi

print "="*80
print "Run from diffcalc/models (in Bash):"
print "python vrml_animator.py sixc.wrl 4567 alpha delta gamma omega chi phi"
print "="*80
diffcalcObjects = create_objects(
	axes_group_scannable = sixcgrp,
	dummy_energy_name = 'en',
	geometry_plugin = 'sixc',
	hklverbose_virtual_angles_to_report=('2theta','Bin','Bout','azimuth'),
	simulated_crystal_counter_name = 'ct',
	demo_commands = demoCommands
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(diffcalcObjects, globals())

ct.setChiMissmount(1) #@UndefinedVariable
ct.setPhiMissmount(1) #@UndefinedVariable
