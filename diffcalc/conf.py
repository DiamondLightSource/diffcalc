'''
Created on Aug 5, 2013

@author: walton
'''
from diffcalc.hkl.vlieg.calc import VliegUbCalcStrategy, vliegAnglesToHkl
from diffcalc.hkl.willmott.calc import WillmottHorizontalUbCalcStrategy,\
    angles_to_hkl
from diffcalc.hkl.you.calc import YouUbCalcStrategy, youAnglesToHkl
from diffcalc.ub.persistence import UBCalculationJSONPersister


AVAILABLE_ENGINES = ('vlieg', 'willmott', 'you')


UBCALC_STRATEGIES = {'vlieg': VliegUbCalcStrategy(),
                     'willmott': WillmottHorizontalUbCalcStrategy(),
                     'you': YouUbCalcStrategy()}


ANGLES_TO_HKL_FUNCTIONS = {'vlieg': vliegAnglesToHkl,
                           'willmott': angles_to_hkl,  #  TODO check return format
                           'you': youAnglesToHkl}

'''
This scheme of configuring settings is based loosely to emulate the basics of that of
the successful Python project Django:
https://docs.djangoproject.com/en/dev/topics/settings/#using-settings-in-python-code
'''
class Settings(object):
    
    
    def __init__(self):
        self.GEOMETRY = None
        self.HARDWARE = None
        self.ENGINE_NAME = None
        self.UBCALC_PERSISTER = None
        
    def configure(self,
                 hardware=None,
                 geometry=None,
                 engine_name=None,
                 ubcalc_perister=None):
        
        if engine_name not in AVAILABLE_ENGINES:
            raise AssertionError('unkown engine: %s' % engine_name )
        
        self.GEOMETRY = geometry
        self.HARDWARE = hardware
        self.ENGINE_NAME = engine_name
        self.UBCALC_PERSISTER = ubcalc_perister
        
    @property
    def UBCALC_STRATEGY(self):
        return UBCALC_STRATEGIES[self.ENGINE_NAME]
    
    @property
    def ANGLES_TO_HKL_FUNCTION(self):
        return ANGLES_TO_HKL_FUNCTIONS[self.ENGINE_NAME]
    
    
        
settings = Settings()