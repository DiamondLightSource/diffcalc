from diffcalc.utils import DiffcalcException

SMALL = 1e-8

from diffcalc.utils import command


def getNameFromScannableOrString(o):
        try:  # it may be a scannable
            return o.getName()
        except AttributeError:
            return str(o)


class HardwareCommands(object):

    def __init__(self, hardware):
        self._hardware = hardware
        self.commands = ['Hardware',
                         self.hardware,
                         self.setcut,
                         self.setmin,
                         self.setmax]

    @command
    def hardware(self):
        """hardware  -- show diffcalc limits and cuts"""
        print self._hardware.reprSectorLimitsAndCuts()

    @command
    def setcut(self, scannable_or_string=None, val=None):
        """setcut {axis_scannable {val}} -- sets cut angle
        setcut {name {val}} -- sets cut angle
        """
        if scannable_or_string is None and val is None:
            print self._hardware.reprSectorLimitsAndCuts()
        else:
            name = getNameFromScannableOrString(scannable_or_string)
            if val is None:
                print '%s: %f' % (name, self._hardware.getCuts()[name])
            else:
                oldcut = self._hardware.getCuts()[name]
                self._hardware.setCut(name, float(val))
                newcut = self._hardware.getCuts()[name]
                print '%s: %f --> %f' % (name, oldcut, newcut)

    @command
    def setmin(self, name=None, val=None):
        """setmin {axis {val}} -- set lower limits used by auto sector code (None to clear)""" #@IgnorePep8
        self._setMinOrMax(name, val, self._hardware.setLowerLimit)

    @command
    def setmax(self, name=None, val=None):
        """setmax {name {val}} -- sets upper limits used by auto sector code (None to clear)""" #@IgnorePep8
        self._setMinOrMax(name, val, self._hardware.setUpperLimit)

    def _setMinOrMax(self, name, val, setMethod):
        if name is None:
            print self._hardware.reprSectorLimitsAndCuts()
        else:
            name = getNameFromScannableOrString(name)
            if val is None:
                print self.reprSectorLimitsAndCuts(name)
            else:
                setMethod(name, float(val))


class HardwareAdapter(object):

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
        raise NotImplementedError()

    def getWavelength(self):
        """wavelength = getWavelength() -- returns wavelength in Angstroms
        """
        return 12.39842 / self.getEnergy()

    def getEnergy(self):
        """energy = getEnergy() -- returns energy in kEv  """
        raise NotImplementedError()

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


class DummyHardwareAdapter(HardwareAdapter):

    _name = "DummyHarwdareMonitor"

    def __init__(self, diffractometerAngleNames):
        HardwareAdapter.__init__(self, diffractometerAngleNames)

        self.diffractometerAngles = [0.] * len(diffractometerAngleNames)
        self.wavelength = 1.
        self.energy = 12.39842 / self.wavelength
        self.energyScannableMultiplierToGetKeV = 1

# Required methods

    def getPosition(self):
        """
        pos = getDiffractometerPosition() -- returns the current physical
        diffractometer position as a list in degrees
        """
        return self.diffractometerAngles

    def getEnergy(self):
        """energy = getEnergy() -- returns energy in kEv  """
        if self.energy is None:
            raise DiffcalcException(
                "Energy has not been set in DummySoftwareMonitor")
        return self.energy * self.energyScannableMultiplierToGetKeV

    def getWavelength(self):
        """wavelength = getWavelength() -- returns wavelength in Angstroms"""
        if self.energy is None:
            raise DiffcalcException(
                "Energy has not been set in DummySoftwareMonitor")
        return self.wavelength

    def getDiffHardwareName(self):
        return 'dummy'

# Dummy implementation methods

    def setPosition(self, pos):
        assert len(pos) == len(self.getPhysicalAngleNames()), \
            "Wrong length of input list"
        self.diffractometerAngles = pos

    def setEnergy(self, energy):
        self.energy = energy
        self.wavelength = 12.39842 / energy

    def setWavelength(self, wavelength):
        self.wavelength = wavelength
        self.energy = 12.39842 / wavelength


class ScannableHardwareAdapter(HardwareAdapter):

    _name = "DummyHarwdareMonitor"

    def __init__(self, diffractometerScannable, energyScannable,
                 energyScannableMultiplierToGetKeV=1):
        input_names = diffractometerScannable.getInputNames()
        HardwareAdapter.__init__(self, input_names)
        self.diffhw = diffractometerScannable
        self.energyhw = energyScannable
        self.energyScannableMultiplierToGetKeV = \
            energyScannableMultiplierToGetKeV

# Required methods

    def getPosition(self):
        """
        pos = getDiffractometerPosition() -- returns the current physical
        diffractometer position as a list in degrees
        """
        return self.diffhw.getPosition()

    def getEnergy(self):
        """energy = getEnergy() -- returns energy in kEv (NOT eV!) """
        multiplier = self.energyScannableMultiplierToGetKeV
        energy = self.energyhw.getPosition() * multiplier
        if energy is None:
            raise DiffcalcException("Energy has not been set")
        return energy

    def getWavelength(self):
        """wavelength = getWavelength() -- returns wavelength in Angstroms"""
        energy = self.getEnergy()
        return 12.39842 / energy

    def getDiffHardwareName(self):
        return self.diffhw.getName()
