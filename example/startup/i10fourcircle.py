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
	import diffcalc
#####

from gdascripts.pd.dummy_pds import DummyPD
from diffcalc.gdasupport.factory import create_objects, add_objects_to_namespace

demoCommands = []
demoCommands.append( "newub 'cubic'" )
demoCommands.append( "setlat 'cubic' 1 1 1 90 90 90" )
demoCommands.append( "pos wl 1" )
demoCommands.append( "pos fourc [60 30 90 0]" )
demoCommands.append( "addref 0 0 1" )
demoCommands.append( "addref 1 0 0 [60 30 0 0] 12.39842" )
demoCommands.append( "checkub" )
demoCommands.append( "ub" )
demoCommands.append( "hklmode" )

#rpenergy = DummyPD('rpenergy')
#rpenergy.moveTo(12398.42)
#exec('del tth, th, chi, phi')
CREATE_DUMMY_AXES = False
if CREATE_DUMMY_AXES:
	print "Creating Dummy Axes: tth, th, chi, phi and rpenergy"
	tth = DummyPD('tth'); tth.setLowerGdaLimits(-80); tth.setUpperGdaLimits(260)
	th  = DummyPD('th');th.setLowerGdaLimits(-100); th.setUpperGdaLimits(190)
	chi = DummyPD('chi'); chi.setLowerGdaLimits(86); chi.setUpperGdaLimits(94)
	phi = DummyPD('phi')
	rpenergy = DummyPD('rpenergy')
	rpenergy.moveTo(12398.42)
	print "Moved rpenergy to 12398.42 eV (1 Angstrom)"
	chi.moveTo(90)
	print "Moved chi to 90"
	print "="*80

diffcalcObjects = create_objects(
	axis_scannable_list = (tth, th, chi, phi),
	energy_scannable = denergy,
	energy_scannable_multiplier_to_get_KeV = .001,
	geometry = 'fourc',
	hklverbose_virtual_angles_to_report=('2theta','Bin','Bout','azimuth'),
	demo_commands = demoCommands
)
diffcalcObjects['alpha_par'] = diffcalcObjects['alpha']
del diffcalcObjects['alpha']
diffcalcObjects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(diffcalcObjects, globals())
