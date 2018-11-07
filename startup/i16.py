from startup._common_imports import *
from diffcalc.hkl.you.geometry import YouPosition
import diffcalc.hkl.you.geometry
if not GDA:
    import startup._demo

LOCAL_MANUAL = 'http://confluence.diamond.ac.uk/display/I16/Diffcalc%20(i16)'

class SixCircleI16(diffcalc.hkl.you.geometry.YouGeometry):
    def __init__(self):
        diffcalc.hkl.you.geometry.YouGeometry.__init__(self, 'sixc', {})

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        #    i16:   phi, chi, eta, mu, delta, gam
        # H. You:   mu, delta, nu, eta, chi, phi
        phi_phys, chi_phys, eta_phys, mu_phys, delta_phys, gam_phys = physical_angle_tuple
        return YouPosition(mu_phys, delta_phys, gam_phys, eta_phys, chi_phys, phi_phys, unit='DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        mu_phys, delta_phys, nu_phys, eta_phys, chi_phys, phi_phys = clone_position.totuple()
        return phi_phys, chi_phys, eta_phys, mu_phys, delta_phys, nu_phys


if GDA:
    from scannable.extraNameHider import ExtraNameHider
    dummy_energy = Dummy('dummy_energy')
    simple_energy = ExtraNameHider('energy', dummy_energy)  # @UndefinedVariable
    if 'euler' not in locals():
        raise Exception('Expecting a device called euler')

else: # Assume running in dummy mode outside GDA
    mu = Dummy('mu')
    delta = Dummy('delta')
    gam = Dummy('gam')
    eta = Dummy('eta')
    chi = Dummy('chi')
    phi = Dummy('phi')
    euler = ScannableGroup('euler', (phi, chi, eta, mu, delta, gam))
    en = simple_energy = Dummy('energy')
    en.level = 3


### Configure and import diffcalc objects ###
ESMTGKeV = 1
settings.hardware = ScannableHardwareAdapter(euler, simple_energy, ESMTGKeV)
settings.geometry = SixCircleI16()
settings.energy_scannable = simple_energy
settings.axes_scannable_group= euler
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV

from diffcalc.hkl.you.persistence import YouStateEncoder
settings.ubcalc_persister = UBCalculationJSONPersister(diffcalc.settings.ubcalc_persister.directory,
                                                                YouStateEncoder)

from diffcalc.gdasupport.you import *  # @UnusedWildImport

hkl.setLevel(6)

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
    
lastub()  # Load the last ub calculation used

from startup.beamlinespecific.azihkl import AzihklClass
azihkl=AzihklClass('aziref')
azihkl()

# iPython removes the actual command from namespace
if not GDA:
    diffcalc.hardware.setrange(chi, -2, 100)
    diffcalc.hardware.setrange(eta, -2, 92)
    diffcalc.hardware.setrange(delta, -2, 145)
    diffcalc.hardware.setrange(gam, -2, 145)
    setcut(phi, -180)

    demo = startup._demo.Demo(globals(), 'i16')
