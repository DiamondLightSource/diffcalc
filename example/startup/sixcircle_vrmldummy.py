try:
	import diffcalc
except ImportError:
	from gda.data.PathConstructor import createFromProperty
	import sys
	diffcalc_path = createFromProperty("gda.root").split('/plugins')[0] + '/diffcalc' 
	sys.path = [diffcalc_path] + sys.path
	print diffcalc_path + ' added to GDA Jython path.'
	import diffcalc #@UnusedImport
from diffcalc.gdasupport.diffcalc_factory import create_objects, add_objects_to_namespace
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