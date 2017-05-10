from startup._common_imports import *
from diffcalc.gdasupport.minigda.scannable import ScannableMotionWithScannableFieldsBase
from startup.beamlinespecific.i21 import I21SampleStage, I21DiffractometerStage,\
    I21TPLab
import startup._demo
LOCAL_MANUAL = "http://confluence.diamond.ac.uk/x/UoIQAw"
# Diffcalc i21
# ======== === 
# delta    diode_tth or vessel_tth
# eta      sapolar
# chi      satilt + 90deg
# phi      saazimuth



### Create dummy scannables ###
if GDA:    
    assert 'diode_tth' in locals()
    assert 'vessel_tth' in locals()
    assert '_sapol' in locals()
    assert '_satilt' in locals()
    assert '_saaz' in locals()
    assert 'xyx_eta' in locals()
else:   
    diode_tth = Dummy('diode_tth')
    vessel_tth = Dummy('vessel_tth')
    _sapol = Dummy('_sapol')
    _satilt = Dummy('_satilt')
    _saaz = Dummy('_saaz')
    x_eta = Dummy('x_eta')
    y_eta = Dummy('y_eta')
    z_eta = Dummy('z_eta')
    xyz_eta = ScannableGroup('xyz_eta', [x_eta, y_eta, z_eta])
    
    

sa = I21SampleStage('sa', _sapol, _satilt, _saaz, xyz_eta)
sapol = sa.sapol
satilt = sa.satilt
saaz = sa.saaz
tpphi = sa.tp_phi_scannable

def zerosample():
    raise Exception('not implemented yet!')

tplab = I21TPLab('tplab', sa)
tplabx = tplab.tplabx
tplaby = tplab.tplaby
tplabz = tplab.tplabz

_fourc = I21DiffractometerStage('_fourc', diode_tth, sa, chi_offset = 90)
delta = _fourc.delta
eta = _fourc.eta
chi = _fourc.chi
phi = _fourc.phi


### Wrap i21 names to get diffcalc names
if GDA:
    raise Exception('need gda class for wrapping scannables. There is one somewhere')
#     import what_is_its_name as XYZ  # @UnresolvedImport
#     delta = XYZ(diode_tth, 'delta')  # or vessel_tth
#     eta = XYZ(sapolar, 'eta')
#     chi = XYZ(satilt, 'chi', 90)  # chi = satilt + 90deg
#     phi = XYZ(saazimuth, 'phi')
#     
#     def usediode():
#         raise Exception('needs implementing')
#    
#     def usevessel():
#         raise Exception('needs implementing')
#     from gda.jython.commands.GeneralCommands import alias
#     alias(usediode)
#     alis(usevessel)

else:
    from diffcalc.gdasupport.minigda.scannable import ScannableAdapter
    from IPython.core.magic import register_line_magic
    from diffcmd.ipython import parse_line
#     delta = ScannableAdapter(diode_tth, 'delta')  # or vessel_tth
#     eta = ScannableAdapter(sapol, 'eta')
#     chi = ScannableAdapter(satilt, 'chi', 90)  # chi = satilt + 90deg
#     phi = ScannableAdapter(saaz, 'phi')
    
    def usediode():
        _fourc.delta_scn = diode_tth
    
    def usevessel():
        _fourc.delta_scn = vessel_tth
        
    if IPYTHON:
        from IPython import get_ipython
        register_line_magic(parse_line(usediode, globals()))
        del usediode
        register_line_magic(parse_line(usevessel, globals()))
        del usevessel
        
print "Created i21 bespoke commands: usediode & usevessel"
 
en = Dummy('en')
en.level = 3
 
 
### Configure and import diffcalc objects ###
ESMTGKeV = 1
settings.hardware = ScannableHardwareAdapter(_fourc, en, ESMTGKeV)
settings.geometry = diffcalc.hkl.you.geometry.FourCircle()  # @UndefinedVariable
settings.energy_scannable = en
settings.axes_scannable_group= _fourc
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV
 
from diffcalc.gdasupport.you import *  # @UnusedWildImport
 



# fourc is created in diffcalc.gdasupport.you. Add some I21 hints into it
fourc.hint_generator = _fourc.get_hints  # (the callablemethod) # @UndefinedVariable

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
 
# Load the last ub calculation used
lastub() 

class I21Demo(startup._demo.Demo):
    
    def __init__(self, namespace):
        startup._demo.Demo.__init__(self, namespace, 'fourc')
    
    def i21(self):
        startup._demo.print_heading('i21 scannables demo')

        self.echorun_magiccmd_list([
            'sa',
            'pos sapol 1',
            'pos satilt 2',
            'pos saaz 3',
            'pos vessel_tth 4',
            'usevessel',
            'fourc'])

if not GDA:
    demo = I21Demo(globals())
