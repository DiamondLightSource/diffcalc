class GdaLikeScannable(object):
    # A compatable subset of the gda's Scannable interface.
    
    def isBusy(self):
        raise Exception("Must be overidden. Not needed in minigda yet!")    
    
    def getPosition(self):
        return self.rawGetPosition()   
    
    def asynchronousMoveTo(self, newpos):
        self.rawAsynchronousMoveTo(newpos)
    
    def rawGetPosition(self):
        raise Exception("Must be overidden")    
    
    def rawAsynchronousMoveTo(self, newpos):
        raise Exception("Must be overidden")
    
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
        for name, val in zip(tuple(self.getInputNames()) + tuple(self.getExtraNames()), formattedValues):
            result += name + ': ' + val
        return '< ' + result + ' >'
###

    def formatPositionFields(self, pos):
        """Returns position as array of formatted strings"""
        # Make sure pos is a tuple or list
        if type(pos) not in (tuple, list):
            pos = tuple([pos])
        
        # Sanity check
        if len(pos) != len(self.getOutputFormat()):
            raise Exception("In scannable '%s':number of position fields differs from number format strings specified" % self.getName())
        
        result = []
        for field, format in zip(pos, self.getOutputFormat()):
            if field == None:
                result.append('???')
            else:
                s = (format % field)
##                if width!=None:
##                s = s.ljust(width)
                result.append(s)
        
        return result    

###

    def getName(self):
        return self.name
    
    def setName(self, value):
        self.name = value

    def getLevel(self):
        return self._level
    
    def setLevel(self, value):
        self._level = value
    
    def getInputNames(self):
        return self._ioFieldNames 
       
    def setInputNames(self, value):
        self._ioFieldNames = value    
    
    def getExtraNames(self):
        try:
            return self._oFieldNames
        except:
            return []
        
    def setExtraNames(self, value):
        self._oFieldNames = value
        
    def getOutputFormat(self):
        return self._formats 
       
    def setOutputFormat(self, value):
        if type(value) not in (tuple, list):
            raise TypeError("%s.setOutputFormat() expects tuple or list; not %s" % (self.getName(), str(type(value))))
        self._formats = value

    def __call__(self, newpos=None):
        if newpos is None:
            return self.getPosition()
        self.asynchronousMoveTo(newpos)

class Scannable(GdaLikeScannable):
    # For possible extensions to the gda scannable interface
    pass

