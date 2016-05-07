'''
Created on Aug 5, 2013

@author: walton
'''
import os 

import diffcalc.hkl.vlieg.calc
import diffcalc.hkl.willmott.calc
import diffcalc.hkl.you.calc
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

    
def set_engine_name(engine_name):
    '''This will be called by one of dcyou, dcvlieg or dcwillmot'''
    global ubcalc_strategy
    global angles_to_hkl_function
    assert engine_name in _AVAILABLE_ENGINES
    ubcalc_strategy = _UBCALC_STRATEGIES[engine_name]
    angles_to_hkl_function = _ANGLES_TO_HKL_FUNCTIONS[engine_name]
    
    
_AVAILABLE_ENGINES = ('vlieg', 'willmott', 'you')


_UBCALC_STRATEGIES = {'vlieg': diffcalc.hkl.vlieg.calc.VliegUbCalcStrategy(),
                     'willmott': diffcalc.hkl.willmott.calc.WillmottHorizontalUbCalcStrategy(),
                     'you': diffcalc.hkl.you.calc.YouUbCalcStrategy()}


_ANGLES_TO_HKL_FUNCTIONS = {'vlieg': diffcalc.hkl.vlieg.calc.vliegAnglesToHkl,
                           'willmott': diffcalc.hkl.willmott.calc.angles_to_hkl,  #  TODO check return format
                           'you': diffcalc.hkl.you.calc.youAnglesToHkl}