from diffcalc.utils import allnum

def getNameFromScannableOrString(o):
        try: # it may be a scannable
            return o.getName()
        except AttributeError:
            return str(o)
            raise TypeError()


def sim(scn, hkl, raise_exception_for_unsupported_target):
    """sim hkl [h k l] --simulates moving hkl
    """
    # Catch common input errors here to tkae burdon off Scannable writers
    if not isinstance(hkl, (tuple, list)):
        raise TypeError
    if not allnum(hkl):
        raise TypeError()

    # try command, if we get an atribute error then arg[0] is not a scannable,
    # or is not a scannable that supports simulateMoveTo
    try:
        print scn.simulateMoveTo(hkl)
    except AttributeError:
        # Likely caused bu arg[0] missing method whereMoveTo
        if raise_exception_for_unsupported_target:
            raise TypeError("The first argument does not support simulated moves")
        else:
            print "The first argument does not support simulated moves"

class DummyParameterManager(object):

    def getParameterDict(self):
        return {}

    def _setParameter(self, name, value):
        raise KeyError(name)
        
    def _getParameter(self, name):
        raise KeyError(name)
    
    def updateTrackedParameters(self):
        pass