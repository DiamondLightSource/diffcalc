try:
    from gda.device.scannable.scannablegroup import ScannableMotionWithScannableFieldsBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.group import ScannableMotionWithScannableFieldsBase


from diffcalc.utils import getMessageFromException

class Hkl(ScannableMotionWithScannableFieldsBase):

    def __init__(self , name , diffractometerObject, diffcalcObject, virtualAnglesToReport=None):
        self.diffhw = diffractometerObject
        self._diffcalc = diffcalcObject
        if type(virtualAnglesToReport) is str:
            virtualAnglesToReport = (virtualAnglesToReport,)
        self.vAngleNames = virtualAnglesToReport
        
        self.setName(name)
        self.setInputNames(['h', 'k', 'l'])
        self.setOutputFormat(['%7.5f'] * 3)
        if self.vAngleNames:
            self.setExtraNames(self.vAngleNames)
            self.setOutputFormat(['%7.5f'] * (3 + len(self.vAngleNames)))
        
        self.completeInstantiation()
        self.setAutoCompletePartialMoveToTargets(True)

    def rawAsynchronousMoveTo(self, hkl):
        #if type(hkl) not in (type(()), type([])): ...
        try:
            hkl = list(hkl)
        except TypeError:
            raise ValueError('Hkl value could not be turned into list. Received %s of type %s' % (str(hkl), str(type(hkl))))
        if len(hkl) != 3: raise ValueError('Hkl device expects three inputs')
        
        (pos, _) = self._diffcalc._hklToAngles(hkl[0], hkl[1], hkl[2])
        self.diffhw.asynchronousMoveTo(pos)
        
    def rawGetPosition(self):
        pos = self.diffhw.getPosition()
        (hkl , params) = self._diffcalc._anglesToHkl(pos)
        result = list(hkl)
        if self.vAngleNames:
            for vAngleName in self.vAngleNames:
                result.append(params[vAngleName])
        return result
    
    def isBusy(self):
        return self.diffhw.isBusy()

    def waitWhileBusy(self):
        return self.diffhw.waitWhileBusy()
    
    def simulateMoveTo(self, hkl):
        if type(hkl) not in (list, tuple):
            raise ValueError('Hkl device expects three inputs')
        if len(hkl) != 3:
            raise ValueError('Hkl device expects three inputs')
        (pos, params) = self._diffcalc._hklToAngles(hkl[0], hkl[1], hkl[2])
        
        result = self.diffhw.getName() + ' would move to:\n'
        for idx, name in enumerate(self.diffhw.getInputNames()):
            result += '  %s : % 9.5f deg\n' % (name.rjust(6), pos[idx])
        result += '\n'
#        result += '   theta : %f\n' % params['theta']
        result += '  2theta : %f\n' % params['2theta']
        result += '     Bin : %f\n' % params['Bin']
        result += '    Bout : %f\n' % params['Bout']
        result += ' azimuth : %f\n' % params['azimuth']
        return result
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        result = 'hkl:\n'
        pos = self.diffhw.getPosition()
        try:
            (hkl , params) = self._diffcalc._anglesToHkl(pos)
        except Exception, e:
            return "<hkl: %s>" % getMessageFromException(e)
        result += '       h : %f\n' % hkl[0]
        result += '       k : %f\n' % hkl[1]
        result += '       l : %f\n' % hkl[2]
        result += '\n'
#        result += '   theta : %f\n' % params['theta']
        result += '  2theta : %f\n' % params['2theta']
        result += '     Bin : %f\n' % params['Bin']
        result += '    Bout : %f\n' % params['Bout']
        result += ' azimuth : %f\n' % params['azimuth']
#        result += '\n'
#        result += self._diffcalc._reportModeBriefly()
        return result
    
#    class MotionScannablePart(DottedAccessPseudoDevice.MotionScannablePart):
#    
#        def __repr__(self):
#            # Get the name of this field (assume its an input field first and correct if wrong
#            name = self.getInputNames()[0]
#            if name == 'value':
#                name = self.getExtraNames()[0]
#            try:
#                return self.parentScannable.getName() + "." + name + " : " + str(self.getPosition())
#            except Exception, e:
#                return "<%s: %s>" % (self.getName(), getMessageFromException(e))
