from diffcalc.utils import DiffcalcException
class Mode:
    def __init__(self, index, name, group, description, parameterNames, implemented=True):
        self.index = index
        self.group = group
        self.name = name
        self.description = description
        self.parameterNames = parameterNames # a list of strings describing parameters are used in this mode
        self.implemented = implemented
    
    def __repr__(self):
        return "%i) %s" % (self.index, self.description)

    def __str__(self):
        return self.__repr__()

    def usesParameter(self,name):
        return name in self.parameterNames
    

class ModeSelector(object):
    
    def __init__(self, geometry, parameterManager=None, gammaParameterName = 'gamma'):
        self.parameter_manager = parameterManager
        self._geometry = geometry
        self._gammaParameterName = gammaParameterName
        self._modelist = {} # indexed by non-contiguous mode number
        self._configureAvailableModes()     
        self._selectedIndex = 1
        
    def setParameterManager(self, manager):
        """Required as a ParameterManager and ModelSelector are mutually tied together in practice
        """
        self.parameter_manager = manager
        
    def _configureAvailableModes(self):        
        #                             name,        group        description                         parameters)
        gammaName = self._gammaParameterName
        self._modelist[0] =  Mode( 0, '4cFixedw', 'fourc',    'fourc fixed-bandlw',    ['alpha',gammaName, 'blw'], False)
        
        self._modelist[1] =  Mode( 1, '4cBeq',    'fourc',    'fourc bisecting',    ['alpha',gammaName])
        self._modelist[2] =  Mode( 2, '4cBin',    'fourc',    'fourc incoming',    ['alpha',gammaName, 'betain'])
        self._modelist[3] =  Mode( 3, '4cBout',   'fourc',    'fourc outgoing',    ['alpha',gammaName, 'betaout'])
        self._modelist[4] =  Mode( 4, '4cAzimuth','fourc',    'fourc azimuth',    ['alpha',gammaName, 'azimuth'], False) 
        self._modelist[5] =  Mode( 5, '4cPhi',    'fourc',    'fourc fixed-phi',    ['alpha',gammaName,'phi'])
        
        self._modelist[10] = Mode(10, '5cgBeq',   'fivecFixedGamma',    'fivec bisecting',    [gammaName])
        self._modelist[11] = Mode(11, '5cgBin',   'fivecFixedGamma',    'fivec incoming',    [gammaName, 'betain'])
        self._modelist[12] = Mode(12, '5cgBout',  'fivecFixedGamma',    'fivec outgoing',    [gammaName, 'betaout'])
        
        self._modelist[13] = Mode(13, '5caBeq',   'fivecFixedAlpha',    'fivec bisecting',    ['alpha'])
        self._modelist[14] = Mode(14, '5caBin',   'fivecFixedAlpha',    'fivec incoming',    ['alpha', 'betain'])
        self._modelist[15] = Mode(15, '5caBout',  'fivecFixedAlpha',    'fivec outgoing',    ['alpha', 'betaout'])
        
        self._modelist[20] = Mode(20, '6czBeq',   'zaxis',    'zaxis bisecting',    [])
        self._modelist[21] = Mode(21, '6czBin',   'zaxis',    'zaxis incoming',    ['betain'])
        self._modelist[22] = Mode(22, '6czBout',  'zaxis',    'zaxiz outgoing',    ['betaout'])
    
    def setModeByIndex(self, index):
        if self._modelist.has_key(index):
            self._selectedIndex = index   
        else:
            raise DiffcalcException("mode %s is not defined" % `index`)    
    
    def setModeByName(self, name):
        def findModeWithName(name):
            for index, mode in self._modelist.items():
                if mode.name == name:
                    return index, mode
            raise ValueError
        
        try:
            index, mode = findModeWithName(name)
        except ValueError:
            raise DiffcalcException('Unknown mode. The diffraction calculator supports these modeSelector: %s' % self._supportedModes.keys() ) 
        if  self._geometry.supportsModeGroup(mode.group):
            self._selectedIndex = index
        else:
            raise DiffcalcException("Mode %s not supported for this diffractometer (%s). Try one of: %s" % (name, self._geometry.getName(),self._geometry.getSupportedModes()) )
    
    def getMode(self):
        return self._modelist[self._selectedIndex]
    
    def reportCurrentMode(self):
        return self.getMode().__str__()
    
    def reportAvailableModes(self):
        result = ''
        indecis = self._modelist.keys()
        indecis.sort()
        for index in indecis:
            mode = self._modelist[index]
            if self._geometry.supportsModeGroup(mode.group):
                paramString=''
                flags = ''
                for paramName in self.parameter_manager.getUserChangableParametersForMode(mode):
                    paramString += paramName + ", "
                if paramString:
                    paramString = paramString[:-2] # remove trailing commas
                if not mode.implemented:
                    flags += "(Not impl.)"
                result += '%2i) %-15s (%s) %s\n' % (mode.index, mode.description, paramString, flags)    
        return result

