from startup._common_imports import *  # @UnusedWildImport
from diffcalc.gdasupport.minigda.scannable import ScannableMotionWithScannableFieldsBase  # @UnusedImport
from startup.beamlinespecific.i21 import FourCircleI21, I21SampleStage, I21TPLab
from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

if not GDA:    
    import startup._demo
else:
#     import __main__  # @UnresolvedImport
    from __main__ import x,y,z,th,chi,phi,difftth,m5tth, energy, simx,simy,simz,simth,simchi,simphi,simdelta,simm5tth # @UnresolvedImport

LOCAL_MANUAL = "http://confluence.diamond.ac.uk/x/UoIQAw"
# Diffcalc i21
# ======== === 
# delta    difftth or m5tth
# eta      th
# chi      chi
# phi      -phi

SIM_MODE=False

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
if GDA:
    en=energy
    if float(en.getPosition()) == 0: # no energy value - dummy?
        en(800)
    simenergy = Dummy('en')
    simenergy(800)
else:
    en = simenergy = Dummy('en')
    en(800)

en.level = 3
simenergy.level = 3

### Configure and import diffcalc objects ###
beamline_axes_transform = matrix('0 0 -1; 0 1 0; 1 0 0')
_lowq_geometry = FourCircleI21(beamline_axes_transform=beamline_axes_transform, delta_offset=-4.)
_highq_geometry = FourCircleI21(beamline_axes_transform=beamline_axes_transform, delta_offset=4.)
_tth_geometry = FourCircleI21(beamline_axes_transform=beamline_axes_transform)

if GDA:
    _sc_difftth = ScannableGroup('_fourc', (difftth, th, chi, phi))
    _sc_m5tth = ScannableGroup('_fourc', (m5tth, th, chi, phi))
    _sc_sim = ScannableGroup('_fourc', (simdelta, simth, simchi, simphi))
else:
    _sc_difftth = _sc_m5tth = _sc_sim = ScannableGroup('_fourc', (delta, th, chi, phi))

ESMTGKeV = 0.001
_hw_difftth = ScannableHardwareAdapter(_sc_difftth, en, ESMTGKeV)
_hw_m5tth = ScannableHardwareAdapter(_sc_m5tth, en, ESMTGKeV)
_hw_sim = ScannableHardwareAdapter(_sc_sim, simenergy, ESMTGKeV)

settings.hardware = _hw_difftth
settings.geometry = _tth_geometry
settings.energy_scannable = en
settings.axes_scannable_group = _sc_difftth
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV
 
from diffcalc.gdasupport.you import *  # @UnusedWildImport

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
 
### Load the last ub calculation used
from diffcalc.ub.ub import lastub
lastub()
 
### Set i21 specific limits
print "INFO: diffcalc limits set in $diffcalc/startup/i21.py taken from http://confluence.diamond.ac.uk/pages/viewpage.action?pageId=51413586"
def setLimitsAndCuts(delta_angle, eta_angle, chi_angle, phi_angle):
    ''' set motor limits for diffcalc, these are within the actual motor limits
    '''
    if not GDA:
        setmin(delta_angle, 0.0)
        setmax(delta_angle, 180.0) #default to diode delta limits
        setmin(chi_angle, -41.0)
        setmax(chi_angle, 36.0)
        setmin(eta_angle, 0.0)
        setmax(eta_angle, 150.0)
        setmin(phi_angle, -100.0)
        setmax(phi_angle, 100.0)
    #http://jira.diamond.ac.uk/browse/I21-361
    setcut(eta_angle, 0.0)
    setcut(phi_angle, -180.0)
    print "Current hardware limits set to:"
    hardware()
    
if GDA:
    setLimitsAndCuts(difftth, th, chi, phi)
else:
    setLimitsAndCuts(delta, th, chi, phi)


### Create i21 bespoke secondary hkl devices
# Warning: this breaks the encapsulation provided by the diffcalc.dc.you public
#          interface, and may be prone to breakage in future.

print 'Creating i21 bespoke scannables:'


hkl_m5tth = Hkl('hkl_m5tth', _sc_m5tth, DiffractometerYouCalculator(_hw_m5tth, _tth_geometry))
hkl_lowq = Hkl('hkl_lowq', _sc_m5tth, DiffractometerYouCalculator(_hw_m5tth, _lowq_geometry))
hkl_highq = Hkl('hkl_highq', _sc_m5tth, DiffractometerYouCalculator(_hw_m5tth, _highq_geometry))
hkl_difftth = Hkl('hkl_difftth', _sc_difftth, DiffractometerYouCalculator(_hw_difftth, _tth_geometry))
hkl_sim = Hkl('hkl_sim', _sc_sim, DiffractometerYouCalculator(_hw_sim, _tth_geometry))

def usem5tth():
    print '- setting hkl ---> hkl_m5tth'
    global settings
    settings.hardware = _hw_m5tth
    settings.geometry = _tth_geometry
    settings.axes_scannable_group = _sc_m5tth

    # Create diffractometer scannable
    _diff_scn_name = _tth_geometry.name
    from diffcalc.dc import dcyou as _dc
    _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_m5tth)

    setLimitsAndCuts(m5tth, th, chi, phi)
    import __main__
    __main__.hkl = hkl_m5tth
    __main__.h   = hkl_m5tth.h
    __main__.k   = hkl_m5tth.k
    __main__.l   = hkl_m5tth.l
    __main__.fourc = _diff_scn
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.fourc, _dc, _virtual_angles)
    if GDA:
        __main__.en = energy
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', __main__.fourc, settings.geometry, __main__.wl)  # @UndefinedVariable

def uselowq():
    print '- setting hkl ---> hkl_lowq'
    global settings
    settings.hardware = _hw_m5tth
    settings.geometry = _lowq_geometry
    settings.axes_scannable_group = _sc_m5tth

    # Create diffractometer scannable
    _diff_scn_name = _lowq_geometry.name
    from diffcalc.dc import dcyou as _dc
    _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_m5tth)

    setLimitsAndCuts(m5tth, th, chi, phi)
    import __main__
    __main__.hkl = hkl_lowq
    __main__.h   = hkl_lowq.h
    __main__.k   = hkl_lowq.k
    __main__.l   = hkl_lowq.l
    __main__.fourc = _diff_scn
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.fourc, _dc, _virtual_angles)
    if GDA:
        __main__.en = energy
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', __main__.fourc, settings.geometry, __main__.wl)  # @UndefinedVariable

def usehighq():
    print '- setting hkl ---> hkl_highq'
    global settings
    settings.hardware = _hw_m5tth
    settings.geometry = _highq_geometry
    settings.axes_scannable_group = _sc_m5tth

    # Create diffractometer scannable
    _diff_scn_name = _highq_geometry.name
    from diffcalc.dc import dcyou as _dc
    _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_m5tth)

    setLimitsAndCuts(m5tth, th, chi, phi)
    import __main__
    __main__.hkl = hkl_highq
    __main__.h   = hkl_highq.h
    __main__.k   = hkl_highq.k
    __main__.l   = hkl_highq.l
    __main__.fourc = _diff_scn
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.fourc, _dc, _virtual_angles)
    if GDA:
        __main__.en = energy
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', __main__.fourc, settings.geometry, __main__.wl)  # @UndefinedVariable

def usedifftth():
    # sample chamber
    print '- setting hkl ---> hkl_difftth'
    global settings
    settings.hardware = _hw_difftth
    settings.geometry = _tth_geometry
    settings.axes_scannable_group = _sc_difftth

    # Create diffractometer scannable
    _diff_scn_name = _tth_geometry.name
    from diffcalc.dc import dcyou as _dc
    _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_difftth)

    setLimitsAndCuts(difftth, th, chi, phi)
    import __main__
    __main__.hkl = hkl_difftth
    __main__.h   = hkl_difftth.h
    __main__.k   = hkl_difftth.k
    __main__.l   = hkl_difftth.l
    __main__.fourc = _diff_scn
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.fourc, _dc, _virtual_angles)
    if GDA:
        __main__.en = energy
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', __main__.fourc, settings.geometry, __main__.wl)  # @UndefinedVariable

def usesim():
    # sample chamber
    print '- setting hkl ---> hkl_sim'
    print '-          en ---> simenergy'
    global settings
    settings.hardware = _hw_sim
    settings.geometry = _tth_geometry
    settings.axes_scannable_group = _sc_sim

    # Create diffractometer scannable
    import __main__
    _diff_scn_name = _tth_geometry.name
    from diffcalc.dc import dcyou as _dc
    _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_sim)

    __main__.hkl = hkl_sim
    __main__.h   = hkl_sim.h
    __main__.k   = hkl_sim.k
    __main__.l   = hkl_sim.l
    setLimitsAndCuts(simdelta, simth, simchi, simphi)
    __main__.fourc = _diff_scn
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.fourc, _dc, _virtual_angles)
    if GDA:
        __main__.en = simenergy
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', __main__.fourc, settings.geometry, __main__.wl)  # @UndefinedVariable

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
    
print "Created i21 bespoke commands: usem5tth, uselowq, usehighq, usedifftth, usesim, centresample, zerosample, toolpoint_on, toolpoint_off"

if GDA:
    def switchMotors(sax, say, saz, sath, sachi, saphi, diodedelta, specm5tth):
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
        _fourc = ScannableGroup('_fourc', (diodedelta, sath, sachi, saphi)) # I21DiffractometerStage('_fourc', diodedelta, __main__.sa)  # @UndefinedVariable
            #update diffcalc objects
        __main__.settings.hardware = ScannableHardwareAdapter(_fourc, __main__.en, ESMTGKeV)  # @UndefinedVariable
        __main__.settings.geometry = FourCircleI21(beamline_axes_transform=beamline_axes_transform)  # @UndefinedVariable
        __main__.settings.energy_scannable = __main__.en  # @UndefinedVariable
        __main__.settings.axes_scannable_group= _fourc
        __main__.settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV
        
        __main__.fourc=DiffractometerScannableGroup('fourc', _dc, _fourc)
        __main__.hkl = Hkl('hkl', _fourc, _dc)
        __main__.h, __main__.k, __main__.l = hkl.h, hkl.k, hkl.l

        from diffcalc.gdasupport.you import _virtual_angles
        from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter
        from diffcalc.gdasupport.scannable.wavelength import Wavelength
        __main__.hklverbose = Hkl('hklverbose', _fourc, _dc, _virtual_angles)
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', _fourc, __main__.settings.geometry,__main__.wl)  # @UndefinedVariable
        #update scannales: fourc_vessel & hkl_vessel'
        _fourc_vessel = ScannableGroup('_fourc', (specm5tth, sath, sachi, saphi)) # I21DiffractometerStage('_fourc_vessel', m5tth, sa)
        __main__.fourc_vessel = DiffractometerScannableGroup('fourc_vessel', _dc, _fourc_vessel)
        __main__.hkl_vessel = Hkl('hkl_vessel', _fourc_vessel, _dc)
        __main__.h_vessel, __main__.k_vessel, __main__.l_vessel = hkl_vessel.h, hkl_vessel.k, hkl_vessel.l
        
        #Update scannables: fourc_lowq & hkl_lowq'
        _fourc_lowq = ScannableGroup('_fourc', (specm5tth, sath, sachi, saphi)) #I21DiffractometerStage('_fourc_lowq', m5tth, sa,delta_offset=LOWQ_OFFSET_ADDED_TO_DELTA_WHEN_READING)
        __main__.fourc_lowq = DiffractometerScannableGroup('fourc_lowq', _dc, _fourc_lowq)
        __main__.hkl_lowq = Hkl('hkl_lowq', _fourc_lowq, _dc)
        __main__.h_lowq, __main__.k_lowq, __main__.l_lowq = hkl_lowq.h, hkl_lowq.k, hkl_lowq.l
        
        #Update scannables: fourc_highq & hkl_highq'
        _fourc_highq = ScannableGroup('_fourc', (specm5tth, sath, sachi, saphi)) #I21DiffractometerStage('_fourc_highq', m5tth, sa,delta_offset=highq_OFFSET_ADDED_TO_DELTA_WHEN_READING)
        __main__.fourc_highq = DiffractometerScannableGroup('fourc_highq', _dc, _fourc_highq)
        __main__.hkl_highq = Hkl('hkl_highq', _fourc_highq, _dc)
        __main__.h_highq, __main__.k_highq, __main__.l_highq = hkl_highq.h, hkl_highq.k, hkl_highq.l
        
        #Update scannables: fourc_diode & hkl_diode'
        _fourc_diode = ScannableGroup('_fourc', (diodedelta, sath, sachi, saphi)) #I21DiffractometerStage('_fourc_diode', delta, sa)
        __main__.fourc_diode = DiffractometerScannableGroup('fourc_diode', _dc, _fourc_diode)
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
        if GDA:
            stopMotors(x, y, z, th, chi, phi, difftth, m5tth)
        else:
            stopMotors(x, y, z, th, chi, phi, delta, m5tth)
        
        global SIM_MODE
        SIM_MODE=True
        import __main__
        __main__.en=Dummy("en")
        print "Set energy to 12398.425 eV in simulation mode!"
        __main__.en(12398.425) #1 Angstrom wavelength @UndefinedVariable
        print "Switch to simulation motors"
        switchMotors(simx,simy,simz,simth,simchi,simphi,simdelta,simm5tth)
#         __main__.th = __main__.sa.simth  # @UndefinedVariable
#         __main__.chi = __main__.sa.simchi  # @UndefinedVariable
#         __main__.phi = __main__.sa.simphi  # @UndefinedVariable
        setLimitsAndCuts(simdelta,simth,simchi,simphi)
        
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
        if GDA:
            switchMotors(x,y,z,th,chi,phi,difftth,m5tth)
            setLimitsAndCuts(difftth,th,chi,phi)
        else:
            switchMotors(x,y,z,th,chi,phi,delta,m5tth)
            setLimitsAndCuts(delta,th,chi,phi)
     
    from gda.jython.commands.GeneralCommands import alias  # @UnresolvedImport
    alias("usem5tth")
    alias("uselowq")
    alias("usehighq")
    alias("usedifftth")
    alias("usesim")
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
        register_line_magic(parse_line(usem5tth, globals()))
        del usem5tth
        register_line_magic(parse_line(uselowq, globals()))
        del uselowq
        register_line_magic(parse_line(usehighq, globals()))
        del usehighq
        register_line_magic(parse_line(usedifftth, globals()))
        del usedifftth
        register_line_magic(parse_line(usesim, globals()))
        del usesim
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
            startup._demo.Demo.__init__(self, namespace, 'i21')
        
        def i21(self):
            startup._demo.print_heading('i21 scannables demo')
    
            self.echorun_magiccmd_list([
                'sa',
                'pos th 1',
                'pos chi 2',
                'pos phi 3',
                'pos m5tth 4',
                'usem5tth',
                'fourc'])
        
    demo = I21Demo(globals())
else: 
    print "DIFFCALC demo:"
    class I21Demo(object):
        
        def __init__(self, namespace):
            self.namespace = namespace

        def all(self):
            self.orient()
            self.constrain()
            self.scan()
            
        def remove_test_ubcalc(self):
            try:
                eval("rmub('test')", self.namespace)
            except (OSError, KeyError):
                pass
        
        def executeCommand(self, cmd_list):
            for cmd in cmd_list:
                if cmd == 'help ub':
                    print("help ub")
                    exec("print ub.__doc__", self.namespace)
                elif cmd == 'help hkl':
                    print("help(hkl)")
                    exec("print hkl.__doc__", self.namespace)
                else:    
                    exec(cmd, self.namespace) 
    
        def orient(self):
            print
            print "-"*100
            print 'Orientation demo'
            print
            self.remove_test_ubcalc()
            cmd_list=[
                'help ub',
                "from gda.jython.commands.ScannableCommands import pos; pos(wl, 10)",
                "newub('test')",
                "setlat('cubic', 1,1, 1, 90, 90, 90)",
                'ub',
                'c2th([0, 0, .1])',
                'from gda.jython.commands.ScannableCommands import pos; pos(fourc, [60, 30, 0, 0])',
                'addref([0, 0, .1])',
                'c2th([0, .1, .1])',
                'from gda.jython.commands.ScannableCommands import pos; pos(fourc, [90, 90, 0, 0])',
                'addref([0, .1, .1])',
                'ub',
                'checkub']        
            self.executeCommand(cmd_list)
            
        def constrain(self):
            print
            print "-"*100
            print 'Constraint demo'
            print
            cmd_list=[
                'help hkl',
                'con(a_eq_b)',
                'con']
            self.executeCommand(cmd_list)
    
        def scan(self):
            print
            print "-"*100
            print 'Scanning demo'
            print
            
            cmd_list=[
                'setnphi([0, 0, 1])',
                'pos hkl([0, 0, .1])',
                'scan(difftth, 40, 90, 10, hkl, ct, 1)',
                'pos(hkl, [0, .1, 0])',
                'scan(h, 0, .1, .02, k, l, fourc, ct, 1)',
                'con(psi)',
                'scan(psi, 0, 90, 10, hkl, [.1, 0, .1], th, chi, phi, ct, .1)']
            self.executeCommand(cmd_list)
