from startup._common_imports import *  # @UnusedWildImport
from diffcalc.gdasupport.minigda.scannable import ScannableMotionWithScannableFieldsBase  # @UnusedImport
from diffcalc.gdasupport.minigda.scannable import DummyPD
if not GDA:    
    import startup._demo
else:
#     import __main__  # @UnresolvedImport
    from __main__ import dd2th,ddth,energy  # @UnresolvedImport
LOCAL_MANUAL = "http://confluence.diamond.ac.uk/pages/viewpage.action?pageId=31853413"
# Diffcalc i06-1
# ======== === 
# delta    dd2th
# eta      ddth
# chi      dummy
# phi      dummy


### Create dummy scannables ###
chi = DummyPD('chi')
phi = DummyPD('phi')
if GDA:  
    print "!!! Starting LIVE diffcalc with delta(dd2th), eta(ddth), chi(dummy), phi(dummy) and denergy." 
    _fourc = ScannableGroup('_fourc', (dd2th, ddth, chi, phi))
    delta = _fourc.dd2th
    eta = _fourc.ddth
    en=energy
    if float(en.getPosition()) == 0: # no energy value - dummy mode
        en(800)
    
else:   
    delta = Dummy('delta')
    eta = Dummy('eta')
    _fourc = ScannableGroup('_fourc', (delta, eta, chi, phi))
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
 
if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
 
# Load the last ub calculation used
lastub() 
if not GDA:
    demo = startup._demo.Demo(globals(), 'fourc')
