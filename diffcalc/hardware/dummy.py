from diffcalc.hardware.plugin import HardwareMonitorPlugin
from diffcalc.utils import DiffcalcException


class DummyHardwareMonitorPlugin(HardwareMonitorPlugin):

    _name = "DummyHarwdareMonitor"

    def __init__(self, diffractometerAngleNames):
        HardwareMonitorPlugin.__init__(self, diffractometerAngleNames)

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
