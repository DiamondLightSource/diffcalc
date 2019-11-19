from startup._common_imports import *  # @UnusedWildImport

from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup
from startup.beamlinespecific.i21 import FourCircleI21, DiffractometerTPScannableGroup, TPScannableGroup

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

if not GDA:    
    import startup._demo
else:
#     import __main__  # @UnresolvedImport
    from __main__ import th, chi, phi, difftth, m5tth, energy, simth,simchi,simphi,simdelta,simm5tth, ps_chi, ps_phi # @UnresolvedImport

LOCAL_MANUAL = "http://confluence.diamond.ac.uk/x/UoIQAw"
# Diffcalc i21
# ======== === 
# delta    difftth or m5tth
# eta      th
# chi      chi
# phi      -phi

### Create dummy scannables ###
if not GDA:  
    delta = Dummy('delta')
    m5tth = Dummy('m5tth')
    th = Dummy('th')
    chi = Dummy('chi')
    phi = Dummy('phi')

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

    _sc_difftth_tp = TPScannableGroup('_fourc', (difftth, th, ps_chi, ps_phi))
    _sc_m5tth_tp = TPScannableGroup('_fourc', (m5tth, th, ps_chi, ps_phi))

    _sc_sim = ScannableGroup('_fourc', (simdelta, simth, simchi, simphi))
else:
    _sc_difftth = _sc_m5tth = _sc_sim = ScannableGroup('_fourc', (delta, th, chi, phi))

ESMTGKeV = 0.001
_hw_difftth = ScannableHardwareAdapter(_sc_difftth, en, ESMTGKeV)
_hw_m5tth = ScannableHardwareAdapter(_sc_m5tth, en, ESMTGKeV)
if GDA:
    _hw_difftth_tp = ScannableHardwareAdapter(_sc_difftth_tp, en, ESMTGKeV)
    _hw_m5tth_tp = ScannableHardwareAdapter(_sc_m5tth_tp, en, ESMTGKeV)
_hw_sim = ScannableHardwareAdapter(_sc_sim, simenergy, ESMTGKeV)

settings.hardware = _hw_difftth
settings.geometry = _tth_geometry
settings.energy_scannable = en
settings.axes_scannable_group = _sc_difftth
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV

from diffcalc.hkl.you.persistence import YouStateEncoder
settings.ubcalc_persister = UBCalculationJSONPersister(diffcalc.settings.ubcalc_persister.directory,
                                                                YouStateEncoder)

from diffcalc.gdasupport.you import *  # @UnusedWildImport

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
 
### Load the last ub calculation used
from diffcalc.ub.ub import lastub
lastub()
 
### Set i21 specific limits
def setLimitsAndCuts(delta_angle, eta_angle, chi_angle, phi_angle):
    ''' set motor limits for diffcalc, these are within the actual motor limits
    '''
    if not GDA:
        print "INFO: diffcalc limits set in $diffcalc/startup/i21.py taken from http://confluence.diamond.ac.uk/pages/viewpage.action?pageId=51413586"
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
if GDA:
    hkl_m5tth_tp = Hkl('hkl_m5tth_tp', _sc_m5tth_tp, DiffractometerYouCalculator(_hw_m5tth_tp, _tth_geometry))
    hkl_lowq_tp = Hkl('hkl_lowq_tp', _sc_m5tth_tp, DiffractometerYouCalculator(_hw_m5tth_tp, _lowq_geometry))
    hkl_highq_tp = Hkl('hkl_highq_tp', _sc_m5tth_tp, DiffractometerYouCalculator(_hw_m5tth_tp, _highq_geometry))
    hkl_difftth_tp = Hkl('hkl_difftth_tp', _sc_difftth_tp, DiffractometerYouCalculator(_hw_difftth_tp, _tth_geometry))

hkl_sim = Hkl('hkl_sim', _sc_sim, DiffractometerYouCalculator(_hw_sim, _tth_geometry))

# Custom scannables
from startup.beamlinespecific.conic_scannables import conic_h, conic_k, conic_l, conic_th

def usem5tth_tp():
    if GDA:
        usem5tth(True)

def uselowq_tp():
    if GDA:
        uselowq(True)

def usehighq_tp():
    if GDA:
        usehighq(True)

def usedifftth_tp():
    if GDA:
        usedifftth(True)

def usem5tth(tp=None):
    print '- setting hkl ---> hkl_m5tth'
    global settings
    if tp:
        settings.hardware = _hw_m5tth_tp
    else:
        settings.hardware = _hw_m5tth
    settings.geometry = _tth_geometry
    if tp:
        settings.axes_scannable_group = _sc_m5tth_tp
    else:
        settings.axes_scannable_group = _sc_m5tth

    # Create diffractometer scannable
    _diff_scn_name = _tth_geometry.name
    from diffcalc.dc import dcyou as _dc
    reload(_dc)
    lastub()

    if tp:
        _diff_scn = DiffractometerTPScannableGroup(_diff_scn_name, _dc, _sc_m5tth_tp)
    else:
        _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_m5tth)

    if tp:
        setLimitsAndCuts(m5tth, th, ps_chi, ps_phi)
    elif GDA:
        setLimitsAndCuts(m5tth, th, chi, phi)
    else:
        setLimitsAndCuts(delta, th, chi, phi)

    import __main__
    if tp:
        __main__.hkl = hkl_m5tth_tp
        __main__.h   = hkl_m5tth_tp.h
        __main__.k   = hkl_m5tth_tp.k
        __main__.l   = hkl_m5tth_tp.l
    else:
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

    # Custom scannables
    import startup.beamlinespecific.conic_scannables as _conic
    reload(_conic)
    __main__.conic_h = _conic.conic_h
    __main__.conic_k = _conic.conic_k
    __main__.conic_l = _conic.conic_l


def uselowq(tp=None):
    print '- setting hkl ---> hkl_lowq'
    global settings
    if tp:
        settings.hardware = _hw_m5tth_tp
    else:
        settings.hardware = _hw_m5tth
    settings.geometry = _lowq_geometry
    if tp:
        settings.axes_scannable_group = _sc_m5tth_tp
    else:
        settings.axes_scannable_group = _sc_m5tth

    # Create diffractometer scannable
    _diff_scn_name = _lowq_geometry.name
    from diffcalc.dc import dcyou as _dc
    reload(_dc)
    lastub()

    if tp:
        _diff_scn = DiffractometerTPScannableGroup(_diff_scn_name, _dc, _sc_m5tth_tp)
    else:
        _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_m5tth)

    if tp:
        setLimitsAndCuts(m5tth, th, ps_chi, ps_phi)
    elif GDA:
        setLimitsAndCuts(m5tth, th, chi, phi)
    else:
        setLimitsAndCuts(delta, th, chi, phi)
    
    import __main__
    if tp:
        __main__.hkl = hkl_lowq_tp
        __main__.h   = hkl_lowq_tp.h
        __main__.k   = hkl_lowq_tp.k
        __main__.l   = hkl_lowq_tp.l
    else:
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

    # Custom scannables
    import startup.beamlinespecific.conic_scannables as _conic
    reload(_conic)
    __main__.conic_h = _conic.conic_h
    __main__.conic_k = _conic.conic_k
    __main__.conic_l = _conic.conic_l


def usehighq(tp=None):
    print '- setting hkl ---> hkl_highq'
    global settings
    if tp:
        settings.hardware = _hw_m5tth_tp
    else:
        settings.hardware = _hw_m5tth
    settings.geometry = _highq_geometry
    if tp:
        settings.axes_scannable_group = _sc_m5tth_tp
    else:
        settings.axes_scannable_group = _sc_m5tth

    # Create diffractometer scannable
    _diff_scn_name = _highq_geometry.name
    from diffcalc.dc import dcyou as _dc
    reload(_dc)
    lastub()

    if tp:
        _diff_scn = DiffractometerTPScannableGroup(_diff_scn_name, _dc, _sc_m5tth_tp)
    else:
        _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_m5tth)

    if tp:
        setLimitsAndCuts(m5tth, th, ps_chi, ps_phi)
    elif GDA:
        setLimitsAndCuts(m5tth, th, chi, phi)
    else:
        setLimitsAndCuts(delta, th, chi, phi)

    import __main__
    if tp:
        __main__.hkl = hkl_highq_tp
        __main__.h   = hkl_highq_tp.h
        __main__.k   = hkl_highq_tp.k
        __main__.l   = hkl_highq_tp.l
    else:
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

    # Custom scannables
    import startup.beamlinespecific.conic_scannables as _conic
    reload(_conic)
    __main__.conic_h = _conic.conic_h
    __main__.conic_k = _conic.conic_k
    __main__.conic_l = _conic.conic_l

def usedifftth(tp=None):
    # sample chamber
    print '- setting hkl ---> hkl_difftth'
    global settings
    if tp:
        settings.hardware = _hw_difftth_tp
    else:
        settings.hardware = _hw_difftth
    settings.geometry = _tth_geometry
    if tp:
        settings.axes_scannable_group = _sc_difftth_tp
    else:
        settings.axes_scannable_group = _sc_difftth

    # Create diffractometer scannable
    _diff_scn_name = _tth_geometry.name

    from diffcalc.dc import dcyou as _dc
    reload(_dc)
    lastub()

    if tp:
        _diff_scn = DiffractometerTPScannableGroup(_diff_scn_name, _dc, _sc_difftth_tp)
    else:
        _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_difftth)

    if tp:
        setLimitsAndCuts(difftth, th, ps_chi, ps_phi)
    elif GDA:
        setLimitsAndCuts(difftth, th, chi, phi)
    else:
        setLimitsAndCuts(delta, th, chi, phi)

    import __main__
    if tp:
        __main__.hkl = hkl_difftth_tp
        __main__.h   = hkl_difftth_tp.h
        __main__.k   = hkl_difftth_tp.k
        __main__.l   = hkl_difftth_tp.l
    else:
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

    # Custom scannables
    import startup.beamlinespecific.conic_scannables as _conic
    reload(_conic)
    __main__.conic_h = _conic.conic_h
    __main__.conic_k = _conic.conic_k
    __main__.conic_l = _conic.conic_l

def usesim():
    # sample chamber
    print '- setting hkl ---> hkl_sim'
    print '-          en ---> simenergy'
    global settings
    settings.hardware = _hw_sim
    settings.geometry = _tth_geometry
    settings.axes_scannable_group = _sc_sim

    setLimitsAndCuts(simdelta, simth, simchi, simphi)

    # Create diffractometer scannable
    import __main__
    _diff_scn_name = _tth_geometry.name
    from diffcalc.dc import dcyou as _dc
    reload(_dc)
    lastub()

    _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sc_sim)

    __main__.hkl = hkl_sim
    __main__.h   = hkl_sim.h
    __main__.k   = hkl_sim.k
    __main__.l   = hkl_sim.l

    __main__.fourc = _diff_scn
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.fourc, _dc, _virtual_angles)
    if GDA:
        __main__.en = simenergy
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', __main__.fourc, settings.geometry, __main__.wl)  # @UndefinedVariable
    # Custom scannables
    import startup.beamlinespecific.conic_scannables as _conic
    reload(_conic)
    __main__.conic_h = _conic.conic_h
    __main__.conic_k = _conic.conic_k
    __main__.conic_l = _conic.conic_l


print "Created i21 bespoke commands:      usem5tth,    uselowq,    usehighq,    usedifftth"
print "Set toolpoint mode using commands: usem5tth_tp, uselowq_tp, usehighq_tp, usedifftth_tp"
print "Set simulation mode using command: usesim"

if GDA:
    from gda.jython.commands.GeneralCommands import alias  # @UnresolvedImport
    alias("usem5tth")
    alias("uselowq")
    alias("usehighq")
    alias("usedifftth")
    alias("usem5tth_tp")
    alias("uselowq_tp")
    alias("usehighq_tp")
    alias("usedifftth_tp")
    alias("usesim")
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
        register_line_magic(parse_line(usem5tth_tp, globals()))
        del usem5tth_tp
        register_line_magic(parse_line(uselowq_tp, globals()))
        del uselowq_tp
        register_line_magic(parse_line(usehighq_tp, globals()))
        del usehighq_tp
        register_line_magic(parse_line(usedifftth_tp, globals()))
        del usedifftth_tp
        register_line_magic(parse_line(usesim, globals()))
        del usesim

### Demo ###

if not GDA:
    class I21Demo(startup._demo.Demo):
        
        def __init__(self, namespace):
            startup._demo.Demo.__init__(self, namespace, 'i21')
        
        def i21(self):
            startup._demo.print_heading('i21 scannables demo')
    
            self.echorun_magiccmd_list([
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
