from startup._common_imports import *  # @UnusedWildImport
from diffcalc.gdasupport.minigda.scannable import ScannableMotionWithScannableFieldsBase  # @UnusedImport
from startup.beamlinespecific.i21 import I21SampleStage, I21DiffractometerStage, I21TPLab
if not GDA:    
    import startup._demo
else:
#     import __main__  # @UnresolvedImport
    from __main__ import diodetth,m5tth,sapolar,satilt,saazimuth,sax,say,saz, energy  # @UnresolvedImport
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
    print "WARNING: saz may need to be reversed to agree with diffcalc"
    xyz_eta = ScannableGroup('xyz_eta', [sax, say, saz])  # @UndefinedVariable
else:   
    diodetth = Dummy('diodetth')
    m5tth = Dummy('m5tth')
    sapolar = Dummy('sapolar')
    satilt = Dummy('satilt')
    saazimuth = Dummy('saazimuth')
    sax = Dummy('sax')
    say = Dummy('say')
    saz = Dummy('saz')
    xyz_eta = ScannableGroup('xyz_eta', [sax, say, saz])
    
    

sa = I21SampleStage('sa', sapolar, satilt, saazimuth, xyz_eta)
sapolar = sa.sapolar
satilt = sa.satilt
saazimuth = sa.saazimuth

tp_phi = sa.tp_phi_scannable

def centresample():
    sa.centresample()

def zerosample():
    sa.zerosample()

tp_lab = I21TPLab('tp_lab', sa)
tp_labx = tp_lab.tp_labx
tp_laby = tp_lab.tp_laby
tp_labz = tp_lab.tp_labz

_fourc = I21DiffractometerStage('_fourc', diodetth, sa, chi_offset = 90)
delta = _fourc.delta
eta = _fourc.eta
chi = _fourc.chi
phi = _fourc.phi


### Wrap i21 names to get diffcalc names
if GDA:
   
    def usediode():
        _fourc.delta_scn = diodetth
    
    def usevessel():
        _fourc.delta_scn = m5tth  # note, if changed also update in _fourc_vessel constructor!
 
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
    alias("centresample")
    alias("zerosample")

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
        register_line_magic(parse_line(centresample, globals()))
        del centresample
        register_line_magic(parse_line(zerosample, globals()))
        del zerosample

        
print "Created i21 bespoke commands: usediode & usevessel"

if GDA:
    en=energy
    if float(en.getPosition()) == 0: # no energy value - dummy?
        en(800)
else:
    en = Dummy('en')
    en(800)
    
en.level = 3
 
 
### Configure and import diffcalc objects ###
ESMTGKeV = 0.001
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
 
### Load the last ub calculation used
lastub() 

### Set i21 specifi limits
print "Warning: diffcalc limits set in $diffcalc/startup/i21.py are unrealistic"
setmin(delta, 0)
setmin(chi, 0)

### Create i21 bespoke secondary hkl devices
# Warning: this breaks the encapsulation provided by the diffcalc.dc.you public
#          interface, and may be prone to breakage in future.

print 'Creating i21 bespoke scannables:'

from diffcalc.dc import dcyou as _dc
from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl

print '- fourc_vessel & hkl_vessel'
_fourc_vessel = I21DiffractometerStage('_fourc_vessel', m5tth, sa, chi_offset = 90)
fourc_vessel = DiffractometerScannableGroup('fourc_vessel', _dc, _fourc_vessel)
fourc_vessel.hint_generator = _fourc_vessel.get_hints
hkl_vessel = Hkl('hkl_vessel', _fourc_vessel, _dc)
h_vessel, k_vessel, l_vessel = hkl_vessel.h, hkl_vessel.k, hkl_vessel.l

print '- fourc_lowq & hkl_lowq'
LOWQ_OFFSET_ADDED_TO_DELTA_WHEN_READING = -8
_fourc_lowq = I21DiffractometerStage(
    '_fourc_lowq', m5tth, sa, chi_offset=90,
    delta_offset=LOWQ_OFFSET_ADDED_TO_DELTA_WHEN_READING)
fourc_lowq = DiffractometerScannableGroup('fourc_lowq', _dc, _fourc_lowq)
fourc_lowq.hint_generator = _fourc_lowq.get_hints
hkl_lowq = Hkl('hkl_lowq', _fourc_lowq, _dc)
h_lowq, k_lowq, l_lowq = hkl_lowq.h, hkl_lowq.k, hkl_lowq.l

print '- fourc_highq & hkl_highq'
highq_OFFSET_ADDED_TO_DELTA_WHEN_READING = 0
_fourc_highq = I21DiffractometerStage(
    '_fourc_highq', m5tth, sa, chi_offset=90,
    delta_offset=highq_OFFSET_ADDED_TO_DELTA_WHEN_READING)
fourc_highq = DiffractometerScannableGroup('fourc_highq', _dc, _fourc_highq)
fourc_highq.hint_generator = _fourc_highq.get_hints
hkl_highq = Hkl('hkl_highq', _fourc_highq, _dc)
h_highq, k_highq, l_highq = hkl_highq.h, hkl_highq.k, hkl_highq.l

# vessel
print '- fourc_diode & hkl_diode'
_fourc_diode = I21DiffractometerStage('_fourc_diode', diodetth, sa, chi_offset = 90)
fourc_diode = DiffractometerScannableGroup('fourc_diode', _dc, _fourc_diode)
fourc_diode.hint_generator = _fourc_diode.get_hints
hkl_diode = Hkl('hkl_diode', _fourc_diode, _dc)
h_diode, k_diode, l_diode = hkl_diode.h, hkl_diode.k, hkl_diode.l

### Demo ###

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
