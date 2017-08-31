
from __future__ import absolute_import


from diffcalc import settings
from diffcalc.hkl.you.geometry import SixCircle
from diffcalc.hardware import DummyHardwareAdapter
import diffcalc.util  # @UnusedImport


# Disable error handling designed for interactive use
diffcalc.util.DEBUG = True


# Configure and import diffcalc objects
settings.hardware = DummyHardwareAdapter(('mu', 'delta', 'gam', 'eta', 'chi', 'phi'))
settings.geometry = SixCircle()  # @UndefinedVariable


# These must be imported AFTER the settings have been configured
from diffcalc.dc import dcyou as dc
from diffcalc.ub import ub
from diffcalc import hardware
from diffcalc.hkl.you import hkl

# Set some limits
hardware.setmin('gam', -179)
hardware.setmax('gam', 179)

# These demos reproduce the outline in the developer guide
def demo_all():
    demo_orient()
    demo_motion()


def demo_orient():

    ub.listub()
    
    # Create a new ub calculation and set lattice parameters
    ub.newub('test')
    ub.setlat('cubic', 1, 1, 1, 90, 90, 90)
    
    # Add 1st reflection (demonstrating the hardware adapter)
    settings.hardware.wavelength = 1
    ub.c2th([1, 0, 0])                 # energy from hardware
    settings.hardware.position = 0, 60, 0, 30, 0, 0
    ub.addref([1, 0, 0])# energy and position from hardware
    
    # Add 2nd reflection (this time without the harware adapter)
    ub.c2th([0, 1, 0], 12.39842)
    ub.addref([0, 1, 0], [0, 60, 0, 30, 0, 90], 12.39842)
    
    # check the state
    ub.ub()
    ub.checkub()


def demo_motion():
    dc.angles_to_hkl((0., 60., 0., 30., 0., 0.))
    hkl.con('qaz', 90)
    hkl.con('a_eq_b')
    hkl.con('mu', 0)
    
    hardware.setmin('delta', 0)
    dc.hkl_to_angles(1, 0, 0)


demo_all()
    
    
    
    