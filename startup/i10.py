from startup._common_imports import *  # @UnusedWildImport
from diffcalc.hkl.you.geometry import YouRemappedGeometry
from diffcalc.settings import NUNAME

if not GDA:    
    import startup._demo
else:
#     import __main__  # @UnresolvedImport
    from __main__ import tth,tthArea,th,thArea,chi,pgm_energy, simtth,simth,simchi,simalpha # @UnresolvedImport

LOCAL_MANUAL = ""

SIM_MODE=False

class FourCircleI10(YouRemappedGeometry):
    """For a diffractometer with angles:
          delta, eta, chi, phi
    """
    def __init__(self, beamline_axes_transform=None):
        YouRemappedGeometry.__init__(self, 'fourc', {'mu': 0, NUNAME: 0, 'phi': 0}, beamline_axes_transform)

        # Order should match scannable order in _fourc group for mapping to work correctly
        self._scn_mapping_to_int = (('delta', lambda x: x),
                                    ('eta',   lambda x: x),
                                    ('chi',   lambda x: x),
                                    ('phi',   lambda x: x))
        self._scn_mapping_to_ext = (('delta', lambda x: x),
                                    ('eta',   lambda x: x),
                                    ('chi',   lambda x: x),
                                    ('phi',   lambda x: x))
### Create dummy scannables ###
if GDA:  
    ###map GDA scannable to diffcalc axis name###
    phi = Dummy('phi')
    _fourc = ScannableGroup('_fourc', (tth, th, chi, phi))
    _area_fourc = ScannableGroup('_fourc', (tthArea, thArea, chi, phi))
    _sim_fourc = ScannableGroup('_fourc', (simtth, simth, simchi, simalpha))
    en=pgm_energy
    if float(en.getPosition()) == 0: # no energy value - dummy mode
        en(800)
    simenergy = Dummy('en')
    simenergy(800)
else:
    #Create dummy axes to run outside GDA in IPython#   
    delta = Dummy('delta')
    eta = Dummy('eta')
    chi = Dummy('chi')
    phi = Dummy('phi')
    _fourc = _area_fourc = _sim_fourc = ScannableGroup('_fourc', (delta, eta, chi, phi))
    en = simenergy = Dummy('en')
    en(800)

en.level = 3
_geometry = FourCircleI10()

### Configure and import diffcalc objects ###
ESMTGKeV = 0.001
_hw = ScannableHardwareAdapter(_fourc, en, ESMTGKeV)
_area_hw = ScannableHardwareAdapter(_area_fourc, en, ESMTGKeV)
_hw_sim = ScannableHardwareAdapter(_sim_fourc, simenergy, ESMTGKeV)
settings.hardware = _hw
settings.geometry = _geometry
settings.energy_scannable = en
settings.axes_scannable_group= _fourc
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV
 
from diffcalc.gdasupport.you import *  # @UnusedWildImport

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
 
### Load the last ub calculation used
lastub()
 
### Set i10 specific limits
def setLimitsAndCuts(delta,eta,chi,phi):
    ''' set motor limits for diffcalc, these are within the actual motor limits
    '''
    if not GDA:
        setmin(delta, -60.0)
        setmax(delta, 165.0) 
        setmin(eta, -94.408)
        setmax(eta, 190.591)
        setmin(chi, 85.5)
        setmax(chi, 94.5)
        setmin(phi, 0)
        setmax(phi, 360.0)
    print "Current hardware limits set to:"
    hardware()

if not GDA:
    setLimitsAndCuts(delta,eta,chi,phi)

if GDA:
    def swithMotors(delta, mu, eta, chi, phi):
        import __main__
        from diffcalc.dc import dcyou as _dc
        
        ### update Wrap i21 names to get diffcalc names
        _fourc = ScannableGroup('_fourc', (delta, mu, eta, chi, phi))
        #update diffcalc objects
        __main__.settings.hardware = ScannableHardwareAdapter(_fourc, __main__.en, ESMTGKeV)  # @UndefinedVariable
        __main__.settings.geometry = diffcalc.hkl.you.geometry.FourCircle()  # @UndefinedVariable
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
        
    def stopMotors(delta, eta, chi, phi):
        delta.stop()
        eta.stop()
        chi.stop()
        phi.stop()
        
    def simdc():
        ''' switch to use dummy motors in diffcalc
        '''
        print "Stop real motors"
        stopMotors(tth,th,chi,phi)
        
        global SIM_MODE
        SIM_MODE=True
        import __main__
        __main__.en=Dummy("en")
        print "Set energy to 12398.425 eV in simulation mode!"
        __main__.en(12398.425) #1 Angstrom wavelength @UndefinedVariable
        print "Switch to simulation motors"
        swithMotors(simtth,simalpha,simth,simchi,phi)
        setLimitsAndCuts(simtth,simalpha,simth,simchi,phi)
        
    def realdc():
        ''' switch to use real motors in diffcalc
        '''
        print "Stop simulation motors"
        stopMotors(simtth,simalpha,simth,simchi,phi)
        
        global SIM_MODE
        SIM_MODE=False
        import __main__
        print "Set energy to current beamline energy in real mode!"
        __main__.en=pgm_energy
        print "Switch to real motors"
        swithMotors(tth,th,chi,phi)
        setLimitsAndCuts(tth,th,chi,phi)
     
    from gda.jython.commands.GeneralCommands import alias  # @UnresolvedImport
    print "Created commands: 'simdc' and 'realdc' to switch between real and simulated motors."
    alias("simdc")
    alias("realdc")


hkl_ccd = Hkl('hkl_ccd', _area_fourc, DiffractometerYouCalculator(_area_hw, _geometry))
hkl_point = Hkl('hkl_point', _fourc, DiffractometerYouCalculator(_hw, _geometry))


def useccd():
    print '- setting hkl ---> hkl_ccd'
    global settings
    settings.hardware = _area_hw
    settings.energy_scannable = pgm_energy
    settings.axes_scannable_group= _area_fourc

    # Create diffractometer scannable
    from diffcalc.dc import dcyou as _dc
    _diff_scn = DiffractometerScannableGroup(settings.geometry.name, _dc, _area_fourc)

    setLimitsAndCuts(tthArea,thArea,chi,phi)
    import __main__
    __main__.hkl = hkl_ccd
    __main__.h   = hkl_ccd.h
    __main__.k   = hkl_ccd.k
    __main__.l   = hkl_ccd.l
    __main__.fourc = _diff_scn
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.fourc, _dc, _virtual_angles)
    if GDA:
        __main__.en = pgm_energy
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', __main__.fourc, settings.geometry, __main__.wl)  # @UndefinedVariable

def usepoint():
    print '- setting hkl ---> hkl_point'
    global settings
    settings.hardware = _hw
    settings.energy_scannable = pgm_energy
    settings.axes_scannable_group= _fourc

    # Create diffractometer scannable
    from diffcalc.dc import dcyou as _dc
    _diff_scn = DiffractometerScannableGroup(settings.geometry.name, _dc, _fourc)

    setLimitsAndCuts(tth,th,chi,phi)
    import __main__
    __main__.hkl = hkl_point
    __main__.h   = hkl_point.h
    __main__.k   = hkl_point.k
    __main__.l   = hkl_point.l
    __main__.fourc = _diff_scn
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.fourc, _dc, _virtual_angles)
    if GDA:
        __main__.en = pgm_energy
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', __main__.fourc, settings.geometry, __main__.wl)  # @UndefinedVariable

def usesim():
    # sample chamber
    print '- setting hkl ---> hkl_sim'
    print '-          en ---> simenergy'
    global settings
    settings.hardware = _hw_sim
    settings.energy_scannable = simenergy
    settings.axes_scannable_group = _sim_fourc

    # Create diffractometer scannable
    import __main__
    _diff_scn_name = settings.geometry.name
    from diffcalc.dc import dcyou as _dc
    _diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _sim_fourc)
    hkl_sim = Hkl('hkl_sim', _sim_fourc, DiffractometerYouCalculator(_hw_sim, settings.geometry))

    __main__.hkl = hkl_sim
    __main__.h   = hkl_sim.h
    __main__.k   = hkl_sim.k
    __main__.l   = hkl_sim.l
    setLimitsAndCuts(simtth, simth, simchi, simalpha)
    __main__.fourc = _diff_scn
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.fourc, _dc, _virtual_angles)
    if GDA:
        __main__.en = simenergy
        __main__.wl = Wavelength('wl',__main__.en,ESMTGKeV)  # @UndefinedVariable
        __main__.ct = SimulatedCrystalCounter('ct', __main__.fourc, settings.geometry, __main__.wl)  # @UndefinedVariable

### Demo ###
if not GDA:
    demo = demo = startup._demo.Demo(globals(), 'fourc')
