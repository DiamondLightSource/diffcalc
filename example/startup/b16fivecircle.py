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

from diffcalc.gdasupport.GdaDiffcalcObjectFactory import createDiffcalcObjects, addObjectsToNamespace

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

diffcalcObjects = createDiffcalcObjects(
	axisScannableList = (alpha, delta, omega, chi, phi), #@UndefinedVariable
	energyScannable = energy, #@UndefinedVariable
	energyScannableMultiplierToGetKeV = 0.001,
	geometryPlugin = 'fivec',
	hklverboseVirtualAnglesToReport=('2theta','Bin','Bout','azimuth'),
	demoCommands = demoCommands,
	simulatedCrystalCounterName = 'ct'
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands
addObjectsToNamespace(diffcalcObjects, globals())

