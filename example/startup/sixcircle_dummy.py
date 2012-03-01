try:
    import diffcalc
except ImportError:
    from gda.data.PathConstructor import createFromProperty
    import sys
    gda_root = createFromProperty("gda.root")
    diffcalc_path = gda_root.split('/plugins')[0] + '/diffcalc'
    sys.path = [diffcalc_path] + sys.path
    print diffcalc_path + ' added to GDA Jython path.'
    import diffcalc  # @UnusedImport
from diffcalc.gdasupport.diffcalc_factory import \
    create_objects, add_objects_to_namespace

demoCommands = []
demoCommands.append("newub 'cubic'")
demoCommands.append("setlat 'cubic' 1 1 1 90 90 90")
demoCommands.append("pos wl 1")
demoCommands.append("pos sixc [0 90 0 45 45 0]")
demoCommands.append("addref 1 0 1")
demoCommands.append("pos phi 90")
demoCommands.append("addref 0 1 1")
demoCommands.append("checkub")
demoCommands.append("ub")
demoCommands.append("hklmode")


print "=" * 80
diffcalcObjects = create_objects(
    dummy_axis_names=('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'),
    dummy_energy_name='en',
    geometry='sixc',
    hklverbose_virtual_angles_to_report=('2theta', 'Bin', 'Bout', 'azimuth'),
    demo_commands=demoCommands
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(diffcalcObjects, globals())


print diffcalcObjects['ub'].__doc__
print "***"
print diffcalcObjects['hkl'].__doc__
print "***"
