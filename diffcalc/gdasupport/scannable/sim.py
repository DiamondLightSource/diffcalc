'''
Created on 7 May 2016

@author: walton
'''

def sim(scn, hkl):
    """sim hkl scn -- simulates moving scannable (not all)
    """
    try:
        print scn.simulateMoveTo(hkl)
    except AttributeError:
        raise TypeError(
            "The first argument does not support simulated moves")