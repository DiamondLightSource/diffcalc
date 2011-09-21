class GdaLikeScannable(object):
    # A compatable subset of the gda's Scannable interface.
    
    def isBusy(self):
        raise Exception("Must be overidden. Not needed in minigda yet!")    
    
    def getPosition(self):
        raise Exception("Must be overidden")    
    
    def asynchronousMoveTo(self, newpos):
        raise Exception("Must be overidden")

###

    def __repr__(self):
        pos = self.getPosition()
        formattedValues = self.formatPositionFields(pos)
        if len(tuple(self.getInputNames()) + tuple(self.getExtraNames()))>1:
            result = self.getName() + ': '
        else:
            result = ''
        for name, val in zip(tuple(self.getInputNames()) + tuple(self.getExtraNames()), formattedValues):
            result += name + ': ' + val
        return '< ' +result + ' >'
###

    def formatPositionFields(self, pos):
        """Returns position as array of formatted strings"""
        # Make sure pos is a tuple or list
        if type(pos) not in (tuple, list):
            pos = tuple([pos])
        
        # Sanity check
        if len(pos) != len(self.getOutputFormat()):
            raise Exception("In scannable '%s':number of position fields differs from number format strings specified"%self.getName())
        
        result = []
        for field, format in zip(pos, self.getOutputFormat()):
            if field==None:
                result.append('???')
            else:
                s = (format%field)
##                if width!=None:
##                s = s.ljust(width)
                result.append( s )
        
        return result    

###

    def getName(self):
        return self._name
    def setName(self, value):
        self._name = value

    def getLevel(self):
        return self.__level
    def setLevel(self, value):
        self.__level = value
    
    def getInputNames(self):
        return self.__ioFieldNames    
    def setInputNames(self, value):
        self.__ioFieldNames = value    
    
    def getExtraNames(self):
        try:
            return self.__oFieldNames
        except:
            return []
    def setExtraNames(self, value):
        self.__oFieldNames = value
        
    def getOutputFormat(self):
        return self.__formats    
    def setOutputFormat(self, value):
        if type(value) not in (tuple,list):
            raise TypeError("%s.setOutputFormat() expects tuple or list; not %s"%(self.getName(), str(type(value))) )
        self.__formats = value

    def __call__(self, newpos=None):
        if newpos is None:
            return self.getPosition()
        self.asynchronousMoveTo(newpos)

class Scannable(GdaLikeScannable):
    # For possible extensions to the gda scannable interface
    pass

