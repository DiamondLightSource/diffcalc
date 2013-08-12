from diffcalc.util import allnum, command, DiffcalcException

@command
def sim(scn, hkl):
    """sim hkl scn -- simulates moving scannable (not all)
    """
    if not isinstance(hkl, (tuple, list)):
        raise TypeError()

    if not allnum(hkl):
        raise TypeError()

    try:
        print scn.simulateMoveTo(hkl)
    except AttributeError:
        raise TypeError(
                "The first argument does not support simulated moves")
        
def energy_to_wavelength(energy):
    try:
        return 12.39842 / energy
    except ZeroDivisionError:
        raise DiffcalcException(
            "Cannot calculate hkl position as Energy is set to 0")