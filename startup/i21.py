from startup._common_imports import *  # @UnusedWildImport
from diffcalc.gdasupport.minigda.scannable import ScannableMotionWithScannableFieldsBase  # @UnusedImport
from startup.beamlinespecific.i21 import I21SampleStage, I21DiffractometerStage, I21TPLab
from diffcalc.hkl.you.geometry import YouGeometry, YouPosition
from diffcalc.hkl.you.constraints import NUNAME

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

if not GDA:    
    import startup._demo
else:
#     import __main__  # @UnresolvedImport
    from __main__ import x,y,z,th,chi,phi,delta,m5tth, energy, simx,simy,simz,simth,simchi,simphi,simdelta,simm5tth # @UnresolvedImport

LOCAL_MANUAL = "http://confluence.diamond.ac.uk/x/UoIQAw"
# Diffcalc i21
# ======== === 
# delta    delta or m5tth
# eta      th
# chi      90deg-chi
# phi      phi

SIM_MODE=False

class FourCircleI21(YouGeometry):
    """For a diffractometer with angles:
          delta, eta, chi, phi
    """
    def __init__(self, beamline_axes_transform=None):
        YouGeometry.__init__(self, 'fourc', {'mu': 0, NUNAME: 0}, beamline_axes_transform)

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        delta_phys, eta_phys, chi_phys, phi_phys = physical_angle_tuple
        return YouPosition(0, delta_phys, 0, eta_phys, 90 - chi_phys, phi_phys, 'DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        _, delta_phys, _, eta_phys, chi_phys, phi_phys = clone_position.totuple()
        return delta_phys, eta_phys, 90 - chi_phys, phi_phys


### Create dummy scannables ###
if GDA:  
    xyz_eta = ScannableGroup('xyz_eta', [x, y, z])  # @UndefinedVariable
else:   
    delta = Dummy('delta')
    m5tth = Dummy('m5tth')
    th = Dummy('th')
    chi = Dummy('chi')
    phi = Dummy('phi')
    x = Dummy('x')
    y = Dummy('y')
    z = Dummy('z')
    xyz_eta = ScannableGroup('xyz_eta', [x, y, z])

#support i21 non-concentric rotation motions
sa = I21SampleStage('sa', th, chi, phi, xyz_eta)
#th = sa.th
#chi = sa.chi
#phi = sa.phi

tp_phi = sa.tp_phi_scannable

tp_lab = I21TPLab('tp_lab', sa)
tp_labx = tp_lab.tp_labx
tp_laby = tp_lab.tp_laby
tp_labz = tp_lab.tp_labz

### Wrap i21 names to get diffcalc names - sample chamber
_fourc = I21DiffractometerStage('_fourc', delta, sa)
delta = _fourc.delta
eta = _fourc.eta
chi = _fourc.chi
phi = _fourc.phi

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
beamline_axes_transform = matrix('0 0 1; 0 1 0; 1 0 0')
settings.geometry = FourCircleI21(beamline_axes_transform=beamline_axes_transform)  # @UndefinedVariable
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
from diffcalc.ub.ub import lastub
lastub()
 
### Set i21 specific limits
print "INFO: diffcalc limits set in $diffcalc/startup/i21.py taken from http://confluence.diamond.ac.uk/pages/viewpage.action?pageId=51413586"
def setLimitsAndCuts(delta,chi,eta,phi):
    ''' set motor limits for diffcalc, these are within the actual motor limits
    '''
    setmin(delta, 0.0)
    setmax(delta, 180.0) #default to diode delta limits
    setmin(chi, -41.0)
    setmax(chi, 36.0)
    setmin(eta, 0.0)
    setmax(eta, 150.0)
    setmin(phi, -100.0)
    setmax(phi, 100.0)
    #http://jira.diamond.ac.uk/browse/I21-361
    setcut(eta, 0.0)
    setcut(phi, -180.0)
    print "Current hardware limits set to:"
    hardware()

setLimitsAndCuts()

### Create i21 bespoke secondary hkl devices
# Warning: this breaks the encapsulation provided by the diffcalc.dc.you public
#          interface, and may be prone to breakage in future.

print 'Creating i21 bespoke scannables:'

from diffcalc.dc import dcyou as _dc
from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl

print '- fourc_vessel & hkl_vessel'
_fourc_vessel = I21DiffractometerStage('_fourc_vessel', m5tth, sa)
fourc_vessel = DiffractometerScannableGroup('fourc_vessel', _dc, _fourc_vessel)
fourc_vessel.hint_generator = _fourc_vessel.get_hints
hkl_vessel = Hkl('hkl_vessel', _fourc_vessel, _dc)
h_vessel, k_vessel, l_vessel = hkl_vessel.h, hkl_vessel.k, hkl_vessel.l

print '- fourc_lowq & hkl_lowq'
LOWQ_OFFSET_ADDED_TO_DELTA_WHEN_READING = -8
_fourc_lowq = I21DiffractometerStage('_fourc_lowq', m5tth, sa,delta_offset=LOWQ_OFFSET_ADDED_TO_DELTA_WHEN_READING)
fourc_lowq = DiffractometerScannableGroup('fourc_lowq', _dc, _fourc_lowq)
fourc_lowq.hint_generator = _fourc_lowq.get_hints
hkl_lowq = Hkl('hkl_lowq', _fourc_lowq, _dc)
h_lowq, k_lowq, l_lowq = hkl_lowq.h, hkl_lowq.k, hkl_lowq.l

print '- fourc_highq & hkl_highq'
highq_OFFSET_ADDED_TO_DELTA_WHEN_READING = 0
_fourc_highq = I21DiffractometerStage('_fourc_highq', m5tth, sa,delta_offset=highq_OFFSET_ADDED_TO_DELTA_WHEN_READING)
fourc_highq = DiffractometerScannableGroup('fourc_highq', _dc, _fourc_highq)
fourc_highq.hint_generator = _fourc_highq.get_hints
hkl_highq = Hkl('hkl_highq', _fourc_highq, _dc)
h_highq, k_highq, l_highq = hkl_highq.h, hkl_highq.k, hkl_highq.l

# sample chamber
print '- fourc_diode & hkl_diode'
_fourc_diode = I21DiffractometerStage('_fourc_diode', delta, sa)
fourc_diode = DiffractometerScannableGroup('fourc_diode', _dc, _fourc_diode)
fourc_diode.hint_generator = _fourc_diode.get_hints
hkl_diode = Hkl('hkl_diode', _fourc_diode, _dc)
h_diode, k_diode, l_diode = hkl_diode.h, hkl_diode.k, hkl_diode.l

def centresample():
    sa.centresample()

def zerosample():
    '''zero on the currently centred sample location
    '''
    sa.zerosample()
    
def toolpoint_on():
    '''Switch on tool point
    '''
    sa.centre_toolpoint = True

def toolpoint_off():
    '''Switch off tool point
    '''
    sa.centre_toolpoint = False
    
def usediode():
    '''Use photo diode in sample chamber
    '''
    if SIM_MODE:
        _fourc.delta_scn=simdelta
        setmin(simdelta, 0)
        setmax(simdelta, 180)
        
    else:
        _fourc.delta_scn = delta
        setmin(delta, 0)
        setmax(delta, 180)
    
def usevessel():
    '''Use spectrometer
    '''
    if SIM_MODE:
        _fourc.delta_scn=simm5tth
        setmin(simm5tth, 0)
        setmax(simm5tth, 150)
    else:
        _fourc.delta_scn = m5tth  # note, if changed also update in _fourc_vessel constructor!
        setmin(m5tth, 0)
        setmax(m5tth, 150)
    
print "Created i21 bespoke commands: usediode, usevessel, centresample, zerosample, toolpoint_on, toolpoint_off"

if GDA:
    def swithMotors(sax, say, saz, sath, sachi, saphi, diodedelta, specm5tth):
        import __main__
        __main__.xyz_eta = ScannableGroup('xyz_eta', [sax, say, saz])  # @UndefinedVariable
        #update support for i21 non-concentric rotation motions
        __main__.sa = I21SampleStage('sa', sath, sachi, saphi,__main__.xyz_eta)  # @UndefinedVariable
        
        __main__.tp_phi = sa.tp_phi_scannable
        
        __main__.tp_lab = I21TPLab('tp_lab', __main__.sa)  # @UndefinedVariable
        __main__.tp_labx = __main__.tp_lab.tp_labx  # @UndefinedVariable
        __main__.tp_laby = __main__.tp_lab.tp_laby  # @UndefinedVariable
        __main__.tp_labz = __main__.tp_lab.tp_labz  # @UndefinedVariable
        
        ### update Wrap i21 names to get diffcalc names
        _fourc = I21DiffractometerStage('_fourc', diodedelta, __main__.sa)  # @UndefinedVariable
        __main__.delta = _fourc.delta
        __main__.eta = _fourc.eta
        __main__.chi = _fourc.chi
        __main__.phi = _fourc.phi
            #update diffcalc objects
        __main__.settings.hardware = ScannableHardwareAdapter(_fourc, __main__.en, ESMTGKeV)  # @UndefinedVariable
        __main__.settings.geometry = FourCircleI21(beamline_axes_transform=beamline_axes_transform)  # @UndefinedVariable
        __main__.settings.energy_scannable = __main__.en  # @UndefinedVariable
        __main__.settings.axes_scannable_group= _fourc
        __main__.settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV
        
        __main__.fourc=DiffractometerScannableGroup('fourc', _dc, _fourc)
        __main__.fourc.hint_generator = _fourc.get_hints  # (the callabl emethod) # @UndefinedVariable
        __main__.hkl = Hkl('hkl', _fourc, _dc)
        __main__.h, __main__.k, __main__.l = hkl.h, hkl.k, hkl.l

        from diffcalc.gdasupport.you import _virtual_angles
        from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter
        from diffcalc.gdasupport.scannable.wavelength import Wavelength
        __main__.hklverbose = Hkl('hklverbose', _fourc, _dc, _virtual_angles)
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', _fourc, __main__.settings.geometry,__main__.wl)  # @UndefinedVariable
        #update scannales: fourc_vessel & hkl_vessel'
        _fourc_vessel = I21DiffractometerStage('_fourc_vessel', specm5tth, __main__.sa)  # @UndefinedVariable
        __main__.fourc_vessel = DiffractometerScannableGroup('fourc_vessel', _dc, _fourc_vessel)
        __main__.fourc_vessel.hint_generator = _fourc_vessel.get_hints
        __main__.hkl_vessel = Hkl('hkl_vessel', _fourc_vessel, _dc)
        __main__.h_vessel, __main__.k_vessel, __main__.l_vessel = hkl_vessel.h, hkl_vessel.k, hkl_vessel.l
        
        #Update scannables: fourc_lowq & hkl_lowq'
        _fourc_lowq = I21DiffractometerStage('_fourc_lowq', specm5tth, __main__.sa,delta_offset=LOWQ_OFFSET_ADDED_TO_DELTA_WHEN_READING)  # @UndefinedVariable
        __main__.fourc_lowq = DiffractometerScannableGroup('fourc_lowq', _dc, _fourc_lowq)
        __main__.fourc_lowq.hint_generator = _fourc_lowq.get_hints
        __main__.hkl_lowq = Hkl('hkl_lowq', _fourc_lowq, _dc)
        __main__.h_lowq, __main__.k_lowq, __main__.l_lowq = hkl_lowq.h, hkl_lowq.k, hkl_lowq.l
        
        #Update scannables: fourc_highq & hkl_highq'
        _fourc_highq = I21DiffractometerStage('_fourc_highq', specm5tth, __main__.sa,delta_offset=highq_OFFSET_ADDED_TO_DELTA_WHEN_READING)  # @UndefinedVariable
        __main__.fourc_highq = DiffractometerScannableGroup('fourc_highq', _dc, _fourc_highq)
        __main__.fourc_highq.hint_generator = _fourc_highq.get_hints
        __main__.hkl_highq = Hkl('hkl_highq', _fourc_highq, _dc)
        __main__.h_highq, __main__.k_highq, __main__.l_highq = hkl_highq.h, hkl_highq.k, hkl_highq.l
        
        #Update scannables: fourc_diode & hkl_diode'
        _fourc_diode = I21DiffractometerStage('_fourc_diode', diodedelta, __main__.sa)  # @UndefinedVariable
        __main__.fourc_diode = DiffractometerScannableGroup('fourc_diode', _dc, _fourc_diode)
        __main__.fourc_diode.hint_generator = _fourc_diode.get_hints
        __main__.hkl_diode = Hkl('hkl_diode', _fourc_diode, _dc)
        __main__.h_diode, __main__.k_diode, __main__.l_diode = hkl_diode.h, hkl_diode.k, hkl_diode.l
        
    def stopMotors(sax, say, saz, sath, sachi, saphi, diodedelta, specm5tth):
        sax.stop()
        say.stop()
        saz.stop()
        sath.stop()
        sachi.stop()
        saphi.stop()
        diodedelta.stop()
        specm5tth.stop()
        
    def simdc():
        ''' switch to use dummy motors in diffcalc
        '''
        print "Stop real motors"
        stopMotors(x, y, z, th, chi, phi, delta, m5tth)
        
        global SIM_MODE
        SIM_MODE=True
        import __main__
        __main__.en=Dummy("en")
        print "Set energy to 12398.425 eV in simulation mode!"
        __main__.en(12398.425) #1 Angstrom wavelength @UndefinedVariable
        print "Switch to simulation motors"
        swithMotors(simx,simy,simz,simth,simchi,simphi,simdelta,simm5tth)
#         __main__.th = __main__.sa.simth  # @UndefinedVariable
#         __main__.chi = __main__.sa.simchi  # @UndefinedVariable
#         __main__.phi = __main__.sa.simphi  # @UndefinedVariable
        setLimitsAndCuts(simdelta,simchi,simth,simphi)
        
    def realdc():
        ''' switch to use real motors in diffcalc
        '''
        print "Stop simulation motors"
        stopMotors(simx,simy,simz,simth,simchi,simphi,simdelta,simm5tth)
        
        global SIM_MODE
        SIM_MODE=False
        import __main__
        print "Set energy to current beamline energy in real mode!"
        __main__.en=energy
        print "Switch to real motors"
        swithMotors(x,y,z,th,chi,phi,delta,m5tth)
#         __main__.th = __main__.sa.th  # @UndefinedVariable
#         __main__.chi = __main__.sa.chi  # @UndefinedVariable
#         __main__.phi = __main__.sa.phi  # @UndefinedVariable
        setLimitsAndCuts(delta,chi,th,phi)
     
    from gda.jython.commands.GeneralCommands import alias  # @UnresolvedImport
    alias("usediode")
    alias("usevessel")
    alias("centresample")
    alias("zerosample")
    alias("toolpoint_on")
    alias("toolpoint_off")
    print "Created i21 bespoke commands: simdc, realdc"
    alias("simdc")
    alias("realdc")
else:
    from IPython.core.magic import register_line_magic  # @UnresolvedImport
    from diffcmd.ipython import parse_line
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
        register_line_magic(parse_line(toolpoint_on, globals()))
        del toolpoint_on
        register_line_magic(parse_line(toolpoint_off, globals()))
        del toolpoint_off
### Demo ###

if not GDA:
    class I21Demo(startup._demo.Demo):
        
        def __init__(self, namespace):
            startup._demo.Demo.__init__(self, namespace, 'fourc')
        
        def i21(self):
            startup._demo.print_heading('i21 scannables demo')
    
            self.echorun_magiccmd_list([
                'sa',
                'pos th 1',
                'pos chi 2',
                'pos phi 3',
                'pos m5tth 4',
                'usevessel',
                'fourc'])

if not GDA:
    demo = I21Demo(globals())
