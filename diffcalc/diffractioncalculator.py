import diffcalc.help #@UnusedImport for flag

from diffcalc.ub.commands import UbCommands, UbCommand
from diffcalc.hkl.commands import HklCommands
from diffcalc.mapper.commands import MapperCommands


class Diffcalc(object):
    """
    Methods that begin with an underscore are used by external classes. The underscore indicates that
    the method should not be exposed on the command line. TODO: Fix this.
    """
    
    def __init__(self, diffractometerPluginObject,
                 hardwareMonitorPluginObject,
                 RAISE_EXCEPTIONS_FOR_ALL_ERRORS=False,
                 raiseExceptionsIfAnglesDoNotMapBackToHkl=True,
                 ub_persister=None):
       
        self._geometry = diffractometerPluginObject  # Geometry specific _plugin        
        
        self._hardware = hardwareMonitorPluginObject
        
        self._mapper = MapperCommands(self._geometry, self._hardware)
        
        self._ubcommands = UbCommands(self._hardware, self._geometry, ub_persister)
                        
        self._hklcommands = HklCommands(self._ubcommands, self._hardware, self._geometry, raiseExceptionsIfAnglesDoNotMapBackToHkl)
    
        diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = RAISE_EXCEPTIONS_FOR_ALL_ERRORS


    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return self._ubcommands.__str__() + "\n" + self._hklcommands.__str__()
    
### Used by diffcalc scannables
    
    def _getDiffractometerPlugin(self):
        return self._geometry

    def _getHardwareMonitor(self):
        return self._hardware

    def _getAxisNames(self):
        return self._hardware.getPhysicalAngleNames()
    
    def _getParameterNames(self):
        return self._hklcommands.getParameterDict().keys()

    def _setParameter(self, name, value):
        self._hklcommands.setParameter(name, value)
        
    def _getParameter(self, name):
        return self._hklcommands.getParameter(name)

    def _hklToAngles(self, h, k, l, energy=None):
        """Convert a given hkl vector to a set of diffractometer angles"""
        if energy is None:
            energy = self._hardware.getEnergy()
        (pos, params) = self._hklcommands.hklToAngles(h, k, l, energy)
        return (self._mapper.map(pos), params)
    
    def _anglesToHkl(self, angleTuple, energy=None):
        """Converts a set of diffractometer angles to an hkl position
        ((h, k, l), paramDict)=_anglesToHkl(self, (a1, a2,aN), energy=None)"""      
        #we will assume this is called correctly, as it is not a user command
        if energy is None:
            energy = self._hardware.getEnergy()
        return self._hklcommands.anglesToHkl(self._geometry.physicalAnglesToInternalPosition(angleTuple), energy)

### ub commands

    def helpub(self, *args):
        return self._ubcommands.helpub(*args)

    def newub(self, *args):
        return self._ubcommands.newub(*args)

    def loadub(self, *args):
        return self._ubcommands.loadub(*args)

    def listub(self, *args):
        return self._ubcommands.listub(*args)

    def saveubas(self, *args):
        return self._ubcommands.saveubas(*args)

    def ub(self, *args):
        return self._ubcommands.ub(*args)

    def setlat(self, *args):
        return self._ubcommands.setlat(*args)
    
    def c2th(self, *args):
        return self._ubcommands.c2th(*args)

    def sigtau(self, *args):
        return self._ubcommands.sigtau(*args)

    def showref(self, *args):
        return self._ubcommands.showref(*args)

    def addref(self, *args):
        return self._ubcommands.addref(*args)

    def editref(self, *args):
        return self._ubcommands.editref(*args)

    def delref(self, *args):
        return self._ubcommands.delref(*args)

    def swapref(self, *args):
        return self._ubcommands.swapref(*args)

    def setu(self, *args):
        return self._ubcommands.setu(*args)

    def setub(self, *args):
        return self._ubcommands.setub(*args)

    def calcub(self, *args):
        return self._ubcommands.calcub(*args)

    # This command requires both the hklcommands and ubcommands components      
    @UbCommand
    def checkub(self):
        """checkub -- show calculated and entered hkl values for reflections."""

        s = "   %-6s %-4s %-4s %-4s  %-6s %-6s %-6s  tag\n" % \
        ('energy', 'h', 'k', 'l', 'h_comp', 'k_comp', 'l_comp')
        
        if self._ubcommands.getReflist() is None:
            s += "<<empty>>"
        else:
            reflist = self._ubcommands.getReflist()
            if len(reflist) == 0:
                s += "<<empty>>"
            for n in range(len(reflist)):
                (hklguess, pos, energy, tag, time) = reflist.getReflection(n + 1)
                (hkl, params) = self._hklcommands.anglesToHkl(pos, energy)
                del time, params
                if tag is None:
                    tag = ""
                s += "%-2d %-6.4f %-4.2f %-4.2f %-4.2f  %-6.4f %-6.4f %-6.4f  %-s\n" % \
                                      (n + 1, energy, hklguess[0], hklguess[1], hklguess[2], hkl[0], hkl[1], hkl[2], tag)
        print s

### hkl commands

    def helphkl(self, *args):
        return self._hklcommands.helphkl(*args)

    def hklmode(self, *args):
        return self._hklcommands.hklmode(*args)

    def setpar(self, *args):
        return self._hklcommands.setpar(*args)

    def trackalpha(self, *args):
        return self._hklcommands.trackalpha(*args)

    def trackgamma(self, *args):
        return self._hklcommands.trackgamma(*args)

    def trackphi(self, *args):
        return self._hklcommands.trackphi(*args)

    def sim(self, *args):
        return self._hklcommands.sim(*args)
    
### mapper commands

    def mapper(self, *args):
        return self._mapper.mapper(*args)

    def transforma(self, *args):
        return self._mapper.transforma(*args)

    def transformb(self, *args):
        return self._mapper.transformb(*args)

    def transformc(self, *args):
        return self._mapper.transformc(*args)

    def sector(self, *args):
        return self._mapper.sector(*args)

    def autosector(self, *args):
        return self._mapper.autosector(*args)

    def setcut(self, *args):
        return self._mapper.setcut(*args)

    def setmin(self, *args):
        return self._mapper.setmin(*args)

    def setmax(self, *args):
        return self._mapper.setmax(*args)
