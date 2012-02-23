try:
    from gda.device.scannable import ScannableMotionBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.scannable import \
        Scannable as ScannableMotionBase


class MockMotor(ScannableMotionBase):

    def __init__(self, name='mock'):
        self.pos = 0.0
        self._busy = False
        self.name = name

    def asynchronousMoveTo(self, pos):
        self._busy = True
        self.pos = float(pos)

    def getPosition(self):
        return self.pos

    def isBusy(self):
        return self._busy

    def makeNotBusy(self):
        self._busy = False

    def getOutputFormat(self):
        return ['%f']
