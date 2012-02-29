import time
from diffcalc.help import format_command_help, ExternalCommand

try:
    from gda.device.scannable.scannablegroup import ScannableGroup
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.group import ScannableGroup

try:
    from gdascripts.pd.dummy_pds import DummyPD
    from gda.device.scannable import ScannableBase
    from gda.device.scannable import PseudoDevice
    from gda.jython.commands.GeneralCommands import alias
    from gda.jython import JythonServerFacade
except ImportError:
    print "WARNING: ExampleSixCircleStartup.py is not running within the GDA:"
    print "         falling back to the (very minimal!) minigda..."

    from diffcalc.gdasupport.minigda.scannable.dummy import DummyPD
    from diffcalc.gdasupport.minigda.scannable.scannable import \
        Scannable as ScannableBase
    from diffcalc.gdasupport.minigda.scannable.scannable import \
        Scannable as PseudoDevice
    # from diffcalc.gdasupport.minigda.terminal import alias
    # Note: minigda will provide an alias method in the rootnamespace

from diffcalc.diffractioncalculator import create_diffcalc_vlieg, \
    create_diffcalc_willmot
from diffcalc.geometry.plugin import DiffractometerGeometryPlugin
from diffcalc.geometry.fourc import fourc
from diffcalc.geometry.fivec import fivec
from diffcalc.geometry.sixc import SixCircleGeometry
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.hardware.plugin import HardwareMonitorPlugin
from diffcalc.hardware.scannable import ScannableHardwareMonitorPlugin
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc import gdasupport
from diffcalc.gdasupport.scannable.wavelength import Wavelength
from diffcalc.gdasupport.scannable.parameter import \
    DiffractionCalculatorParameter
from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter


def isObjectScannable(obj):
    return isinstance(obj, PseudoDevice) or isinstance(obj, ScannableBase)


class DiffcalcDemo(object):

    def __init__(self, commands=[]):
        self.commands = commands
        self.delay = 2

    def __call__(self):
        jsf = JythonServerFacade.getInstance()
        for command in self.commands:

            jsf.runCommand(command)
            time.sleep(self.delay)


geometryPluginByName = {
    'fourc': fourc,
    'fivec': fivec,
    'sixc': SixCircleGeometry,
    'sixc_gamma_on_arm': SixCircleGammaOnArmGeometry
}


def addObjectsToNamespace(objectDict, namespace):
    for nameToAdd in objectDict.keys():
        if nameToAdd in namespace:
            raise Exception(
                "Did not add diffcalc objects/method to namespace, as doing "
                "so would overwrite the object %s" % nameToAdd)
    namespace.update(objectDict)
    print "Added objects/methods to namespace: ", ', '.join(objectDict.keys())


def createDiffcalcObjects(
        dummyAxisNames=None,  # list of strings
        axisScannableList=None,  # list of single axis scannables
        axesGroupScannable=None,  # single scannable group
        dummyEnergyName=None,
        energyScannable=None,
        energyScannableMultiplierToGetKeV=1,
        geometryPlugin=None,    # Class or name
                                # (avoids setting path before script is run)
        hardwarePluginClass=ScannableHardwareMonitorPlugin,
        mirrorInXzPlane=False,
        hklName='hkl',
        hklVirtualAnglesToReport=(),
        hklverboseName='hklverbose',
        hklverboseVirtualAnglesToReport=('2theta', 'Bin', 'Bout', 'azimuth'),
        diffractometerScannableName=None,   # e.g. SixCircleGammaOnArmGeometry.
                                            # or determined by geometryPlugin
        demoCommands=[],
        simulatedCrystalCounterName=None,
        engineName='vlieg',
        raiseExceptionsForAllErrors=True
        ):
    print "=" * 80
    objects = {}

    geometryPlugin = determineGeometryPlugin(geometryPlugin)
    geometryPlugin.mirrorInXzPlane = mirrorInXzPlane

    diffractometerScannableName = determineDiffractometerScannableName(
        diffractometerScannableName, geometryPlugin)

    objects_, diffractometerScannable = \
        createDiffractometerScannableAndPossiblyDummies(
            dummyAxisNames, axisScannableList, axesGroupScannable,
            diffractometerScannableName)
    objects.update(objects_)

    objects_, energyScannable = buildWavelengthAndPossiblyEnergyScannable(
        dummyEnergyName, energyScannable, energyScannableMultiplierToGetKeV)
    objects.update(objects_)

    checkHardwarePluginClass(hardwarePluginClass)
    m = energyScannableMultiplierToGetKeV
    hardware = hardwarePluginClass(diffractometerScannable, energyScannable,
                                   energyScannableMultiplierToGetKeV=m)

    # instantiate diffcalc
    engineName = engineName.lower()
    if engineName == 'vlieg':
        diffcalc = create_diffcalc_vlieg(geometryPlugin, hardware,
                                         raiseExceptionsForAllErrors)
    elif engineName == 'willmott':
        diffcalc = create_diffcalc_willmot(geometryPlugin, hardware,
                                           raiseExceptionsForAllErrors)
    else:
        raise KeyError(
            "The engine '%s' was not recognised. Try 'vlieg' or 'willmott'" %
            engineName)

    objects['diffcalc_object'] = diffcalc
    diffractometerScannable.setDiffcalcObject(diffcalc)

    objects.update(buildHklScannableAndComponents(
        hklName, diffractometerScannable, diffcalc, hklVirtualAnglesToReport))

    objects.update(buildHklverboseScannable(
        hklverboseName, diffractometerScannable, diffcalc,
        hklverboseVirtualAnglesToReport))

    objects.update(createParameterScannables(diffcalc))

    if simulatedCrystalCounterName:
        ct = SimulatedCrystalCounter(
            simulatedCrystalCounterName, diffractometerScannable,
            geometryPlugin, objects['wl'])
        objects.update({simulatedCrystalCounterName: ct})
        print "Created Simulated Crystal Counter", simulatedCrystalCounterName

    print "UB"
    print "=="
    objects.update(expose_and_alias_commands(diffcalc.ub.commands))
    print "hkl"
    print "==="
    objects.update(expose_and_alias_commands(diffcalc.hkl.commands))
    print "Tutorial"
    print ""
    objects.update(createAndAliasDiffcalcdemoCommand(demoCommands))
    # add strings for transformX commands
    objects.update(
        {'on': 'on', 'off': 'off', 'auto': 'auto', 'manual': 'manual'})

    print "=" * 80

    objects['ub'].__doc__ = format_command_help(diffcalc.ub.commands)
    #objects['hkl'].dynamic_docstring = format_command_help(diffcalc.hklcommands)
    Hkl.dynamic_docstring = format_command_help(diffcalc.hkl.commands)
    #objects['hkl'].__doc__ = format_command_help(diffcalc.hklcommands)
    return objects


def determineGeometryPlugin(geometryPlugin):
    if isinstance(geometryPlugin, DiffractometerGeometryPlugin):
        return geometryPlugin
    elif type(geometryPlugin) is str:
        try:
            return geometryPluginByName[geometryPlugin]()
        except KeyError:
            raise KeyError(
                "If specifying geometry inputGeometryPlugin by name (rather "
                "than by passing an plugin instance),\n the name must be one "
                "of:\n  %s" % ', '.join(geometryPluginByName.keys()))
    else:
        raise TypeError(
                "inputGeometryPlugin must be an instance of a "
                "DiffractometerPlugin or a string from:\n  %s" %
                ', '.join(geometryPluginByName.keys()))


def determineDiffractometerScannableName(diffractometerScannableName,
                                         geometryPlugin):
    if diffractometerScannableName is None:
        return geometryPlugin.getName()
    elif type(diffractometerScannableName) is str:
        return diffractometerScannableName
    else:
        raise TypeError(
            "If set, diffractometerScannableName must be a string. Leave as "
            "None to default to the geometry plugin name.\n"
            " diffractometerScannableName was: %r" %
            diffractometerScannableName)


def createDiffractometerScannableAndPossiblyDummies(
    dummyAxisNames, axesScannableList, axesGroupScannable,
    diffractometerScannableName):
    objects = {}

    def createDummyMotorScannables(nameList):
        result = []
        for name in nameList:
            result.append(DummyPD(name))
            print "Created DummyPD: %s" % name
        return result

    options = [dummyAxisNames, axesScannableList, axesGroupScannable]
    if sum([arg is not None for arg in options]) != 1:
        raise ValueError(
            "Specify only one of dummyAxisNames, inputAxisScannables or "
            "inputAxesGroupScannable")
    if dummyAxisNames:
        axesScannableList = createDummyMotorScannables(dummyAxisNames)
        objects.update(dict(zip(dummyAxisNames, axesScannableList)))
    if axesScannableList:
        axesGroupScannable = ScannableGroup(
            diffractometerScannableName + '_group', axesScannableList)
    diffractometerScannable = DiffractometerScannableGroup(
            diffractometerScannableName, None, axesGroupScannable)
    print "Created diffractometer scannable:", diffractometerScannableName
    objects[diffractometerScannableName] = diffractometerScannable
    return objects, diffractometerScannable


def buildWavelengthAndPossiblyEnergyScannable(dummyEnergyName, energyScannable,
                                            energyScannableMultiplierToGetKeV):
    objects = {}

    def createEnergyScannable(name):
        scn = DummyPD(name)
        scn.asynchronousMoveTo(12.39842)
        print "Created dummy energy scannable: ", name
        print "Set dummy energy to 1 Angstrom"
        return scn

    options = [dummyEnergyName, energyScannable]
    if sum([arg is not None for arg in options]) != 1:
        raise ValueError(
            "Specify only one of dummyEnergyName or energyScannable")
    if dummyEnergyName:
        if not isinstance(dummyEnergyName, str):
            raise TypeError(
                "dummyEnergyName must be a string. dummyEnergyName was: %r" %
                dummyEnergyName)
        energyScannable = createEnergyScannable(dummyEnergyName)
        objects[dummyEnergyName] = energyScannable
    if not isObjectScannable(energyScannable):
        raise TypeError(
            "energyScannable must Scannable. energyScannable was: %r" %
            energyScannable)

    # create wavelength scannable
    objects['wl'] = Wavelength('wl', energyScannable,
                               energyScannableMultiplierToGetKeV)
    print "Created wavelength scannable: wl"
    return objects, energyScannable


def checkHardwarePluginClass(hardwarePluginClass):
    try:
        if not issubclass(hardwarePluginClass, HardwareMonitorPlugin):
            raise ValueError(
                "hardwarePluginClass must be a HardwareMonitorPlugin, not a %r"
                % type(hardwarePluginClass))
    except TypeError:
        raise TypeError("hardwarePluginClass must be class not an instance")


def buildHklScannableAndComponents(hklScannableName, diffractometerScannable,
                                   diffcalc, hklVirtualAnglesToReport):
    objects = {}
    if type(hklScannableName) is not str:
        raise TypeError(
            "hklScannableName must be a string. hklScannableName was: %r" %
            hklScannableName)
    hkl = Hkl(hklScannableName, diffractometerScannable, diffcalc,
              hklVirtualAnglesToReport)
    objects[hklScannableName] = hkl
    objects['h'] = hkl.h
    objects['k'] = hkl.k
    objects['l'] = hkl.l
    if len(hklVirtualAnglesToReport) == 0:
        print "Created hkl scannable:", hklScannableName
    else:
        print ("Created hkl scannable: %s. Reports the virtual angles: %s" %
               (hklScannableName, ', '.join(hklVirtualAnglesToReport)))
    print "Created hkl component scannables: h, k & l"
    return objects


def buildHklverboseScannable(hklverboseScannableName, diffractometerScannable,
                             diffcalc, hklverboseVirtualAnglesToReport):
    objects = {}
    if hklverboseScannableName:
        if type(hklverboseScannableName) is not str:
            raise TypeError(
                "hklverboseScannableName must be a string, or None. "
                "hklverboseScannableName was: %r" % hklverboseScannableName)
        objects[hklverboseScannableName] = Hkl(
            hklverboseScannableName, diffractometerScannable, diffcalc,
            hklverboseVirtualAnglesToReport)
        if len(hklverboseVirtualAnglesToReport) == 0:
            print "Created verbose hkl scannable:", hklverboseScannableName
        else:
            virtual_to_report = ', '.join(hklverboseVirtualAnglesToReport)
            print ("Created verbose hkl scannable: %s. Reports the virtual "
                   "angles: %s" % (hklverboseScannableName, virtual_to_report))
    return objects


def createParameterScannables(diffcalc):
    objects = {}
    paramNames = diffcalc.parameter_manager.getParameterDict().keys()
    axisNames = diffcalc._hardware.getPhysicalAngleNames()
    for param in paramNames:
        scnname = param
        if param in axisNames:
            scnname += '_par'
        objects[scnname] = DiffractionCalculatorParameter(scnname, param,
                                                          diffcalc)
        print "Created parameter scannable:", scnname
    return objects


def expose_and_alias_commands(command_list):
    command_dict = {}

    for obj in command_list:
        if isinstance(obj, basestring):
            print obj + ':'
            continue
        if isinstance(obj, ExternalCommand):
            continue
        cmd = obj
        if cmd.__name__ in command_dict:
            raise Exception("Duplicate command: " + cmd.__name__)
        command_dict[cmd.__name__] = cmd
        _try_to_alias(cmd.__name__)

    return command_dict


def _try_to_alias(command_name):
    try:
        alias(command_name)
    except NameError:
        pass
    print "   ", command_name


def createAndAliasDiffcalcdemoCommand(demoCommands):
    objects = {}
    objects['diffcalcdemo'] = DiffcalcDemo(demoCommands)
    _try_to_alias('diffcalcdemo')
    print "=" * 80
    print "Try the following:"
    for line in demoCommands:
        print line
    print
    print ("Or type 'diffcalcdemo' to run this script "
           "(Caution, will move the diffractometer!)")
    return objects
