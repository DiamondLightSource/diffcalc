from startup._common_imports import *
from diffcalc.hkl.you.geometry import YouPosition
import diffcalc.hkl.you.geometry

if GDA:
    from __main__ import delta, theta, chi, phi

from diffcalc.hkl.you.geometry import YouRemappedGeometry

class FourCircleB16(YouRemappedGeometry):
    """For a diffractometer with angles:
          delta, theta, chi, phi
    """
    def __init__(self, beamline_axes_transform=None):
        YouRemappedGeometry.__init__(self, 'fourc', {"gam": 0, "mu": 0}, beamline_axes_transform)

        # Order should match scannable order in _fourc group for mapping to work correctly
        self._scn_mapping_to_int = (('delta', lambda x: x),
                                    ('eta',   lambda x: x),
                                    ('chi',   lambda x: x + 90.0),
                                    ('phi',   lambda x: x))
        self._scn_mapping_to_ext = (('delta', lambda x: x),
                                    ('eta',   lambda x: x),
                                    ('chi',   lambda x: x - 90.0),
                                    ('phi',   lambda x: x))

if GDA:
    from scannable.extraNameHider import ExtraNameHider
    dummy_energy = Dummy('dummy_energy')
    simple_energy = ExtraNameHider('energy', dummy_energy)  # @UndefinedVariable

else: # Assume running in dummy mode outside GDA
    delta = Dummy('delta')
    theta = Dummy('theta')
    chi = Dummy('chi')
    phi = Dummy('phi')
    energy = simple_energy = Dummy('energy')
    energy.level = 3

### Configure and import diffcalc objects ###

ESMTGKeV = 0.001
euler = ScannableGroup('euler', (delta, theta, chi, phi))

settings.hardware = ScannableHardwareAdapter(euler, simple_energy, ESMTGKeV)
settings.geometry = FourCircleB16()
settings.energy_scannable = simple_energy
settings.axes_scannable_group= euler
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV

from diffcalc.gdasupport.you import *  # @UnusedWildImport

hkl.setLevel(6)

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
    
#lastub()  # Load the last ub calculation used

from startup.beamlinespecific.azihkl import AzihklClass
azihkl=AzihklClass('aziref')
azihkl()

# iPython removes the actual command from namespace
if not GDA:
    diffcalc.hardware.setrange(chi, -96.4, 259.4)
    diffcalc.hardware.setrange(phi, -147, 150)
    diffcalc.hardware.setrange(theta, -100, 235)
    diffcalc.hardware.setrange(delta, -10.4, 101.9)
    setcut(phi, -180)
