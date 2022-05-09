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
    if 'reuler' not in locals():
        raise Exception('Expecting a device called reuler')

else: # Assume running in dummy mode outside GDA
    mu = Dummy('mu')
    delta = Dummy('delta')
    gam = Dummy('gam')
    eta = Dummy('eta')
    chi = Dummy('chi')
    phi = Dummy('phi')
    euler = ScannableGroup('euler', (phi, chi, eta, mu, delta, gam))
    rmu = Dummy('rmu')
    reta = Dummy('reta')
    rchi = Dummy('rchi')
    rphi = Dummy('rphi')
    en = simple_energy = Dummy('energy')
    en.level = 3

### Configure and import diffcalc objects ###

ESMTGKeV = 1
reuler = ScannableGroup('reuler', (rphi, rchi, reta, rmu, delta, gam))
_hw_euler = ScannableHardwareAdapter(euler, simple_energy, ESMTGKeV)
_hw_robot = ScannableHardwareAdapter(reuler, simple_energy, ESMTGKeV)

settings.hardware = _hw_euler
settings.geometry = SixCircleI16()
settings.energy_scannable = simple_energy
settings.axes_scannable_group= euler
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV

from diffcalc.gdasupport.you import *  # @UnusedWildImport

hkl.setLevel(6)

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
    
lastub()  # Load the last ub calculation used

hkl_euler = Hkl('hkl_euler', euler, DiffractometerYouCalculator(_hw_euler, settings.geometry))
hkl_robot = Hkl('hkl_robot', reuler, DiffractometerYouCalculator(_hw_robot, settings.geometry))

from startup.beamlinespecific.azihkl import AzihklClass
azihkl=AzihklClass('aziref')
azihkl()

# iPython removes the actual command from namespace
def setLimitsAndCuts(delta_angle, gam_angle, eta_angle, chi_angle, phi_angle):
    if not GDA:
        diffcalc.hardware.setrange(chi_angle, -2, 100)
        diffcalc.hardware.setrange(eta_angle, -2, 92)
        diffcalc.hardware.setrange(delta_angle, -2, 145)
        diffcalc.hardware.setrange(gam_angle, -2, 145)
        setcut(phi_angle, -180)

demo = startup._demo.Demo(globals(), 'i16')

def useeuler(tp=None):
    # sample chamber
    print '- setting hkl ---> hkl_euler'
    global settings
    settings.hardware = _hw_euler
    settings.axes_scannable_group = euler

    from diffcalc.dc import dcyou as _dc
    reload(_dc)
    lastub()

    setLimitsAndCuts(delta, gam, eta, chi, phi)

    import __main__
    __main__.hkl = hkl_euler
    __main__.h   = hkl_euler.h
    __main__.k   = hkl_euler.k
    __main__.l   = hkl_euler.l

    __main__.sixc = DiffractometerScannableGroup('sixc', _dc, euler)
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.sixc, _dc, _virtual_angles)

    # Custom scannables
    __main__.sr2 = Sr2('sr2', euler, _dc)
    __main__.qtrans = Qtrans('qtrans', euler, _dc)


def userobot(tp=None):
    # sample chamber
    print '- setting hkl ---> hkl_robot'
    global settings
    settings.hardware = _hw_robot
    settings.axes_scannable_group = reuler

    from diffcalc.dc import dcyou as _dc
    reload(_dc)
    lastub()

    setLimitsAndCuts(delta, gam, reta, rchi, rphi)

    import __main__
    __main__.hkl = hkl_robot
    __main__.h   = hkl_robot.h
    __main__.k   = hkl_robot.k
    __main__.l   = hkl_robot.l

    __main__.sixc = DiffractometerScannableGroup('sixc', _dc, reuler)
    from diffcalc.gdasupport.you import _virtual_angles
    __main__.hklverbose = Hkl('hklverbose', __main__.sixc, _dc, _virtual_angles)

    # Custom scannables
    __main__.sr2 = Sr2('sr2', reuler, _dc)
    __main__.qtrans = Qtrans('qtrans', reuler, _dc)

print "Created i16 bespoke commands: useeuler, userobot"

if GDA:
    from gda.jython.commands.GeneralCommands import alias  # @UnresolvedImport
    alias("useeuler")
    alias("userobot")
else:
    from IPython.core.magic import register_line_magic  # @UnresolvedImport
    from diffcmd.ipython import parse_line
    if IPYTHON:
        from IPython import get_ipython  # @UnresolvedImport @UnusedImport
        register_line_magic(parse_line(useeuler, globals()))
        del useeuler
        register_line_magic(parse_line(userobot, globals()))
        del userobot
