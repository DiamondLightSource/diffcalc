###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

#try:
#    from gda.device import Scannable
#except ImportError:
#    from diffcalc.gdasupport.minigda.scannable import Scannable
from diffcalc.gdasupport.minigda.scannable import Scannable
from diffcalc.util import getMessageFromException
import math
import time


class Pos(object):

    def __init__(self, mainNamepaceDict):
        self.mainNamepaceDict = mainNamepaceDict
        self.__name__ = 'pos'

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
            try:
                result += "%s" % scannable.formatPositionFields(pos)[0]
            except AttributeError:
                result += str(scannable())
        # Multi field scannable:
        else:
            try:
                formatted = scannable.formatPositionFields(pos)
                for name, formattedValue in zip(fieldNames, formatted):
                    result += "%s: %s " % (name, formattedValue)
            except AttributeError:
                result += str(scannable())

        return result


class ScanDataHandler:
    def __init__(self):
        self.scannables = None

    def callAtScanStart(self, scannables):
        pass

    def callWithScanPoint(self, PositionDictIndexedByScannable):
        pass

    def callAtScanEnd(self):
        pass


class ScanDataPrinter(ScanDataHandler):
    def callAtScanStart(self, scannables):
        self.scannables = scannables
        header = ""
        for scn in self.scannables:
            fieldNames = scn.getInputNames() + scn.getExtraNames()
            if len(fieldNames) == 1:
                header += "%s\t" % scn.getName()
            else:
                for fieldName in fieldNames:
                    header += "%s.%s\t" % (scn.getName(), fieldName)
        self.headerWidth = len(header.expandtabs())
        result = (time.asctime(), '\n', '=' * self.headerWidth, '\n', header,
                  '\n', '-' * self.headerWidth)
        print result

    def callWithScanPoint(self, positionDictIndexedByScannable):
        result = ""
        for scn in self.scannables:
            for formattedValue in scn.formatPositionFields(
                positionDictIndexedByScannable[scn]):
                result += formattedValue + '\t'
        print result

    def callAtScanEnd(self):
        print '=' * self.headerWidth


class Scan(object):
    class Group:
        def __init__(self, scannable):
            self.scannable = scannable
            self.args = []

        def __cmp__(self, other):
            return(self.scannable.getLevel() - other.scannable.getLevel())

        def __repr__(self):
            return "Group(%s, %s)" % (self.scannable.getName(), str(self.args))

        def shouldTriggerLoop(self):
            return len(self.args) == 3

    def __init__(self, scanDataHandlers):
        # scanDataHandlers should be list
        if type(scanDataHandlers) not in (tuple, list):
            scanDataHandlers = (scanDataHandlers,)
        self.dataHandlers = scanDataHandlers

    def __call__(self, *scanargs):
        groups = self._parseScanArgsIntoScannableArgGroups(scanargs)
        groups = self._reorderInnerGroupsAccordingToLevel(groups)
        # Configure data handlers for a new scan
        for handler in self.dataHandlers: handler.callAtScanStart(
            [grp.scannable for grp in groups])
        # Perform the scan
        self._performScan(groups, currentRecursionLevel=0)
        # Inform data handlers of scan completion
        for handler in self.dataHandlers: handler.callAtScanEnd()

    def _parseScanArgsIntoScannableArgGroups(self, scanargs):
        """
        -> [ Group(scnA, (a1, a2, a2)), Group((scnB), (b1)), ...
        ... Group((scnC),()), Group((scnD),(d1))]
        """
        result = []
        if not isinstance(scanargs[0], Scannable):
            raise TypeError("First scan argument must be a scannable")

        # Parse out scannables followed by non-scannable args
        for arg in scanargs:
            if isinstance(arg, Scannable):
                result.append(Scan.Group(arg))
            else:
                result[-1].args.append(arg)
        return result

    def _reorderInnerGroupsAccordingToLevel(self, groups):
        # Find the first group not to trigger a loop
        for idx, group in enumerate(groups):
            if not group.shouldTriggerLoop():
                break
        latter = groups[idx:]; latter.sort() # Horrible hack not needed in python 3!
        return groups[:idx] + latter

    def _performScan(self, groups, currentRecursionLevel):
        # groups[currentRecursionLevel:] will start with either:
        #  a) A loop triggering group
        #  b) A number (possibly 0) of non-loop triggering groups
        unprocessedGroups = groups[currentRecursionLevel:]

        # 1) If first remaining group should trigger a loop, perform this loop,
        #    recursively calling this method on the remaining groups
        if len(unprocessedGroups) > 0:
            first = unprocessedGroups[0]
            # If groups starts with a request to loop:
            if first.shouldTriggerLoop():
                posList = self._frange(first.args[0], first.args[1], first.args[2])
                for pos in posList:
                    first.scannable.asynchronousMoveTo(pos)
                    # TODO: Should wait. minigda assumes all moves complete immediately
                    self._performScan(groups, currentRecursionLevel + 1)
                return

        # 2) Move all non-loop triggering groups (may be zero)
        self._moveNonLoopTriggeringGroups(unprocessedGroups)

        # 3) Sample position of all scannables
        posDict = self._samplePositionsOfAllScannables(groups)

        # 4) Inform the data handlers that this point has been recorded
        for handler in self.dataHandlers: handler.callWithScanPoint(posDict)

    def _moveNonLoopTriggeringGroups(self, groups):
        # TODO: Should wait. minigda assumes all moves complete immediately. groups could be zero lengthed.
        for grp in groups:
            if len(grp.args) == 0:
                pass
            elif len(grp.args) == 1:
                grp.scannable.asynchronousMoveTo(grp.args[0])
            elif len(grp.args) == 2:
                raise Exception("Scannables followed by two args not supported by minigda's scan command ")
            else:
                raise Exception("Scannable: %s args%s" % (grp.scannable, str(grp.args)))

    def _samplePositionsOfAllScannables(self, groups):
        posDict = {}
        for grp in groups:
            posDict[grp.scannable] = grp.scannable.getPosition()
        return posDict

    def _frange(self, limit1, limit2, increment):
        """Range function that accepts floats (and integers).
        """
#        limit1 = float(limit1)
#        limit2 = float(limit2)
        increment = float(increment)
        count = int(math.ceil((limit2 - limit1) / increment))
        result = []
        for n in range(count):
            result.append(limit1 + n * increment)
        return result
