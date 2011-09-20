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
demoCommands.append( "pos sixc [0 60 0 30 1 0]" )
demoCommands.append( "addref 1 0 0" )
demoCommands.append( "pos chi 91" )
demoCommands.append( "addref 0 0 1" )
demoCommands.append( "checkub" )
demoCommands.append( "ub" )
demoCommands.append( "hklmode" )


from diffcalc.gdasupport.scannable.vrmlanimator import VrmlModelDriver, LinearProfile, MoveThread
sixcgrp=VrmlModelDriver('sixcgrp',['alpha','delta','gamma', 'omega', 'chi','phi'], speed=30, host='ws010')
alpha = sixcgrp.alpha
delta = sixcgrp.delta
gamma = sixcgrp.gamma
omega = sixcgrp.omega
chi = sixcgrp.chi
phi = sixcgrp.phi


diffcalcObjects=createDiffcalcObjects(
	#axisScannableList = (alpha, delta, gamma, omega, chi, phi), #@UndefinedVariable
	axesGroupScannable = sixcgrp,
	dummyEnergyName = 'en',
#	energyScannable = dcm1energy, #@UndefinedVariable
	geometryPlugin = 'sixc',
	hklverboseVirtualAnglesToReport=('2theta','Bin','Bout','azimuth'),
	demoCommands = demoCommands
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands;
addObjectsToNamespace( diffcalcObjects, globals() )