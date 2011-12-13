from diffcalc.diffractioncalculator import Diffcalc
from diffcalc.geometry.plugin import DiffractometerGeometryPlugin
from diffcalc.geometry.fourc import fourc
from diffcalc.geometry.fivec import fivec
from diffcalc.geometry.sixc import SixCircleGeometry
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.hardware.plugin import HardwareMonitorPlugin
from diffcalc.hardware.scannable import ScannableHardwareMonitorPlugin
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc.gdasupport.scannable.wavelength import Wavelength
from diffcalc.gdasupport.scannable.parameter import DiffractionCalculatorParameter
from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter
try:
    from gda.device.scannable.scannablegroup import ScannableGroup
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.group import ScannableGroup

import time
try:
    from gdascripts.pd.dummy_pds import DummyPD
    from gda.device.scannable import ScannableBase
    from gda.device.scannable import PseudoDevice
    from gda.jython.commands.GeneralCommands import alias
    from gda.jython import JythonServerFacade
except ImportError:
    print "WARNING: ExampleSixCircleStartup.py is not running within the GDA: falling back to the (very minimal!) minigda..."
    from diffcalc.gdasupport.minigda.scannable.dummy import DummyPD
    from diffcalc.gdasupport.minigda.scannable.scannable import Scannable as ScannableBase
    from diffcalc.gdasupport.minigda.scannable.scannable import Scannable as PseudoDevice
    from diffcalc.gdasupport.minigda.terminal import alias
    # Note: minigda will provide an alias method in the rootnamespace



def isObjectScannable(obj):
    return isinstance(obj, PseudoDevice) or isinstance(obj, ScannableBase)

class DiffcalcDemo(object):
    
    def __init__(self, commands = []):
        self.commands = commands
        self.delay = 2
        
    def __call__(self):
        jsf = JythonServerFacade.getInstance()
        for command in self.commands:
            
            jsf.runCommand(command)
            time.sleep(self.delay)
        

geometryPluginByName = {
    'fourc' : fourc,
    'fivec' : fivec,
    'sixc' : SixCircleGeometry,
    'sixc_gamma_on_arm' : SixCircleGammaOnArmGeometry
}


def addObjectsToNamespace(objectDict, namespace):
    for nameToAdd in objectDict.keys():
        if namespace.has_key(nameToAdd):
            raise Exception, "Did not add diffcalc objects/method to namespace, as doing so would overwrite the object %s" % nameToAdd
    namespace.update(objectDict)
    print "Added objects/methods to namespace: %s" % ', '.join(objectDict.keys())


def createDiffcalcObjects(
        dummyAxisNames = None, # list of strings
        axisScannableList = None, # list of single axis scannables
        axesGroupScannable = None, # single scannable group
        dummyEnergyName = None,
        energyScannable = None,
        energyScannableMultiplierToGetKeV = 1,
        geometryPlugin = None, # Class or name (avoids needing to set path before script is run)
        hardwarePluginClass = ScannableHardwareMonitorPlugin,
        mirrorInXzPlane = False,
        hklName = 'hkl',
        hklVirtualAnglesToReport = (),
        hklverboseName = 'hklverbose',
        hklverboseVirtualAnglesToReport = ('2theta','Bin','Bout','azimuth'),
        diffractometerScannableName = None, # e.g. SixCircleGammaOnArmGeometry. If None, determined by geometry-plug in
        demoCommands = [],
        simulatedCrystalCounterName = None
        ):
    print "="*80
    diffcalcObjects = {}
    
    geometryPlugin = determineGeometryPlugin(geometryPlugin)
    geometryPlugin.mirrorInXzPlane = mirrorInXzPlane
    
    diffractometerScannableName = determineDiffractometerScannableName(diffractometerScannableName, geometryPlugin)
    
    objects, diffractometerScannable = createDiffractometerScannableAndPossiblyDummies(dummyAxisNames, axisScannableList, axesGroupScannable, diffractometerScannableName)
    diffcalcObjects.update(objects)

    objects, energyScannable = buildWavelengthAndPossiblyEnergyScannable(dummyEnergyName, energyScannable, energyScannableMultiplierToGetKeV)
    diffcalcObjects.update(objects)
    
    checkHardwarePluginClass(hardwarePluginClass)
    
    # instantiate diffcalc
    diffcalc = Diffcalc(geometryPlugin, hardwarePluginClass(diffractometerScannable, energyScannable, energyScannableMultiplierToGetKeV = energyScannableMultiplierToGetKeV))
    diffcalcObjects['diffcalc_object'] = diffcalc
    diffractometerScannable.setDiffcalcObject(diffcalc)
    
    diffcalcObjects.update( buildHklScannableAndComponents(hklName, diffractometerScannable, diffcalc, hklVirtualAnglesToReport) )
    
    diffcalcObjects.update( buildHklverboseScannable(hklverboseName, diffractometerScannable, diffcalc, hklverboseVirtualAnglesToReport) )
    
    diffcalcObjects.update( createParameterScannables(diffcalc) )
    
    if simulatedCrystalCounterName:
        ct = SimulatedCrystalCounter(simulatedCrystalCounterName, diffractometerScannable, geometryPlugin, diffcalcObjects['wl'])
        diffcalcObjects.update( {simulatedCrystalCounterName: ct})    
        print "Created Simulated Crystal Counter " + simulatedCrystalCounterName
    
    diffcalcObjects.update( createAndAliasCommands(diffcalc) )
    
    diffcalcObjects.update( createAndAliasDiffcalcdemoCommand(demoCommands) )
    # add strings for transformX commands
    diffcalcObjects.update({'on':'on', 'off':'off', 'auto':'auto', 'manual':'manual'})
    

    
    print "="*80
    return diffcalcObjects
    
def determineGeometryPlugin(geometryPlugin):
    if isinstance(geometryPlugin, DiffractometerGeometryPlugin):
        return geometryPlugin
    elif type(geometryPlugin) is str:
        try:
            return geometryPluginByName[geometryPlugin]()
        except KeyError:
            raise KeyError, "If specifying geometry inputGeometryPlugin by name (rather than by passing an plugin instance),\n the name must be one of:\n  %s" % ', '.join(geometryPluginByName.keys())
    else:
        raise TypeError, "inputGeometryPlugin must be an instance of a DiffractometerPlugin or a string from:\n  %s" % ', '.join(geometryPluginByName.keys())

def determineDiffractometerScannableName(diffractometerScannableName, geometryPlugin):
    if diffractometerScannableName is None:
        return geometryPlugin.getName()
    elif type(diffractometerScannableName) is str:
        return diffractometerScannableName
    else:
        raise TypeError, "if set, diffractometerScannableName must be a string. Leave as None to default to the geometry plugin name.\n diffractometerScannableName was: %s" % `diffractometerScannableName`

def createDiffractometerScannableAndPossiblyDummies(dummyAxisNames, axesScannableList, axesGroupScannable, diffractometerScannableName):
    # build diffractometer-scannable (and possibly scannable-group and/or dummy axes)
    objects = {}
    
    def createDummyMotorScannables(nameList):
        result = []
        for name in nameList:
            result.append( DummyPD(name) )
            print "Created DummyPD: %s" % name
        return result

    if sum([arg is not None for arg in [dummyAxisNames, axesScannableList, axesGroupScannable]]) != 1:
        raise ValueError, "Specify only one of dummyAxisNames, inputAxisScannables or inputAxesGroupScannable"
    if dummyAxisNames:
        axesScannableList = createDummyMotorScannables(dummyAxisNames)
        objects.update(dict(zip(dummyAxisNames,axesScannableList)))
    if axesScannableList:
        axesGroupScannable = ScannableGroup(diffractometerScannableName+'_group', axesScannableList)
    diffractometerScannable = DiffractometerScannableGroup(diffractometerScannableName, None, axesGroupScannable)
    print "Created diffractometer scannable:", diffractometerScannableName
    objects[diffractometerScannableName] = diffractometerScannable
    return objects, diffractometerScannable

def buildWavelengthAndPossiblyEnergyScannable(dummyEnergyName, energyScannable, energyScannableMultiplierToGetKeV):
    objects = {}
    
    def createEnergyScannable(name):
        scn = DummyPD(name)
        scn.asynchronousMoveTo(12.39842)
        print "Created dummy energy scannable: ", name
        print "Set dummy energy to 1 Angstrom"
        return scn
    
    if sum([arg is not None for arg in [dummyEnergyName, energyScannable]]) != 1:
        raise ValueError, "Specify only one of dummyEnergyName or energyScannable"
    if dummyEnergyName:
        if not isinstance(dummyEnergyName, str):
            raise TypeError, "dummyEnergyName must be a string. dummyEnergyName was: %s" % ` dummyEnergyName`
        energyScannable = createEnergyScannable(dummyEnergyName)
        objects[dummyEnergyName] = energyScannable
    if not isObjectScannable(energyScannable):
        raise TypeError, "energyScannable must Scannable. energyScannable was: %s" % `energyScannable`
    
    # create wavelength scannable
    objects['wl'] = Wavelength('wl', energyScannable, energyScannableMultiplierToGetKeV)
    print "Created wavelength scannable: wl"
    return objects, energyScannable

def checkHardwarePluginClass(hardwarePluginClass):
    try:
        if not issubclass(hardwarePluginClass, HardwareMonitorPlugin):
            raise ValueError, "hardwarePluginClass must be a HardwareMonitorPlugin, not a %s" % `type(hardwarePluginClass)`
    except TypeError: 
        raise TypeError, "hardwarePluginClass must be class not an instance"

def buildHklScannableAndComponents(hklScannableName, diffractometerScannable, diffcalc, hklVirtualAnglesToReport):
    objects = {}
    if type(hklScannableName) is not str:
        raise TypeError, "hklScannableName must be a string. hklScannableName was: %s" % `hklScannableName`
    hkl = Hkl(hklScannableName, diffractometerScannable, diffcalc, hklVirtualAnglesToReport)
    objects[hklScannableName] = hkl
    objects['h'] = hkl.h
    objects['k'] = hkl.k
    objects['l'] = hkl.l
    if len(hklVirtualAnglesToReport) == 0:
        print "Created hkl scannable:", hklScannableName
    else:
        print "Created hkl scannable: %s. Reports the virtual angles: %s" %(hklScannableName, ', '.join(hklVirtualAnglesToReport))
    print "Created hkl component scannables: h, k & l"
    return objects
    
def buildHklverboseScannable(hklverboseScannableName, diffractometerScannable, diffcalc, hklverboseVirtualAnglesToReport):
    objects = {}
    if hklverboseScannableName:
        if type(hklverboseScannableName) is not str:
            raise TypeError, "hklverboseScannableName must be a string, or None. hklverboseScannableName was: %s" % `hklverboseScannableName`
        objects[hklverboseScannableName] = Hkl(hklverboseScannableName, diffractometerScannable, diffcalc, hklverboseVirtualAnglesToReport)
        if len(hklverboseVirtualAnglesToReport) == 0:
            print "Created verbose hkl scannable:", hklverboseScannableName
        else:
            print "Created verbose hkl scannable: %s. Reports the virtual angles: %s" %(hklverboseScannableName, ', '.join(hklverboseVirtualAnglesToReport) )
    return objects

def createParameterScannables(diffcalc):
    objects = {}
    paramNames = diffcalc._getParameterNames()
    axisNames = diffcalc._getAxisNames()
    for param in paramNames:
        scnname = param
        if param in axisNames:
            scnname+='_par'
        objects[scnname] = DiffractionCalculatorParameter(scnname, param, diffcalc)
        print "Created parameter scannable:", scnname
    return objects

def createAndAliasCommands(diffcalc):
    objects = {}
    for command_group in [diffcalc.ubcommands, diffcalc.hklcommands, diffcalc.mappercommands]:
        commandNames = filter(lambda s:s[0]!='_', dir(command_group))
        for name in commandNames:
            if name in objects:
                raise Exception("Duplicate command: " + name)
            objects[name] = command_group.__getattribute__(name)
            alias(name)
            print "Aliased command:", name
    objects['checkub'] = diffcalc.checkub
    alias('checkub')
    print "Aliased command: checkub"
    return objects

def createAndAliasDiffcalcdemoCommand(demoCommands):
    objects = {}
    objects['diffcalcdemo'] = DiffcalcDemo(demoCommands)
    alias('diffcalcdemo')
    print "Aliased command: diffcalcdemo"
    print "="*80
    print "Try the following:"
    for line in demoCommands:
        print line
    print
    print "Or type 'diffcalcdemo' to run this script (Caution, will move the diffractometer!)"
    return objects