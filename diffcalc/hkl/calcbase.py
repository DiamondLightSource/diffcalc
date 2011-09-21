from diffcalc.hkl.modes import ModeSelector
from diffcalc.hkl.parameters import ParameterManager
from diffcalc.utils import DiffcalcException, differ
from math import pi

TORAD = pi / 180
TODEG = 180 / pi

class HklCalculatorBase(object):
    """
    NOTE: IN THIS CLASS ALL ANGLES USED BY EXTERNAL METHODS ARE IN DEGREES AND ALL
    INTERNAL METHODS IN RADIANS. VALUES IN THE PARAMETER DICTIONARY ARE IN DEGREES.
    """

    def __init__(self, ubcalc, geometry, hardware, raiseExceptionsIfAnglesDoNotMapBackToHkl=False):
        
        self._ubcalc = ubcalc # Used only to get the UBMatrix, tau and sigma
        self._geometry = geometry # Used to access information about the diffractometer geometry and mode_selector
        self._gammaParameterName = {'arm':'gamma', 'base':'oopgamma'}[self._geometry.gammaLocation()]
        self._hardware = hardware #Used for tracking parameters only
        self.raiseExceptionsIfAnglesDoNotMapBackToHkl = raiseExceptionsIfAnglesDoNotMapBackToHkl
        
        self.mode_selector = ModeSelector(self._geometry, None, self._gammaParameterName) # parameter_manager set below
        self.parameter_manager = ParameterManager(self._geometry, self._hardware, self.mode_selector, self._gammaParameterName)
        self.mode_selector.setParameterManager(self.parameter_manager)
###
    def __str__(self):
        # should list paramemeters and indicate which are used in selected mode mode.
        result = "Available mode_selector:\n"
        result += self.mode_selector.reportAvailableModes()
        result += '\nCurrent mode:\n'
        result += self.mode_selector.reportCurrentMode()
        result += '\n\nParameters:\n'
        result += self.parameter_manager.reportAllParameters()
        return result
###
    def anglesToHkl(self, pos, energy):
        """
        ((h, k, l), paramDict) = anglesToHkl(pos, energy) -- Returns hkl indices from pos object in degrees.
        """
        # Calculate the (possibly) virtual angles: 2theta, betain, betaout, azimuth    
   
        h, k, l = self._anglesToHkl(pos.inRadians(), energy)
        paramDict = self.anglesToVirtualAngles(pos, energy)
        return ((h, k, l), paramDict)   

    def anglesToVirtualAngles(self, pos, energy):
        anglesDict = self._anglesToVirtualAngles(pos.inRadians(), energy)
        for name in anglesDict:
            anglesDict[name] = anglesDict[name] * TODEG
        return anglesDict
    
    def hklToAngles(self, h, k, l, energy):
        """calls _hklToAngles() and then checks if the calculated angles map
        back to the requested hkl setting. Also calculates the virtual angles
        associated with the calculated angle, and checks that they agree with any
        specified or derived as part of the initial calculation.
        """
        
        # Update tracked parameters. During this calculation parameter values will
        # be read directly from self._parameters instead of via self.getParameter
        # which would trigger another potentially time-costly position update.
        self.parameter_manager.updateTrackedParameters()
        
        (pos, virtualAngles) = self._hklToAngles(h, k, l, energy)
        (hkl, _) = self.anglesToHkl(pos, energy)
        e = 0.001
        if (abs(hkl[0] - h) > e) or (abs(hkl[1] - k) > e) or (abs(hkl[2] - l) > e):
            s = "PROBABLE ERROR: The angles calculated for hkl=(%f,%f,%f) were %s.\n" % (h, k, l, str(pos))
            s += "Converting these angles back to hkl resulted in hkl=(%f,%f,%f)" % (hkl[0], hkl[1], hkl[2])
            if self.raiseExceptionsIfAnglesDoNotMapBackToHkl:
                raise DiffcalcException(s)
            else:
                print s
                
        # Check that the virtual angles calculated/fixed during the hklToAnglesXXX calculation
        # those read back from pos using anglesToVirtualAngles
        virtualAnglesReadback = self.anglesToVirtualAngles(pos, energy)
                    
        for key, val in virtualAngles.items():
            if val != None: #Some values calculated in some mode_selector
                d = differ(val, virtualAnglesReadback[key], .00001)
                if d:
                    s = "PROBABLE ERROR: The angles calculated for hkl=(%f,%f,%f) with mode=%s were %s.\n" % (h, k, l, self._mode.name, str(pos))
                    s += "During verification the virtual angle %s resulting from (or set for) this calculation of %f" % (key, val)
                    s += "did not match that calculated by anglesToVirtualAngles of %f" % virtualAnglesReadback[key]
                    # TODO: misuse of existing variable: rename it
                    if self.raiseExceptionsIfAnglesDoNotMapBackToHkl:
                        raise DiffcalcException(s)
                    else:
                        print s
        
        # Return the verified, and posibbly more complete, virtualAnglesReadback
        return (pos, virtualAnglesReadback)

### Collect all math access to context here

    def _getUBMatrix(self):
        return self._ubcalc.getUBMatrix()
        
    def _getMode(self):
        return self.mode_selector.getMode()
    
    def _getSigma(self):
        return self._ubcalc.getSigma()
    
    def _getTau(self):
        return self._ubcalc.getTau()
    
    def _getParameter(self, name):
        # Does not use context.getParameter as this will trigger a costly parameter collection
        return self.parameter_manager.getParameterWithoutUpdatingTrackedParemeters(name)
    
    def _getGammaParameterName(self):
        return self._gammaParameterName
    
