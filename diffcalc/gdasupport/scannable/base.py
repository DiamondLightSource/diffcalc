try:
    from gda.device.scannable import PseudoDevice
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.scannable import \
        Scannable as PseudoDevice


class ScannableGroup(PseudoDevice):

    def __init__(self, name, motorList):

        self.setName(name)
        # Set input format
        motorNames = []
        for scn in motorList:
            motorNames.append(scn.getName())
        self.setInputNames(motorNames)
        # Set output format
        format = []
        for motor in motorList:
            format.append(motor.getOutputFormat()[0])
        self.setOutputFormat(format)
        self.__motors = motorList

    def asynchronousMoveTo(self, position):
        # if input has any Nones, then replace these with the current positions
        if None in position:
            position = list(position)
            current = self.getPosition()
            for idx, val in enumerate(position):
                if val is None:
                    position[idx] = current[idx]

        for scn, pos in zip(self.__motors, position):
            scn.asynchronousMoveTo(pos)

    def getPosition(self):
        return [scn.getPosition() for scn in self.__motors]

    def isBusy(self):
        for scn in self.__motors:
            if scn.isBusy():
                return True
        return False
