SMALL = 1e-8


class HardwareMonitorPlugin(object):

    _name = "BaseHarwdareMonitor"

    def __init__(self, diffractometerAngleNames, defaultCuts={},
                 energyScannableMultiplierToGetKeV=1):

        self._diffractometerAngleNames = diffractometerAngleNames
        self._upperLimitDict = {}
        self._lowerLimitDict = {}
        self._cutAngles = {}
        self._configureCuts(defaultCuts)
        self.energyScannableMultiplierToGetKeV = \
            energyScannableMultiplierToGetKeV

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
        return 12.39842 / self.getEnergy()

    def getEnergy(self):
        """energy = getEnergy() -- returns energy in kEv  """
        #### Overide me ###
        raise Exception("Abstract")

    def getDiffHardwareName(self):
        return 'base'

    def __str__(self):
        s = self._name + ":\n"
        s += "  energy : " + str(self.getEnergy()) + " keV\n"
        s += "  wavelength : " + str(self.getWavelength()) + " Angstrom\n"
        names = self._diffractometerAngleNames
        for name, pos in zip(names, self.getPosition()):
            s += "  %s : %r deg\n" % (name, pos)
        return s

    def __repr__(self):
        return self.__str__()

    def getPositionByName(self, angleName):
        names = list(self._diffractometerAngleNames)
        return self.getPosition()[names.index(angleName)]

### Limits ###

    def getLowerLimit(self, name):
        '''returns lower limits by axis name. Limit may be None if not set
        '''
        if name not in self._diffractometerAngleNames:
            raise ValueError("No angle called %s. Try one of: %s" %
                             (name, self._diffractometerAngleNames))
        return self._lowerLimitDict.get(name)

    def getUpperLimit(self, name):
        '''returns upper limit by axis name. Limit may be None if not set
        '''
        if name not in self._diffractometerAngleNames:
            raise ValueError("No angle called %s. Try one of: %s" %
                             name, self._diffractometerAngleNames)
        return self._upperLimitDict.get(name)

    def setLowerLimit(self, name, value):
        """value may be None to remove limit"""
        if name not in self._diffractometerAngleNames:
            raise ValueError(
                "Cannot set lower Diffcalc limit: No angle called %s. Try one "
                "of: %s" % (name, self._diffractometerAngleNames))
        if value is None:
            try:
                del self._lowerLimitDict[name]
            except KeyError:
                print ("WARNING: There was no lower Diffcalc limit %s set to "
                       "clear" % name)
        else:
            self._lowerLimitDict[name] = value

    def setUpperLimit(self, name, value):
        """value may be None to remove limit"""
        if name not in self._diffractometerAngleNames:
            raise ValueError(
                "Cannot set upper Diffcalc limit: No angle called %s. Try one "
                "of: %s" % (name, self._diffractometerAngleNames))
        if value is None:
            try:
                del self._upperLimitDict[name]
            except KeyError:
                print ("WARNING: There was no upper Diffcalc limit %s set to "
                       "clear" % name)
        else:
            self._upperLimitDict[name] = value

    def isPositionWithinLimits(self, positionArray):
        """
        where position array is in degrees and cut to be between -180 and 180
        """
        names = self._diffractometerAngleNames
        for axis_name, value in zip(names, positionArray):
            if not self.isAxisValueWithinLimits(axis_name, value):
                return False
        return True

    def isAxisValueWithinLimits(self, axis_name, value):
        if axis_name in self._upperLimitDict:
            if value > self._upperLimitDict[axis_name]:
                return False
        if axis_name in self._lowerLimitDict:
            if value < self._lowerLimitDict[axis_name]:
                return False
        return True

    def reprSectorLimitsAndCuts(self, name=None):
        if name is None:
            s = 'Cuts and Sector-limits:\n'
            for name in self.getPhysicalAngleNames():
                s += self.reprSectorLimitsAndCuts(name) + '\n'
            s += "  Note: When auto sector/transforms are used, "
            s += "cuts are applied before checking limits."
            return s
        # limits:
        low = self.getLowerLimit(name)
        high = self.getUpperLimit(name)
        s = '  '
        if low is not None:
            s += "%f <= " % low
        s += name
        if high is not None:
            s += " <= %f" % high
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
        if 'phi' in self._cutAngles:
            self._cutAngles['phi'] = 0.
        # 2. Overide with user-specified cuts
        for name, val in defaultCutsDict.iteritems():
            self.setCut(name, val)

    def setCut(self, name, value):
        if name in self._cutAngles:
            self._cutAngles[name] = value
        else:
            raise KeyError("Diffractometer has no angle %s. Try: %s." %
                            (name, self._diffractometerAngleNames))

    def getCuts(self):
        return self._cutAngles

    def cutAngles(self, positionArray):
        '''Assumes each angle in positionArray is between -360 and 360
        '''
        cutArray = []
        names = self._diffractometerAngleNames
        for axis_name, value in zip(names, positionArray):
            cutArray.append(self.cutAngle(axis_name, value))
        return tuple(cutArray)

    def cutAngle(self, axis_name, value):
        cut_angle = self._cutAngles[axis_name]
        if cut_angle is None:
            return value
        return cut_angle_at(cut_angle, value)


def cut_angle_at(cut_angle, value):
    if (cut_angle == 0 and (abs(value - 360) < SMALL) or
        (abs(value + 360) < SMALL) or
        (abs(value) < SMALL)):
        value = 0.
    if value < (cut_angle - SMALL):
        return value + 360.
    elif value >= cut_angle + 360. + SMALL:
        return value - 360.
    else:
        return value
