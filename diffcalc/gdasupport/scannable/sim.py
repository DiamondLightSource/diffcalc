'''
Created on 7 May 2016

@author: walton
'''
from diffcalc.util import allnum

def sim(self, scn, hkl):
    """sim hkl scn -- simulates moving scannable (not all)
    """
    if not isinstance(hkl, (tuple, list)):
        raise TypeError

    if not allnum(hkl):
        raise TypeError()

    try:
        print scn.simulateMoveTo(hkl)
    except AttributeError:
        raise TypeError(
            "The first argument does not support simulated moves")