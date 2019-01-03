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

import time
from diffcalc.util import DiffcalcException

try:
    from gda.device.scannable import ScannableBase, ScannaleMotionBase
except ImportError:
    class Scannable(object):
        pass

    class ScannableBase(Scannable):
        """Implementation of a subset of OpenGDA's Scannable interface
        """
    
        level = 5
        inputNames = []
        extraNames = []
        outputFormat = []
    
        def isBusy(self):
            raise NotImplementedError()
    
        def rawGetPosition(self):
            raise NotImplementedError()
    
        def rawAsynchronousMoveTo(self, newpos):
            raise NotImplementedError()
    
        def waitWhileBusy(self):
            while self.isBusy():
                time.sleep(.1)
    
        def getPosition(self):
            return self.rawGetPosition()
    
        def checkPositionValid(self, externalPosition):
            raise NotImplementedError()
    
        def asynchronousMoveTo(self, newpos):
            self.rawAsynchronousMoveTo(newpos)
    
        def atScanStart(self):
            pass
    
        def atScanEnd(self):
            pass
    
        def atCommandFailure(self):
            pass
    
    ###
    
        def __repr__(self):
            pos = self.getPosition()
            formattedValues = self.formatPositionFields(pos)
            if len(tuple(self.getInputNames()) + tuple(self.getExtraNames())) > 1:
                result = self.getName() + ': '
            else:
                result = ''
    
            names = tuple(self.getInputNames()) + tuple(self.getExtraNames())
            for name, val in zip(names, formattedValues):
                result += ' ' + name + ': ' + val
            return result
    ###
    
        def formatPositionFields(self, pos):
            """Returns position as array of formatted strings"""
            # Make sure pos is a tuple or list
            if type(pos) not in (tuple, list):
                pos = tuple([pos])
    
            # Sanity check
            if len(pos) != len(self.getOutputFormat()):
                raise Exception(
                    "In scannable '%s':number of position fields differs from "
                    "number format strings specified" % self.getName())
    
            result = []
            for field, frmt in zip(pos, self.getOutputFormat()):
                if field is None:
                    result.append('???')
                else:
                    s = (frmt % field)
    ##                if width!=None:
    ##                s = s.ljust(width)
                    result.append(s)
    
            return result
    
        def getName(self):
            return self.name
    
        def setName(self, value):
            self.name = value
    
        def getLevel(self):
            return self.level
    
        def setLevel(self, value):
            self.level = value
    
        def getInputNames(self):
            return self.inputNames
    
        def setInputNames(self, value):
            self.inputNames = value
    
        def getExtraNames(self):
            return self.extraNames
    
        def setExtraNames(self, value):
            self.extraNames = value
    
        def getOutputFormat(self):
            return self.outputFormat
    
        def setOutputFormat(self, value):
            if type(value) not in (tuple, list):
                raise TypeError(
                    "%s.setOutputFormat() expects tuple or list; not %s" %
                    (self.getName(), str(type(value))))
            self.outputFormat = value
    
        def __call__(self, newpos=None):
            if newpos is None:
                return self.getPosition()
            self.asynchronousMoveTo(newpos)


    class ScannableLimitsComponent(object):

        def __init__(self):
            # Array of lower limits (one for each input name). Null if no limits set. Any value within array may be null if
            # that input has no corresponding limit.
            self.internalLowerLim = None

            # Array of upper limits (one for each input name). Null if no limits set. Any value within array may be null if
            # that input has no corresponding limit.
            self.internalUpperLim = None

            self.hostScannable = None
            self.limitType = "Scannable"

        def getInternalLower(self):
            return self.internalLowerLim

        def getInternalUpper(self):
            return self.internalUpperLim

        def checkInternalPosition(self, internalPosition):

            # If neither limits are set, return null indicating okay.
            if self.internalLowerLim is None and self.internalUpperLim is None:
                return None

            # Check lower limits if set
            if self.internalLowerLim:
                for i, (lim, pos) in enumerate(zip(self.internalLowerLim, internalPosition)):
                    if pos < lim:
                        fieldName = "{}.{}".format(self.getHostScannable().getName(), self.getHostScannable().getInputNames()[i])
                        return "{} limit violation on {}: {} < {} (internal/hardware/dial values).".format(
                                                                self.limitType, fieldName, pos, lim)

            # Check upper limits if set
            if self.internalUpperLim:
                for i, (lim, pos) in enumerate(zip(self.internalUpperLim, internalPosition)):
                    if pos > lim:
                        fieldName = "{}.{}".format(self.getHostScannable().getName(), self.getHostScannable().getInputNames()[i])
                        return "{} limit violation on {}: {} > {} (internal/hardware/dial values).".format(
                                                                self.limitType, fieldName, pos, lim)
            return None

        def checkPositionLength(self, positionArray):
            if len(positionArray) != len(self.getHostScannable().getInputNames()):
                raise DiffcalcException(
                    "Expected position of length {} but got position of length {}".format(len(self.getHostScannable().getInputNames().length),
                                                                                          len(positionArray)))

        def setInternalUpper(self, internalUpperLim, index=None, length=None):
            if index is not None:
                if not self.internalUpperLim:
                    self.internalUpperLim = [None] * length
                self.internalUpperLim[index] = internalUpperLim
            else:
                if internalUpperLim:
                    self.checkPositionLength(internalUpperLim)
                self.internalUpperLim = internalUpperLim

        def setInternalLower(self, internalLowerLim, index=None, length=None):
            if index is not None:
                if not self.internalLowerLim:
                    self.internalLowerLim = [None] * length
                self.internalLowerLim[index] = internalLowerLim
            else:
                if internalLowerLim:
                    self.checkPositionLength(internalLowerLim)
                self.internalLowerLim = internalLowerLim

        def setHostScannable(self, hostScannable):
            self.hostScannable = hostScannable

        def getHostScannable(self):
            return self.hostScannable


    class ScannableMotionBase(ScannableBase):
        """Implementation of a subset of OpenGDA's ScannableMotion interface
        """

        def __init__(self):
            self.limitsComponent = ScannableLimitsComponent()
            self.limitsComponent.setHostScannable(self)

        def asynchronousMoveTo(self, newpos):
            report = self.checkPositionValid([newpos,])
            if report:
                raise DiffcalcException(report)
            ScannableBase.asynchronousMoveTo(self, newpos)

        def checkPositionValid(self, externalPosition):
            limitsComponentMsg = self.limitsComponent.checkInternalPosition(externalPosition)
            if limitsComponentMsg:
                return limitsComponentMsg
            return None

        def getLowerInnerLimit(self):
            limits = self.limitsComponent.getInternalLower()
            try:
                return limits[0]
            except TypeError:
                return None

        def getUpperInnerLimit(self):
            limits = self.limitsComponent.getInternalUpper()
            try:
                return limits[0]
            except TypeError:
                return None


    class ScannableAdapter(Scannable):
        '''Wrap up a Scannable and give it a new name and optionally an offset
        (added to the delegate when reading up and subtracting when setting down
        '''
        
        def __init__(self, delegate_scn, name, offset=0):
            assert len(delegate_scn.getInputNames()) == 1
            assert len(delegate_scn.getExtraNames()) == 0
            self.delegate_scn = delegate_scn
            self.name = name
            self.offset = offset
                   
        def __getattr__(self, name):
            return getattr(self.delegate_scn, name)
        
        def getName(self):
            return self.name
        
        def getInputNames(self):
            return [self.name]
        
        def getPosition(self):
            return self.delegate_scn.getPosition() + self.offset
        
        def asynchronousMoveTo(self, newpos):
            self.delegate_scn.asynchronousMoveTo(newpos - self.offset)
            
        def __repr__(self):
            pos = self.getPosition()
            formatted_values = self.delegate_scn.formatPositionFields(pos)  
            return self.name + ': ' + formatted_values[0] + ' ' + self.get_hint()
        
        def get_hint(self):
            if self.offset:
                offset_hint = ' + ' if self.offset >= 0 else ' - '
                offset_hint += str(self.offset)
            else:
                offset_hint = ''
            return '(%s%s)' % (self.delegate_scn.name, offset_hint)
        
        def __call__(self, newpos=None):
            if newpos is None:
                return self.getPosition()
            self.asynchronousMoveTo(newpos)


class SingleFieldDummyScannable(ScannableMotionBase):

    def __init__(self, name, initial_position=0.):
        ScannableMotionBase.__init__(self)
        self.name = name
        self.inputNames = [name,]
        self.outputFormat = ['% 6.4f',]
        self.level = 3
        self._current_position = float(initial_position)

    def isBusy(self):
        return False

    def waitWhileBusy(self):
        return

    def asynchronousMoveTo(self, new_position):
        report = self.checkPositionValid([new_position,])
        if report:
            raise DiffcalcException(report)
        self._current_position = float(new_position)

    def getPosition(self):
        return self._current_position

    def setLowerDummyLimit(self, lowLimit):
        self.limitsComponent.setInternalLower(lowLimit, 0, len(self.getInputNames()))
        
    def setUpperDummyLimit(self, upperLimit):
        self.limitsComponent.setInternalUpper(upperLimit, 0, len(self.getInputNames()))


class DummyPD(SingleFieldDummyScannable):
    """For compatability with the gda's dummy_pd module"""
    pass


class MultiInputExtraFieldsDummyScannable(ScannableMotionBase):
    '''Multi input Dummy PD Class supporting input and extra fields'''
    def __init__(self, name, inputNames, extraNames):
        ScannableMotionBase.__init__(self)
        self.setName(name)
        self.setInputNames(inputNames)
        self.setExtraNames(extraNames)
        self.setOutputFormat(['%6.4f'] * (len(inputNames) + len(extraNames)))
        self.setLevel(3)
        self.currentposition = [0.0] * len(inputNames)

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self, new_position):
        if type(new_position) == type(1) or type(new_position) == type(1.0):
            new_position = [new_position]
            msg = "Wrong new_position size"
        assert len(new_position) == len(self.currentposition), msg
        for i in range(len(new_position)):
            if new_position[i] != None:
                self.currentposition[i] = float(new_position[i])

    def getPosition(self):
        extraValues = range(100, 100 + (len(self.getExtraNames())))
        return self.currentposition + map(float, extraValues)


class ZeroInputExtraFieldsDummyScannable(ScannableMotionBase):
    '''Zero input/extra field dummy pd
    '''
    def __init__(self, name):
        ScannableMotionBase.__init__(self)
        self.setName(name)
        self.setInputNames([])
        self.setOutputFormat([])

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self, new_position):
        pass

    def getPosition(self):
        pass


class ScannableGroup(ScannableBase):
    """wraps up motors. Simulates motors if non given."""

    def __init__(self, name, motorList):

        self.setName(name)
        # Set input format
        motorNames = []
        for scn in motorList:
            motorNames.append(scn.getName())
        self.setInputNames(motorNames)
        # Set output format
        frmt = []
        for motor in motorList:
            frmt.append(motor.getOutputFormat()[0])
        self.setOutputFormat(frmt)
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

    def getGroupMembers(self):
        return self.__motors

    def getGroupMember(self, name):
        for scn in self.__motors:
            if scn.getName() == name:
                return scn
        return None

    def isBusy(self):
        for scn in self.__motors:
            if scn.isBusy():
                return True
        return False

    def configure(self):
        pass

    def checkPositionValid(self, positionArray):

        msg = "Wrong position array size for scannable group"
        assert len(self.__motors) == len(positionArray), msg
        
        for motor, pos in zip(self.__motors, positionArray):
            reason = motor.checkPositionValid([pos,])
            if reason:
                return reason
        return None


class ScannableMotionWithScannableFieldsBase(ScannableMotionBase):
    '''
    This extended version of ScannableMotionBase contains a
    completeInstantiation() method which adds a dictionary of
    MotionScannableParts to an instance. Each part allows one of the
    instances fields to be interacted with like it itself is a scannable.
    Fields are dynamically added to the instance linking to these parts
    allowing dotted access from Jython.  They may also be accessed using
    Jython container access methods (via the __getitem__() method). To acess
    them from Jave use the getComponent(name) method.

    When moving a part (via either a pos or scan command), the part calls
    the parent to perform the actual task.  The parts asynchronousMoveto
    command will call the parent with a list of None values except for the
    field it represents which will be passed the desired position value.

    The asynchronousMoveTo method in class that inherats from this base
    class then must handle these Nones.  In some cases the method may
    actually be able to move the underlying system assoiciated with one
    field individually from others. If this is not possible the best
    behaviour may be to simply not support this beahviour and exception or
    alternatively to substitute the None values with actual current position
    of parent's scannables associated fields.

    ScannableMotionBaseWithMemory() inherats from this calss and provides a
    solution useful for some scenarious: it keeps track of the last position
    moved to, and replaces the Nones in an asynchronousMoveTo request with
    these values. There are a number of dangers associated with this which
    are addressed in that class's documentation, but it provides a way to
    move one axis within a group of non-orthogonal axis while keeping the
    others still.
    '''
    childrenDict = {}
    numInputFields = None
    numExtraFields = None

    def completeInstantiation(self):
        '''This method should be called at the end of all user defined
        consructors'''
        # self.validate()
        self.numInputFields = len(self.getInputNames())
        self.numExtraFields = len(self.getExtraNames())
        self.addScannableParts()
        self.autoCompletePartialMoveToTargets = False
        self.positionAtScanStart = None

    def setAutoCompletePartialMoveToTargets(self, b):
        self.autoCompletePartialMoveToTargets = b

    def atScanStart(self):
        self.positionAtScanStart = self.getPosition()

    def atCommandFailure(self):
        self.positionAtScanStart = None

    def atScanEnd(self):
        self.positionAtScanStart = None

###

    def __repr__(self):
        pos = self.getPosition()
        formattedValues = self.formatPositionFields(pos)
        if len(tuple(self.getInputNames()) + tuple(self.getExtraNames())) > 1:
            result = self.getName() + ': '
        else:
            result = ''

        names = tuple(self.getInputNames()) + tuple(self.getExtraNames())
        for name, val in zip(names, formattedValues):
            result += ' ' + name + ': ' + val
        return result
###

    def formatPositionFields(self, pos):
        """Returns position as array of formatted strings"""
        # Make sure pos is a tuple or list
        if type(pos) not in (tuple, list):
            pos = tuple([pos])

        # Sanity check
        if len(pos) != len(self.getOutputFormat()):
            raise Exception(
                "In scannable '%s':number of position fields differs from "
                "number format strings specified" % self.getName())

        result = []
        for field, frmt in zip(pos, self.getOutputFormat()):
            if field is None:
                result.append('???')
            else:
                s = (frmt % field)
##                if width!=None:
##                s = s.ljust(width)
                result.append(s)

        return result

###
    
    def addScannableParts(self):
        '''
        Creates an array of MotionScannableParts each of which allows access to
        the scannable's fields. See this class's documentation for more info.
        '''
        self.childrenDict = {}
        # Add parts to access the input fields
        for index in range(len(self.getInputNames())):
            scannableName = self.getInputNames()[index]
            self.childrenDict[scannableName] = self.MotionScannablePart(
                scannableName, index, self, isInputField=1)

        # Add parts to access the extra fields
        for index in range(len(self.getExtraNames())):
            scannableName = self.getExtraNames()[index]
            self.childrenDict[scannableName] = self.MotionScannablePart(
                scannableName, index + len(self.getInputNames()),
                self, isInputField=0)

    def asynchronousMoveTo(self, newpos):
        if self.autoCompletePartialMoveToTargets:
            newpos = self.completePosition(newpos)
        ScannableBase.asynchronousMoveTo(self, newpos)

    def completePosition(self, position):
        '''
        If position contains any null or None values, these are replaced with
        the corresponding fields from the scannables current position and then
        returned.'''
        # Just return position if it does not need padding
        if None not in position:
            return position
        if self.positionAtScanStart is not None:
            basePosition = self.positionAtScanStart
        else:
            basePosition = self.getPosition()[:self.numInputFields]
        for i in range(self.numInputFields):
            if position[i] is None:
                position[i] = basePosition[i]
        return position

    def __getattr__(self, name):
        try:
            return self.childrenDict[name]
        except:
            raise AttributeError("No child named:" + name)

    def __getitem__(self, key):
        '''Provides container like access from Jython'''
        return self.childrenDict[key]

    def getPart(self, name):
        '''Returns the a compnent scannable'''
        return self.childrenDict[name]

    class MotionScannablePart(ScannableMotionBase):
        '''
        A scannable to be placed in the parent's childrenDict that allows
        access to the parent's individual fields.'''

        def __init__(self, scannableName, index, parentScannable,
                     isInputField):
            ScannableMotionBase.__init__(self)
            self.setName(scannableName)
            if isInputField:
                self.setInputNames([scannableName])
            else:
                self.setExtraNames([scannableName])
            self.index = index
            self.parentScannable = parentScannable
            self.setOutputFormat(
                [self.parentScannable.getOutputFormat()[index]])

        def getParent(self):
            return self.parentScannable

        def isBusy(self):
            return self.parentScannable.isBusy()

        def asynchronousMoveTo(self, new_position):
            if self.parentScannable.isBusy():
                raise Exception(
                    self.parentScannable.getName() + "." + self.getName() +
                    " cannot be moved because " +
                    self.parentScannable.getName() + " is already moving")

            toMoveTo = [None] * len(self.parentScannable.getInputNames())
            toMoveTo[self.index] = new_position
            self.parentScannable.asynchronousMoveTo(toMoveTo)
            
        def moveTo(self, new_position):
            self.asynchronousMoveTo(new_position)
            self.waitWhileBusy()

        def getPosition(self):
            return self.parentScannable.getPosition()[self.index]

        def getLowerGdaLimits(self):
            limit = self.parentScannable.getLowerGdaLimits()
            return None if limit is None else [limit[self.index]]

        def getUpperGdaLimits(self):
            limit = self.parentScannable.getUpperGdaLimits()
            return None if limit is None else [limit[self.index]]

        def setLowerGdaLimits(self, lowerLim):
            try:
                if len(lowerLim) != 1:
                    raise DiffcalcException("Could not setLowerGdaLmits() on scannable {} to {}. This scannable has only one field.".format(
                        self.getName(), str(lowerLim)))
                lowerLimValue = lowerLim[0]
            except TypeError:
                lowerLimValue = lowerLim
            limit = self.parentScannable.getLowerGdaLimits()
            if not limit:
                limit = [None] * len(self.parentScannable.getInputNames())
            limit[self.index] = lowerLimValue
            self.parentScannable.setLowerGdaLimits(limit)

        def setUpperGdaLimits(self, upperLim):
            try:
                if len(upperLim) != 1:
                    raise DiffcalcException("Could not setUpperGdaLmits() on scannable {} to {}. This scannable has only one field.".format(
                        self.getName(), str(upperLim)))
                upperLimValue = upperLim[0]
            except TypeError:
                upperLimValue = upperLim
            limit = self.parentScannable.getUpperGdaLimits()
            if not limit:
                limit = [None] * len(self.parentScannable.getInputNames())
            limit[self.index] = upperLimValue
            self.parentScannable.setUpperGdaLimits(limit)

        def __str__(self):
            return self.__repr__()

        def __repr__(self):
            # Get the name of this field
            # (assume its an input field first and correct if wrong)
            name = self.getInputNames()[0]

            if name == 'value':
                name = self.getExtraNames()[0]
            parentName = self.parentScannable.getName()
            return parentName + "." + name + " : " + str(self.getPosition())
