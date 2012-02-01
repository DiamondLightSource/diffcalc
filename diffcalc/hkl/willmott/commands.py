from diffcalc.help import HelpList, UsageHandler
from diffcalc.hkl.common_commands import sim
import diffcalc.help

_hklcalcCommandHelp = HelpList()

class HklCommand(UsageHandler):
    def appendDocLine(self, line):
        _hklcalcCommandHelp.append(line)


class WillmottHklCommands(object):
    
    def __init__(self, hardware, geometry, hklcalc):
        self._hardware = hardware
        self._geometry = geometry
        self._hklcalc = hklcalc
        
        self._addDynamicHelpLines()

    def _addDynamicHelpLines(self):
        angleNames = self._hardware.getPhysicalAngleNames()
        formatStr = ("[" + "%s, "*len(angleNames))[:-1] + "]"
        diffHwName = self._hardware.getDiffHardwareName()
        _hklcalcCommandHelp.append('pos ' + diffHwName + ' ' + formatStr % angleNames + ' --move diffractometer to Eularian position. Use None to hold a value still')
        _hklcalcCommandHelp.append('sim ' + diffHwName + ' ' + formatStr % angleNames + '-- simulates moving ' + diffHwName)    
        _hklcalcCommandHelp.append(diffHwName + '-- shows loads of info about current ' + diffHwName + ' position')
    
    def __str__(self):
        return self._hklcalc.__str__()
    
    _hklcalcCommandHelp.append('Diffcalc')
    
    @HklCommand
    def helphkl(self, name=None):
        """helphkl [command] -- lists all hkl commands, or one if command is given
        """
        if name is None:
            print _hklcalcCommandHelp.getCompleteCommandUsageList()
        else:
            print _hklcalcCommandHelp.getCommandUsageString(str(name))

    _hklcalcCommandHelp.append('helpub [command] -- lists all ub commands, or one if command is given')
    
### Settings ###
    _hklcalcCommandHelp.append('Calculator')
    
    ## TODO:HklCommand hklmode

    def _setParameter(self, name, value):
        raise Exception("parameters not supported yet")
        
    def _getParameter(self, name):
        raise Exception("parameters not supported yet")
    
    # TODO: @HklCommand setpar
   
    # TODO: @HklCommand trackalpha

    # TODO: @HklCommand trackgamma

    # TODO: @HklCommand trackphi

### Motion ###

    #(Note except for the sim command, these are all implemented by the external euler, and hkl
    _hklcalcCommandHelp.append('Motion')

    #TODO: Messy, inconsistant use of square brackets in usage strings.
    _hklcalcCommandHelp.append('pos hkl [h k l] -- move diffractometer to hkl, or read hkl position. Use None to hold a value still')

    _hklcalcCommandHelp.append('sim hkl [h k l] -- simulates moving hkl')

    _hklcalcCommandHelp.append('hkl -- shows loads of info about current hkl position')

    @HklCommand
    def sim(self, scn, hkl):
        """sim hkl [h k l] --simulates moving hkl
        """
        sim(scn, hkl, diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS)
