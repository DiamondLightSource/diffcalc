from diffcalc.hardware.plugin import HardwareMonitorPlugin
from diffcalc.utils import DiffcalcException

class ScannableHardwareMonitorPlugin(HardwareMonitorPlugin):
	
	_name = "DummyHarwdareMonitor"

	def __init__(self, diffractometerScannable, energyScannable, energyScannableMultiplierToGetKeV=1):
		HardwareMonitorPlugin.__init__(self, diffractometerScannable.getInputNames())
		self.diffhw = diffractometerScannable
		self.energyhw = energyScannable
		self.energyScannableMultiplierToGetKeV = energyScannableMultiplierToGetKeV
		
# Required methods

	def getPosition(self):
		"""pos = getDiffractometerPosition() -- returns the current physical diffractometer
		position as a list in degrees
		"""
		return self.diffhw.getPosition()
		
	def getEnergy(self):
		"""energy = getEnergy() -- returns energy in kEv (NOT eV!) """
		energy = self.energyhw.getPosition() * self.energyScannableMultiplierToGetKeV
		if energy is None:
			raise DiffcalcException("Energy has not been set")
		return energy 

	def getWavelength(self):
		"""wavelength = getWavelength() -- returns wavelength in Angstroms   """
		energy = self.getEnergy()
		return 12.39842 / energy
	
	def getDiffHardwareName(self):
		return self.diffhw.getName()

# Limit stuff
# TODO: Override ScannableHardwareMonitorPlugin getLimit methods to know about scannables
