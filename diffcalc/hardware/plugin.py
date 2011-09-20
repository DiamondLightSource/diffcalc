
SMALL = 1e-8

class HardwareMonitorPlugin:
    
    _name = "BaseHarwdareMonitor"
    
    def __init__(self, diffractometerAngleNames, defaultCuts = {}, energyScannableMultiplierToGetKeV=1):
        
        self._diffractometerAngleNames = diffractometerAngleNames
        self._upperLimitDict = {}
        self._lowerLimitDict = {} 
        self._cutAngles = {}
        self._configureCuts(defaultCuts)
        self.energyScannableMultiplierToGetKeV = energyScannableMultiplierToGetKeV

    def getPhysicalAngleNames(self):
        return tuple(self._diffractometerAngleNames)

    def getPosition(self):
        """pos = getPosition() -- returns the current physical diffractometer
        position as a diffcalc.utils object in degrees
        """
        #### Overide me ###
        raise Exception("Abstract")

    def getWavelength(self):
        """wavelength = getWavelength() -- returns wavelength in Angstroms
        """
        return 12.39842/self.getEnergy()    
    
    def getEnergy(self):
        """energy = getEnergy() -- returns energy in kEv  """
        #### Overide me ###
        raise Exception("Abstract")

    def getDiffHardwareName(self):
        return 'base'

    def __str__(self):
        toReturn = self._name +":\n"
        toReturn += "  energy : " + str(self.getEnergy()) + " keV\n"
        toReturn += "  wavelength : " + str(self.getWavelength()) + " Angstrom\n"
        for name, pos in zip(self._diffractometerAngleNames, self.getPosition()):
            toReturn += "  %s : %s deg\n" % (name, `pos`)
        return toReturn
    
    def __repr__(self):
        return self.__str__()
    
    def getPositionByName(self, angleName):
        return self.getPosition()[list(self._diffractometerAngleNames).index(angleName)]

### Limits ###
    
    def getLowerLimit(self, name):
        '''returns lower limits by axis name. Limit may be None if not set
        '''
        if name not in self._diffractometerAngleNames:
            raise ValueError("No angle called %s. Try one of: %s" % (name, self._diffractometerAngleNames))
        return self._lowerLimitDict.get(name)

    def getUpperLimit(self, name):
        '''returns upper limit by axis name. Limit may be None if not set
        '''
        if name not in self._diffractometerAngleNames:
            raise ValueError("No angle called %s. Try one of: %s" % (name, self._diffractometerAngleNames))
        return self._upperLimitDict.get(name)

    def setLowerLimit(self, name, value):
        """value may be None to remove limit"""
        if name not in self._diffractometerAngleNames:
            raise ValueError("Cannot set lower Diffcalc limit: No angle called %s. Try one of: %s" % (name, self._diffractometerAngleNames))
        if value is None:
            try:
                del self._lowerLimitDict[name]
            except KeyError:
                print "WARNING: There was no lower Diffcalc limit %s set to clear" % name
        else:
            self._lowerLimitDict[name] = value
                
    def setUpperLimit(self, name, value):
        """value may be None to remove limit"""
        if name not in self._diffractometerAngleNames:
            raise ValueError("Cannot set upper Diffcalc limit: No angle called %s. Try one of: %s" % (name, self._diffractometerAngleNames))
        if value is None:
            try:
                del self._upperLimitDict[name]
            except KeyError:
                print "WARNING: There was no upper Diffcalc limit %s set to clear" % name
        else:
            self._upperLimitDict[name] = value
            
    def isPositionWithinLimits(self, positionArray):
        """where position array is in degrees and cut to be between -180 and 180"""
        for name, val in zip(self._diffractometerAngleNames, positionArray):
            if self._upperLimitDict.has_key(name):
                if val > self._upperLimitDict[name]:
                    return False
            if self._lowerLimitDict.has_key(name):
                if val < self._lowerLimitDict[name]:
                    return False
        return True
    
    def reprSectorLimitsAndCuts(self, name=None):
        if name is None:
            s='Cuts and Sector-limits:\n'
            for name in self.getPhysicalAngleNames():
                s += self.reprSectorLimitsAndCuts(name) + '\n'
            return s + "  Note: When auto sector/transforms are used, cuts are applied before checking limits." 
        # limits:
        low = self.getLowerLimit(name)
        max = self.getUpperLimit(name)
        s = '  '
        if low is not None:
            s += "%f <= " % low
        s += name
        if max is not None:
            s += " <= %f" % max
        # cuts:
        try:
            if self.getCuts()[name] is not None:
                s += " - cut at %f" % self.getCuts()[name]
        except KeyError:
            pass    
            
        return s

### Cutting Stuff ###

    def _configureCuts(self, defaultCutsDict):
        # 1. Set default cut angles
        self._cutAngles = dict.fromkeys(self._diffractometerAngleNames, -180.)
        if self._cutAngles.has_key('phi'):
            self._cutAngles['phi'] = 0.
        # 2. Overide with user-specified cuts    
        for name, val in defaultCutsDict.iteritems():
            self.setCut(name, val)
    
    def setCut(self, name, value):
        if self._cutAngles.has_key(name):
            self._cutAngles[name] = value
        else:
            raise KeyError, "Diffractometer has no angle %s. Try: %s." % (name, self._diffractometerAngleNames)

    def getCuts(self):
        return self._cutAngles

    def cutAngles(self, positionArray):
        '''Assumes each angle in positionArray is between -360 and 360
        '''
        cutArray = []
        for name, pos in zip(self._diffractometerAngleNames, positionArray):
            cutAngle = self._cutAngles[name]
            if cutAngle is None:
                cutArray.append(pos)
            else:
                if cutAngle == 0 and (abs(pos-360)<SMALL) or (abs(pos+360)<SMALL) or (abs(pos)<SMALL):
                    pos = 0.
                if pos < (cutAngle-SMALL):
                    cutArray.append(pos + 360.)
                elif pos >= cutAngle + 360. + SMALL:
                    cutArray.append(pos - 360.)
                else:
                    cutArray.append(pos)
        return tuple(cutArray)
    
