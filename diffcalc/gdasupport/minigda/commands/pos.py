from diffcalc.utils import getMessageFromException
from diffcalc.gdasupport.minigda.scannable.scannable import Scannable


class Pos(object):

    def __init__(self, mainNamepaceDict):
        self.mainNamepaceDict = mainNamepaceDict

    def __call__(self, *posargs):
        if len(posargs) == 0:

            keys = self.mainNamepaceDict.keys()
            keys.sort()
            for key in keys:
                val = self.mainNamepaceDict[key]
                if isinstance(val, Scannable):
                    print self.posReturningReport(val)
        else:
            print self.posReturningReport(*posargs)

    def posReturningReport(self, *posargs):
        # report position of this scannable
        if len(posargs) == 1:
            scannable = posargs[0]
            if not isinstance(scannable, Scannable):
                raise TypeError(
                    "The first argument to the pos command must be scannable")
            return self._generatePositionReport(scannable)

        # Move the scannable and report
        elif len(posargs) == 2:
            scannable = posargs[0]
            if not isinstance(scannable, Scannable):
                raise TypeError(
                    "The first argument to the pos command must be scannable.")
            # Move it
            scannable.asynchronousMoveTo(posargs[1])
            # TODO: minigda assumes all moves complete instantly, so no need
            # yet to check the move is complete
            return self._generatePositionReport(scannable)

        else:
            raise ValueError(
                "Invlaid arguements: 'pos [ scannable [ value ] ]'")

    def _generatePositionReport(self, scannable):
        fieldNames = (tuple(scannable.getInputNames()) +
                      tuple(scannable.getExtraNames()))
        # All scannables
        result = "%s:" % scannable.getName()
        result = result.ljust(10)
        try:
            pos = scannable.getPosition()
        except Exception, e:
            return result + "Error: %s" % getMessageFromException(e)
        if pos is None:
            return result + "---"
        # Single field scannable:
        if len(fieldNames) == 1:
            result += "%s" % scannable.formatPositionFields(pos)[0]
        # Multi field scannable:
        else:
            formatted = scannable.formatPositionFields(pos)
            for name, formattedValue in zip(fieldNames, formatted):
                result += "%s: %s " % (name, formattedValue)

        return result
