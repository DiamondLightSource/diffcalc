from startup._common_imports import *  # @UnusedWildImport
from diffcalc.gdasupport.minigda.scannable import ScannableMotionWithScannableFieldsBase  # @UnusedImport
from startup.beamlinespecific.i21 import I21SampleStage, I21DiffractometerStage, I21TPLab
if not GDA:    
    import startup._demo
else:
#     import __main__  # @UnresolvedImport
    from __main__ import diodetth,m5tth,sapolar,satilt,saazimuth,sax,say,saz  # @UnresolvedImport
LOCAL_MANUAL = "http://confluence.diamond.ac.uk/x/UoIQAw"
# Diffcalc i21
# ======== === 
# delta    diodetth or m5tth
# eta      sapolar
# chi      satilt + 90deg
# phi      saazimuth



### Create dummy scannables ###
if GDA:  
#     assert 'diodetth' in __main__.__dict__  #GDA name is diodetth
#     assert 'm5tth' in __main__.__dict__ #GDA name is m5tth - m5 has 2 mirrors with fixed tth offset
#     assert 'sapolar' in __main__.__dict__     #GDA name is sapolar
#     assert 'satilt' in __main__.__dict__  #GDA name is satilt    - fix 90 deg offset
#     assert 'saazimuth' in __main__.__dict__      #GDA name is saazimuth
#     assert 'sax'in __main__.__dict__
#     assert 'say'in __main__.__dict__
#     assert 'saz'in __main__.__dict__
    xyz_eta = ScannableGroup('xyz_eta', [sax, say, saz])  # @UndefinedVariable
else:   
    diodetth = Dummy('diodetth')
    m5tth = Dummy('m5tth')
    sapolar = Dummy('sapolar')
    satilt = Dummy('satilt')
    saazimuth = Dummy('saazimuth')
    sax = Dummy('sax')
    say = Dummy('sax')
    saz = Dummy('sax')
    xyz_eta = ScannableGroup('xyz_eta', [sax, say, saz])
    
    

sa = I21SampleStage('sa', sapolar, satilt, saazimuth, xyz_eta)
sapol = sa.sapolar
satilt = sa.satilt
saaz = sa.saazimuth
tpphi = sa.tp_phi_scannable

def zerosample():
    raise Exception('not implemented yet!')

tplab = I21TPLab('tplab', sa)
tplabx = tplab.tplabx
tplaby = tplab.tplaby
tplabz = tplab.tplabz

_fourc = I21DiffractometerStage('_fourc', diodetth, sa, chi_offset = 90)
delta = _fourc.delta
eta = _fourc.eta
chi = _fourc.chi
phi = _fourc.phi


### Wrap i21 names to get diffcalc names
if GDA:
    from diffcalc.gdasupport.minigda.scannable import ScannableAdapter
    delta = ScannableAdapter(diodetth, 'delta')  # or vessel_tth
    eta = ScannableAdapter(sapolar, 'eta')
    chi = ScannableAdapter(satilt, 'chi', 90)  # chi = satilt + 90deg
    phi = ScannableAdapter(saazimuth, 'phi')
    
    def usediode():
        _fourc.delta_scn = diodetth
    
    def usevessel():
        _fourc.delta_scn = m5tth
 
#    raise Exception('need gda class for wrapping scannables. There is one somewhere')
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
    from gda.jython.commands.GeneralCommands import alias  # @UnresolvedImport
    alias("usediode")
    alias("usevessel")

else:
    from diffcalc.gdasupport.minigda.scannable import ScannableAdapter
    from IPython.core.magic import register_line_magic  # @UnresolvedImport
    from diffcmd.ipython import parse_line
#     delta = ScannableAdapter(diodetth, 'delta')  # or vessel_tth
#     eta = ScannableAdapter(sapolar, 'eta')
#     chi = ScannableAdapter(satilt, 'chi', 90)  # chi = satilt + 90deg
#     phi = ScannableAdapter(saazimuth, 'phi')
    
    def usediode():
        _fourc.delta_scn = diodetth
    
    def usevessel():
        _fourc.delta_scn = m5tth
        
    if IPYTHON:
        from IPython import get_ipython  # @UnresolvedImport @UnusedImport
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
if not GDA:
    class I21Demo(startup._demo.Demo):
        
        def __init__(self, namespace):
            startup._demo.Demo.__init__(self, namespace, 'fourc')
        
        def i21(self):
            startup._demo.print_heading('i21 scannables demo')
    
            self.echorun_magiccmd_list([
                'sa',
                'pos sapolar 1',
                'pos satilt 2',
                'pos saazimuth 3',
                'pos m5tth 4',
                'usevessel',
                'fourc'])

if not GDA:
    demo = I21Demo(globals())
