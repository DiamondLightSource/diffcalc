from diffcalc.gdasupport.minigda.scannable.scannable import \
    Scannable as PseudoDevice


class ScannableGroup(PseudoDevice):
    """wraps up motors. Simulates motors if non given."""

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

    def configure(self):
        pass


class ScannableMotionWithScannableFieldsBase(PseudoDevice):
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
        PseudoDevice.asynchronousMoveTo(self, newpos)

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

    class MotionScannablePart(PseudoDevice):
        '''
        A scannable to be placed in the parent's childrenDict that allows
        access to the parent's individual fields.'''

        def __init__(self, scannableName, index, parentScannable,
                     isInputField):
            self.setName(scannableName)
            if isInputField:
                self.setInputNames([scannableName])
            else:
                self.setExtraNames([scannableName])
            self.index = index
            self.parentScannable = parentScannable
            self.setOutputFormat(
                [self.parentScannable.getOutputFormat()[index]])

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

        def getPosition(self):
            return self.parentScannable.getPosition()[self.index]

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
