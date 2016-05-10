'''
Created on Aug 5, 2013

@author: walton
'''
import os 

from diffcalc.ub.persistence import UBCalculationJSONPersister

###############################################################################
# These should be set via configure()  
geometry = None
hardware = None
ubcalc_persister = UBCalculationJSONPersister(os.getcwd())

#  Used only by diffcalc.gdasupport
axes_scannable_group = None
energy_scannable = None
energy_scannable_multiplier_to_get_KeV=1

# These will be set by dcyou, dcvlieg or dcwillmot
ubcalc_strategy = None
angles_to_hkl_function = None
###############################################################################
   
def configure(hardware=None,
              geometry=None,
              ubcalc_persister=None,
              axes_scannable_group=None,
              energy_scannable = None,
              energy_scannable_multiplier_to_get_KeV=1):
    globals()['hardware'] = hardware
    globals()['geometry'] = geometry
    globals()['ubcalc_persister'] = ubcalc_persister
    globals()['axes_scannable_group'] = axes_scannable_group
    globals()['energy_scannable'] = energy_scannable
    globals()['energy_scannable_multiplier_to_get_KeV'] = energy_scannable_multiplier_to_get_KeV
