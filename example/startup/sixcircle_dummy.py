try:
	import diffcalc
except ImportError:
	from gda.data.PathConstructor import createFromProperty
	import sys
	diffcalc_path = createFromProperty("gda.root").split('/plugins')[0] + '/diffcalc' 
	sys.path = [diffcalc_path] + sys.path
	print diffcalc_path + ' added to GDA Jython path.'
	import diffcalc #@UnusedImport
from diffcalc.gdasupport.GdaDiffcalcObjectFactory import createDiffcalcObjects, addObjectsToNamespace

demoCommands = []
demoCommands.append( "newub 'cubic'" )
demoCommands.append( "setlat 'cubic' 1 1 1 90 90 90" )
demoCommands.append( "pos wl 1" )
demoCommands.append( "pos sixc [0 90 0 45 45 0]" )
demoCommands.append( "addref 1 0 1" )
demoCommands.append( "pos phi 90" )
demoCommands.append( "addref 0 1 1" )
demoCommands.append( "checkub" )
demoCommands.append( "ub" )
demoCommands.append( "hklmode" )



# <<< Start Modifying
print "="*80
diffcalcObjects = createDiffcalcObjects(
	dummyAxisNames = ('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'),
	dummyEnergyName = 'en',
	geometryPlugin = 'sixc',
	hklverboseVirtualAnglesToReport=('2theta','Bin','Bout','azimuth'),
	demoCommands = demoCommands
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands
addObjectsToNamespace(diffcalcObjects, globals())
