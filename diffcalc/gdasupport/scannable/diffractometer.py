from diffcalc.utils import getMessageFromException
try:
    from gda.device.scannable import PseudoDevice
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.scannable import Scannable as PseudoDevice
    
# TODO: Split into a base class when making other scannables

class DiffractometerScannableGroup(PseudoDevice):
    """"Wraps up a scannableGroup of axis to tweak the way the resulting object is
    displayed and to add a simulate move to method.
    
    The scannable group should have the same geometry as that expected by the
    diffractometer hardware geometry used in the diffraction calculator.
    
    The optional parameter slaveDriver can be used to provide a SlaveScannableDriver. This is useful for
    triggering a move of an incidental axis whose position depends on that of the diffractometer, but whose
    position need not be included in the DiffractometerScannableGroup itself. This parameter is exposed
    as a field and can be set or cleared to null at will without effecting the core calculation code.
    """
    
    def __init__(self , name , diffcalcObject, scannableGroup, slaveScannableDriver = None):
        # if motorList is None, will create a dummy __group
        self.__diffcalc = diffcalcObject
        self.__group = scannableGroup
        self.slaveScannableDriver = slaveScannableDriver
        self.setName(name)
        self.setInputNames(self.__group.getInputNames())
        self.setOutputFormat(self.__group.getOutputFormat())
    
    def setDiffcalcObject(self, diffcalcObject):
        self.__diffcalc = diffcalcObject
    
    def asynchronousMoveTo(self,position):
        self.__group.asynchronousMoveTo(position)
        if self.slaveScannableDriver is not None:
            self.slaveScannableDriver.triggerAsynchronousMove(position)
        
    def getPosition(self):
        return self.__group.getPosition()
        
    def isBusy(self):
        if self.slaveScannableDriver is None:
            return self.__group.isBusy()
        else:
            return self.__group.isBusy() or self.slaveScannableDriver.isBusy() 
    
    def simulateMoveTo(self, pos):
        if len(pos)!=len(self.getInputNames()): raise ValueError('Wrong number of inputs')
        try:
            (hkl, params) = self.__diffcalc._anglesToHkl(pos)
        except Exception, e:
            return "Error: %s" % getMessageFromException(e)
        result = 'hkl would move to:\n'
        result += '  h : %f\n  k : %f\n  l : %f\n' % (hkl[0], hkl[1], hkl[2])
        result += '\n'
#        result += '   theta : %f\n' % params['theta']
        result += '  2theta : %f\n' % params['2theta']
        result += '     Bin : %f\n' % params['Bin']
        result += '    Bout : %f\n' % params['Bout']
        result += ' azimuth : %f\n' % params['azimuth']
        return result
    
    def __repr__(self):
        result = self.getName() + ':\n'
        pos = self.getPosition()
        for idx, name in enumerate(self.getInputNames()):
            result += '  %s : %s deg\n' % (name.rjust(5), str(pos[idx]))
        return result