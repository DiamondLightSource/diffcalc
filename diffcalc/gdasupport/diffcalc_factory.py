import time

from diffcalc.diffcalc_ import create_diffcalc, AVAILABLE_ENGINES
from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc.gdasupport.scannable.parameter import \
    DiffractionCalculatorParameter
from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter
from diffcalc.gdasupport.scannable.wavelength import Wavelength
import diffcalc.hkl.vlieg.geometry
from diffcalc.hardware import ScannableHardwareAdapter
from diffcalc.util import format_command_help, ExternalCommand
from diffcalc.hkl.vlieg.geometry import VliegGeometry
from diffcalc.hkl.you.geometry import YouGeometry
from diffcalc.ub.persistence import UBCalculationPersister

try:
    from gda.device.scannable.scannablegroup import ScannableGroup
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import ScannableGroup

try:
    from gdascripts.pd.dummy_pds import DummyPD
    from gda.device.scannable import ScannableBase
    from gda.device.scannable import PseudoDevice
    from gda.jython.commands.GeneralCommands import alias
    from gda.jython import JythonServerFacade
except ImportError:
    print "WARNING: ExampleSixCircleStartup.py is not running within the GDA:"
    print "         falling back to the (very minimal!) minigda..."

    from diffcalc.gdasupport.minigda.scannable import DummyPD
    from diffcalc.gdasupport.minigda.scannable import \
        Scannable as ScannableBase
    from diffcalc.gdasupport.minigda.scannable import \
        Scannable as PseudoDevice
    # from diffcalc.gdasupport.minigda.terminal import alias
    # Note: minigda will provide an alias method in the rootnamespace


def _is_scannable(obj):
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


VLIEG_GEOMETRIES = {
    'fourc': diffcalc.hkl.vlieg.geometry.Fourc,
    'fivec': diffcalc.hkl.vlieg.geometry.Fivec,
    'sixc': diffcalc.hkl.vlieg.geometry.SixCircleGeometry,
    'sixc_gamma_on_arm':
        diffcalc.hkl.vlieg.geometry.SixCircleGammaOnArmGeometry
}

YOU_GEOMETRIES = {
    'sixc': diffcalc.hkl.vlieg.geometry.SixCircleGeometry,
}


def add_objects_to_namespace(object_dict, namespace):
    for nameToAdd in object_dict.keys():
        if nameToAdd in namespace:
            raise Exception(
                "Did not add diffcalc objects/method to namespace, as doing "
                "so would overwrite the object %s" % nameToAdd)
    namespace.update(object_dict)
    print "Added objects/methods to namespace: ", ', '.join(object_dict.keys())


def create_objects(
    dummy_axis_names=None,               # list of strings
    axis_scannable_list=None,            # list of single axis scannables
    axes_group_scannable=None,           # single scannable group
    dummy_energy_name=None,
    energy_scannable=None,
    energy_scannable_multiplier_to_get_KeV=1,
    geometry=None,                       # instance or name
    hkl_name='hkl',
    hkl_virtual_angles_to_report=(),
    hklverbose_name='hklverbose',
    hklverbose_virtual_angles_to_report=('2theta', 'Bin', 'Bout', 'azimuth'),
    diffractometer_scannable_name=None,   # e.g. SixCircleGammaOnArmGeometry.
                                          # or determined by geometry
    demo_commands=[],
    simulated_crystal_counter_name=None,
    engine_name='vlieg',
    raise_exceptions_for_all_errors=True):

    print "=" * 80
    objects = {}

    # Obtain geometry instance
    geometry = _determine_vlieg_geometry(geometry)

    # Create diffractometer scannable and possibly dummy axes
    diffractometer_scannable_name = _determine_diffractometer_scannable_name(
        diffractometer_scannable_name, geometry)

    objects.update(_create_diff_and_dummies(dummy_axis_names,
                                        axis_scannable_list,
                                        axes_group_scannable,
                                        diffractometer_scannable_name))
    diff_scannable = objects[diffractometer_scannable_name]

    # Create dummy energy (if needed) and wavelength scannable
    objects_, energy_scannable = _create_wavelength_and_energy(
        dummy_energy_name, energy_scannable,
        energy_scannable_multiplier_to_get_KeV)
    objects.update(objects_)

    # Create hardware adapter
    hardware = ScannableHardwareAdapter(diff_scannable, energy_scannable,
                                        energy_scannable_multiplier_to_get_KeV)

    # Instantiate diffcalc
    if engine_name.lower() not in AVAILABLE_ENGINES:
        raise KeyError("The engine '%s' was not recognised. "
                       "Try %r" % (engine_name, AVAILABLE_ENGINES))

    dc = create_diffcalc(engine_name.lower(),
                          geometry,
                          hardware,
                          raise_exceptions_for_all_errors,
                          UBCalculationPersister())

    objects['dc'] = dc
    diff_scannable.diffcalc = dc

    # Create hkl, h, k and l scannables
    objects.update(
        _create_hkl(hkl_name, diff_scannable, dc,
                    hkl_virtual_angles_to_report))

    # Create verbose hkl
    objects.update(
        _create_hkl_verbose(hklverbose_name, diff_scannable, dc,
                            hklverbose_virtual_angles_to_report))

    # Create parameter/constraint scannables
    objects.update(_create_constraint_scannables(dc))

    # Create simulated crystal counter
    if simulated_crystal_counter_name:
        ct = SimulatedCrystalCounter(simulated_crystal_counter_name,
                                     diff_scannable, geometry, objects['wl'])
        objects.update({ct.name: ct})
        print "\nCreated Simulated Crystal Counter:\n   ", ct.name

    # expose and alias ub and hkl commands from diffcalc object
    print "UB"
    print "=="
    objects.update(_expose_and_alias_commands(dc.ub.commands))
    print "hkl"
    print "==="
    objects.update(_expose_and_alias_commands(dc.hkl.commands))
    print "Tutorial"
    print ""
    objects.update(_create_and_alias_diffcalcdemo(demo_commands))

    if engine_name.lower() == 'vlieg':
        # add strings for transformX commands
        objects.update(
            {'on': 'on', 'off': 'off', 'auto': 'auto', 'manual': 'manual'})

    print "=" * 80

    objects['ub'].__func__.__doc__ = format_command_help(dc.ub.commands)
    Hkl.dynamic_docstring = format_command_help(dc.hkl.commands)
    return objects


def _determine_vlieg_geometry(geometry):
    if isinstance(geometry, VliegGeometry):
        return geometry
    elif type(geometry) is str:
        try:
            return VLIEG_GEOMETRIES[geometry]()
        except KeyError:
            raise KeyError(
                "If specifying geometry inputGeometryPlugin by name (rather "
                "than by passing an plugin instance),\n the name must be one "
                "of:\n  %s" % ', '.join(VLIEG_GEOMETRIES.keys()))
    else:
        raise TypeError(
                "inputGeometryPlugin must be an instance of a "
                "DiffractometerPlugin or a string from:\n  %s" %
                ', '.join(VLIEG_GEOMETRIES.keys()))


def _determine_you_geometry(geometry):
    if isinstance(geometry, YouGeometry):
        return geometry
    elif type(geometry) is str:
        try:
            return YOU_GEOMETRIES[geometry]()
        except KeyError:
            raise KeyError(
                "If specifying geometry inputGeometryPlugin by name (rather "
                "than by passing an plugin instance),\n the name must be one "
                "of:\n  %s" % ', '.join(YOU_GEOMETRIES.keys()))
    else:
        raise TypeError(
                "inputGeometryPlugin must be an instance of a "
                "DiffractometerPlugin or a string from:\n  %s" %
                ', '.join(YOU_GEOMETRIES.keys()))


def _determine_diffractometer_scannable_name(diffractometer_scannable_name,
                                             geometry):
    if diffractometer_scannable_name is None:
        return geometry.name
    elif type(diffractometer_scannable_name) is str:
        return diffractometer_scannable_name
    else:
        raise TypeError(
            "If set, diffractometer_scannable_name must be a string. Leave as "
            "None to default to the geometry plugin name.\n"
            " diffractometer_scannable_name was: %r" %
            diffractometer_scannable_name)


def _create_diff_and_dummies(dummy_axis_names,
                                       axes_scannable_list,
                                       axes_group_scannable,
                                       diffractometer_scannable_name):
    objects = {}

    def create_dummy_axes_scannables(nameList):
        result = []
        for name in nameList:
            result.append(DummyPD(name))
        print "\nCreated dummy axes:"
        print "   ", ', '.join(nameList[:-1]) + ' and ' + nameList[-1]
        return result

    options = [dummy_axis_names, axes_scannable_list, axes_group_scannable]
    if sum([arg is not None for arg in options]) != 1:
        raise ValueError(
            "Specify only one of dummy_axis_names, inputAxisScannables or "
            "inputAxesGroupScannable")
    if dummy_axis_names:
        axes_scannable_list = create_dummy_axes_scannables(dummy_axis_names)
        objects.update(dict(zip(dummy_axis_names, axes_scannable_list)))
    if axes_scannable_list:
        axes_group_scannable = ScannableGroup(
            diffractometer_scannable_name + '_group', axes_scannable_list)
    diff_scannable = DiffractometerScannableGroup(
            diffractometer_scannable_name, None, axes_group_scannable)
    print ("\nCreated diffractometer scannable:\n    " +
           diffractometer_scannable_name)
    objects[diffractometer_scannable_name] = diff_scannable
    return objects


def _create_wavelength_and_energy(dummy_energy_name,
                                  energy_scannable,
                                  energy_scannable_multiplier_to_KeV):
    objects = {}

    def create_energy_scannable(name):
        scn = DummyPD(name)
        scn.asynchronousMoveTo(12.39842)
        print "\nCreated dummy energy scannable:\n   ", name
        print "    (set dummy energy to 1 Angstrom)"
        return scn

    options = [dummy_energy_name, energy_scannable]
    if sum([arg is not None for arg in options]) != 1:
        raise ValueError(
            "Specify only one of dummy_energy_name or energy_scannable")
    if dummy_energy_name:
        if not isinstance(dummy_energy_name, str):
            raise TypeError(
                "dummy_energy_name must be a string; not: %r" %
                dummy_energy_name)
        energy_scannable = create_energy_scannable(dummy_energy_name)
        objects[dummy_energy_name] = energy_scannable
    if not _is_scannable(energy_scannable):
        raise TypeError(
            "energy_scannable must Scannable; not: %r" %
            energy_scannable)

    # create wavelength scannable
    objects['wl'] = Wavelength('wl', energy_scannable,
                               energy_scannable_multiplier_to_KeV)
    print "\nCreated wavelength scannable:\n    wl"
    return objects, energy_scannable


def _create_hkl(hklScannableName, diffractometerScannable,
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
        print "\nCreated hkl scannable:\n   ", hklScannableName
    else:
        print ("\nCreated hkl scannable:\n    %s\n    (reports the virtual angles: %s)" %
               (hklScannableName, ', '.join(hklVirtualAnglesToReport)))
    print "\nCreated hkl component scannables:\n    h, k & l"
    return objects


def _create_hkl_verbose(hklverboseScannableName, diffractometerScannable,
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
            print "\nCreated verbose hkl scannable:\n   ", hklverboseScannableName
        else:
            virtual_to_report = ', '.join(hklverboseVirtualAnglesToReport)
            print ("\nCreated verbose hkl scannable:\n    %s. Reports the virtual "
                   "angles: %s" % (hklverboseScannableName, virtual_to_report))
    return objects


def _create_constraint_scannables(diffcalc):
    objects = {}
    paramNames = diffcalc.parameter_manager.settable_constraint_names
    axisNames = diffcalc._hardware.getPhysicalAngleNames()
    created_names = []
    for param in paramNames:
        scnname = param
        if param in axisNames:
            scnname += '_par'
        objects[scnname] = DiffractionCalculatorParameter(scnname, param,
                                                          diffcalc)
        created_names.append(scnname)
    print "\nCreated parameter scannables:"
    print "   ", ', '.join(created_names[:-1]) + ' and ' + created_names[-1]
    return objects


def _expose_and_alias_commands(command_list):
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


def _create_and_alias_diffcalcdemo(demoCommands):
    objects = {}
    objects['diffcalcdemo'] = DiffcalcDemo(demoCommands)
    _try_to_alias('diffcalcdemo')
    print "=" * 80
    print "Try the following:"
    for line in demoCommands:
        print line
    print
    print ("Or type 'diffcalcdemo' to run this script. "
           "(Caution, will move the diffractometer!)")
    return objects
