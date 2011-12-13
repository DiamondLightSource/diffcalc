import diffcalc.help #@UnusedImport for flag

from diffcalc.ub.commands import UbCommands, UbCommand
from diffcalc.hkl.commands import HklCommands
from diffcalc.mapper.commands import MapperCommands
from diffcalc.ub.calculation import UBCalculation
from diffcalc.hkl.calcvlieg import VliegHklCalculator
from diffcalc.mapper.sector import SectorSelector
from diffcalc.mapper.mapper import PositionMapper
from diffcalc.utils import DiffcalcException


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
       
        self._geometry = diffractometerPluginObject 
        self._hardware = hardwareMonitorPluginObject
        diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = RAISE_EXCEPTIONS_FOR_ALL_ERRORS

        # Create core calculation code
        self._ubcalc = UBCalculation(self._hardware, self._geometry, ub_persister)
        self._hklcalc = VliegHklCalculator(self._ubcalc, self._geometry, self._hardware, raiseExceptionsIfAnglesDoNotMapBackToHkl)
        self._sector_selector = SectorSelector()
        self._position_mapper = PositionMapper(self._geometry, self._hardware, self._sector_selector)

        # Create user interface code
        self.ubcommands = UbCommands(self._hardware, self._geometry, self._ubcalc)
        self.hklcommands = HklCommands(self._hardware, self._geometry, self._hklcalc)
        self.mappercommands = MapperCommands(self._geometry, self._hardware, self._position_mapper)


    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return self.ubcommands.__str__() + "\n" + self.hklcommands.__str__()
    
### Used by diffcalc scannables
    
    def _getDiffractometerPlugin(self):
        return self._geometry

    def _getHardwareMonitor(self):
        return self._hardware

    def _getAxisNames(self):
        return self._hardware.getPhysicalAngleNames()
    
    def _getParameterNames(self):
        return self._hklcalc.parameter_manager.getParameterDict().keys()

    def _setParameter(self, name, value):
        self._hklcalc.parameter_manager.setParameter(name, value)
        
    def _getParameter(self, name):
        return self._hklcalc.parameter_manager.getParameter(name)

    def _hklToAngles(self, h, k, l, energy=None):
        """Convert a given hkl vector to a set of diffractometer angles"""
        if energy is None:
            energy = self._hardware.getEnergy()
            
        try:
            wavelength = 12.39842 / energy
        except ZeroDivisionError:
            raise DiffcalcException("Cannot calculate hkl position as Energy is set to 0")

        (pos, params) = self._hklcalc.hklToAngles(h, k, l, wavelength)
        return (self._position_mapper.map(pos), params)
    
    def _anglesToHkl(self, angleTuple, energy=None):
        """Converts a set of diffractometer angles to an hkl position
        ((h, k, l), paramDict)=_anglesToHkl(self, (a1, a2,aN), energy=None)"""      
        #we will assume this is called correctly, as it is not a user command
        if energy is None:
            energy = self._hardware.getEnergy()

        try:
            wavelength = 12.39842 / energy
        except ZeroDivisionError:
            raise DiffcalcException("Cannot calculate hkl position as Energy is set to 0")

        return self._hklcalc.anglesToHkl(self._geometry.physicalAnglesToInternalPosition(angleTuple), wavelength)


    # This command requires both the hklcommands and ubcommands components      
    @UbCommand
    def checkub(self):
        """checkub -- show calculated and entered hkl values for reflections."""

        s = "   %-6s %-4s %-4s %-4s  %-6s %-6s %-6s  tag\n" % \
        ('energy', 'h', 'k', 'l', 'h_comp', 'k_comp', 'l_comp')
        
        if self._ubcalc.getReflist() is None:
            s += "<<empty>>"
        else:
            reflist = self._ubcalc.getReflist()
            if len(reflist) == 0:
                s += "<<empty>>"
            for n in range(len(reflist)):
                (hklguess, pos, energy, tag, time) = reflist.getReflection(n + 1)
                (hkl, params) = self._hklcalc.anglesToHkl(pos, energy)
                del time, params
                if tag is None:
                    tag = ""
                s += "%-2d %-6.4f %-4.2f %-4.2f %-4.2f  %-6.4f %-6.4f %-6.4f  %-s\n" % \
                                      (n + 1, energy, hklguess[0], hklguess[1], hklguess[2], hkl[0], hkl[1], hkl[2], tag)
        print s