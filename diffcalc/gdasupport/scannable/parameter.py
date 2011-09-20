try:
    from gda.device.scannable import PseudoDevice
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.scannable import Scannable as PseudoDevice

class DiffractionCalculatorParameter(PseudoDevice):
    "wraps up the diffractometer motors"
    def __init__(self , name , parameterName, diffcalcObject):

        self.diffcalcObject = diffcalcObject
        self.parameterName = parameterName
                
        self.setName(name)
        self.setInputNames([parameterName])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(3)
    
    def asynchronousMoveTo(self,value):
        self.diffcalcObject._setParameter(self.parameterName, value)
        
    def getPosition(self):
        return self.diffcalcObject._getParameter(self.parameterName)
        
    def isBusy(self):
        return 0
