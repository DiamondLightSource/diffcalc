"""
This script is referenced by b16 directly
"""

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

from diffcalc.gdasupport.diffcalc_factory import create_objects, add_objects_to_namespace

demoCommands = []
demoCommands.append( "newub 'cubic'" )
demoCommands.append( "setlat 'cubic' 1 1 1 90 90 90" )
demoCommands.append( "pos wl 1" )
demoCommands.append( "pos fivec [0 60 30 1 0]" )
demoCommands.append( "addref 1 0 0" )
demoCommands.append( "pos chi 91" )
demoCommands.append( "addref 0 0 1" )
demoCommands.append( "checkub" )
demoCommands.append( "ub" )
demoCommands.append( "hklmode" )

diffcalcObjects = create_objects(
	#axisScannableList = (alpha, delta, omega, chi, phi), #@UndefinedVariable
	axes_group_scannable = dif, #@UndefinedVariable
	energy_scannable = energy, #@UndefinedVariable
	energy_scannable_multiplier_to_get_KeV = 0.001,
	geometry_plugin = 'fivec',
	hklverbose_virtual_angles_to_report=('2theta','Bin','Bout','azimuth'),
	demo_commands = demoCommands,
	simulated_crystal_counter_name = 'ct'
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(diffcalcObjects, globals())

