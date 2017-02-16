'''
Created on Aug 5, 2013

@author: walton
'''
import os 

from diffcalc.ub.persistence import UbCalculationNonPersister

# These should be by the user *before* importing other modules
geometry = None
hardware = None
ubcalc_persister = UbCalculationNonPersister()

axes_scannable_group = None
energy_scannable = None
energy_scannable_multiplier_to_get_KeV=1


# These will be set by dcyou, dcvlieg or dcwillmot
ubcalc_strategy = None
angles_to_hkl_function = None  # Used by checkub to avoid coupling it to an hkl module
include_sigtau=False
include_reference=False