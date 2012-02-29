try:
    from gda.device.scannable import ScannableMotionBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import \
        Scannable as ScannableMotionBase


class DiffractionCalculatorParameter(ScannableMotionBase):
    "wraps up the diffractometer motors"

    def __init__(self, name, parameterName, parameter_manager):

        self.parameter_manager = parameter_manager
        self.parameterName = parameterName

        self.setName(name)
        self.setInputNames([parameterName])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(3)

    def asynchronousMoveTo(self, value):
        self.parameter_manager.setParameter(self.parameterName, value)

    def getPosition(self):
        return self.parameter_manager.getParameter(self.parameterName)

    def isBusy(self):
        return False
