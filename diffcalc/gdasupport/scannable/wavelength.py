try:
    from gdascripts.pd.dummy_pds import DummyPD
except ImportError:
    print "WARNING: ExampleSixCircleStartup.py is not running within the GDA: falling back to the (very minimal!) minigda..."
    from diffcalc.gdasupport.minigda.scannable.dummy import DummyPD

class Wavelength(DummyPD):
    def __init__(self, name, energyScannable, energyScannableMultiplierToGetKeV = 1):
        self.energyScannable = energyScannable
        self.energyScannableMultiplierToGetKeV = energyScannableMultiplierToGetKeV
        
        DummyPD.__init__(self, name)
        
    def asynchronousMoveTo(self,pos):
        self.energyScannable.asynchronousMoveTo((12.39842/pos)/self.energyScannableMultiplierToGetKeV)
        
    def getPosition(self):
        return 12.39842/(self.energyScannable.getPosition()*self.energyScannableMultiplierToGetKeV)
    
    def isBusy(self):
        return self.energyScannable.isBusy()
    
