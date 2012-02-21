from datetime import datetime
from diffcalc.help import HelpList, UsageHandler
from diffcalc.utils import getInputWithDefault as promptForInput, \
    promptForNumber, promptForList, allnum, isnum
from math import asin, pi


TORAD = pi / 180
TODEG = 180 / pi

_ubcalcCommandHelp = HelpList()


class UbCommand(UsageHandler):
    def appendDocLine(self, line):
        _ubcalcCommandHelp.append(line)


class UbCommands(object):
    
    def __init__(self, hardware, geometry, ubcalc):
        self._hardware = hardware
        self._geometry = geometry
        self._ubcalc = ubcalc
    
    def __str__(self):
        return self._ubcalc.__str__()
        

    _ubcalcCommandHelp.append('Diffcalc')
    
    @UbCommand
    def helpub(self, name=None):
        """helpub ['command'] -- lists all ub commands, or one if command is given'
        """
        if name is None:
            print _ubcalcCommandHelp.getCompleteCommandUsageList()
        else:
            print _ubcalcCommandHelp.getCommandUsageString(str(name))
    
        
    _ubcalcCommandHelp.append("helphkl ['command'] -- lists all hkl commands, or one if command is given")  

    
### UB state ###
    _ubcalcCommandHelp.append('UB_State')
    
    @UbCommand
    def newub(self, name=None):
        """newub ['name'] -- starts a new ub calculation with reflectionlist. Will prompt for lattice parameters.
        """
        if name is None:
            # interactive
            name = promptForInput('calculation name')
            self._ubcalc.newCalculation(name)
            self.setlat()
        elif isinstance(name, str):
            # just trying might cause confusion here
            self._ubcalc.newCalculation(name)
        else:
            raise TypeError()
        
    @UbCommand
    def loadub(self, name_or_num):
        """loadub 'name' -- loads an existing ub calculation: lattice and reflection list.
        """
        if isinstance(name_or_num, str):
            self._ubcalc.load(name_or_num) # the calculation name could be resolvable to int
        self._ubcalc.load(self._ubcalc.listub()[int(name_or_num)])
    
    @UbCommand
    def listub(self):
        """listub -- lists the ub calculations available to load.
        """
        print "UB calculations in cross-visit database:"
        for n, name in enumerate(self._ubcalc.listub()):
            print "%2i) %s" % (n, name)
    
        
    @UbCommand
    def saveubas(self, name):
        """saveubas 'name' -- saves the ubcalculation with a new name (other changes are autosaved)
        """
        if isinstance(name, str):
            # just trying might cause confusion here
            self._ubcalc.saveas(name)
        else:
            raise TypeError()

    @UbCommand
    def ub(self):
        """ub -- shows the complete state of the ub calculation
        """
        print self._ubcalc.__str__() + "Wavelength: %f\n    Energy: %f\n" % (float(self._hardware.getWavelength()), float(self._hardware.getEnergy()))

### UB lattice ###
    _ubcalcCommandHelp.append('UB_lattice')

    @UbCommand
    def setlat(self, name=None, *args):
        """
        setlat  -- prompts user to enter lattice parameters (in Angstroms and Degrees)
        setlat name a -- assumes cubic
        setlat name a b -- assumes tetragonal
        setlat name a b c -- assumes ortho
        setlat name a b c gamma -- assumes mon/hex with gam not equal to 90
        setlat name a b c alpha beta gamma -- arbitrary
        """
        
        if name is None: # Interactive
            name = promptForInput(" name")
            a = promptForNumber('    a', 1)
            b = promptForNumber('    b', a)
            c = promptForNumber('    c', a)
            alpha = promptForNumber('alpha', 90)
            beta = promptForNumber('beta', 90)
            gamma = promptForNumber('gamma', 90)
            self._ubcalc.setLattice(name, a, b, c, alpha, beta, gamma)
            
        elif isinstance(name, str) and len(args) in (1, 2, 3, 4, 6) and allnum(args):
            # first arg is string and rest are numbers
            self._ubcalc.setLattice(name, *args)
        else:
            raise TypeError()
    
    @UbCommand
    def c2th(self, hkl=None):
        """
        c2th [h k l]  -- calculated two-theta angle for given reflection
        """
        wl = self._hardware.getWavelength()
        d = self._ubcalc.getHklPlaneDistance(hkl)
        # n*lamba = 2d*sin(theta)
        tmp = wl / (2 * d)
        return 2.0 * asin(wl / (d * 2)) * TODEG

### Surface stuff ###
    _ubcalcCommandHelp.append('UB_surface')

    @UbCommand
    def sigtau(self, sigma=None, tau=None):
        """sigtau [sigma tau] -- sets sigma and tau'"""
        if sigma is None and tau is None:
            chi = self._hardware.getPositionByName('chi')
            phi = self._hardware.getPositionByName('phi')
            print "sigma, tau = %f, %f" % (self._ubcalc.getSigma(), self._ubcalc.getTau())
            print "  chi, phi = %f, %f" % (chi, phi)
            sigma = promptForInput("sigma", -chi)
            tau = promptForInput("  tau", -phi)
            self._ubcalc.setSigma(sigma)
            self._ubcalc.setTau(tau)
        else:
            self._ubcalc.setSigma(float(sigma))
            self._ubcalc.setTau(float(tau))
        
### UB refelections ###
    _ubcalcCommandHelp.append('UB_reflections')
    
    @UbCommand
    def showref(self):
        """showref -- shows full reflection list"""
        print self._ubcalc.dispReflectionList()
        
    @UbCommand
    def addref(self, *args):
        """addref -- add reflection interactively
        addref h k l ['tag'] -- add reflection with hardware position and energy
        addref h k l (p1,p2...pN) energy ['tag'] -- add reflection with specified position and energy)
        addref h k l [tag_string] #len=3/4
        addref h k l (p1,p2...pN) energy [tag_string] #len=5/6
        Position is that of the external diffractometer in degrees
        """
        
        if len(args) == 0:
            h = promptForNumber('h', 0.)
            k = promptForNumber('k', 0.)
            l = promptForNumber('l', 0.)
            if None in (h, k, l):
                self.handleInputError("h,k and l must all be numbers")
            reply = promptForInput('current pos', 'y')
            if reply in ('y', 'Y', 'yes'):
                positionList = self._hardware.getPosition()
                energy = self._hardware.getEnergy()
            else:
                currentPos = self._hardware.getPosition()
                positionList = []
                for i, angleName in enumerate(self._hardware.getPhysicalAngleNames()):
                    val = promptForNumber(angleName.rjust(7), currentPos[i])
                    if val is None:
                        self.handleInputError("Please enter a number, or press Return to accept default!")
                        return
                    positionList.append(val)
                energy = promptForNumber('energy', self._hardware.getEnergy())
                if val is None:
                    self.handleInputError("Please enter a number, or press Return to accept default!")
                    return
                energy = energy * self._hardware.energyScannableMultiplierToGetKeV
            tag = promptForInput("tag")
            if tag == '':tag = None
            pos = self._geometry.physicalAnglesToInternalPosition(positionList)
            self._ubcalc.addReflection(h, k, l, pos, energy, tag, datetime.now())
        elif len(args) in (3, 4, 5, 6):
            args = list(args)
            h = args.pop(0)
            k = args.pop(0)
            l = args.pop(0)
            if not (isnum(h) and isnum(k) and isnum(l)):
                raise TypeError()
            if len(args) >= 2:
                pos = self._geometry.physicalAnglesToInternalPosition(args.pop(0))
                energy = args.pop(0)
                if not isnum(energy):
                    raise TypeError()
            else:
                pos = self._geometry.physicalAnglesToInternalPosition(self._hardware.getPosition())
                energy = self._hardware.getEnergy()
            if len(args) == 1:
                tag = args.pop(0)
                if not isinstance(tag, str):
                    raise TypeError()
            else:
                tag = None
            self._ubcalc.addReflection(h, k, l, pos, energy, tag, datetime.now())
        else:
            raise TypeError()



    @UbCommand
    def editref(self, num):
        """editref num -- interactively edit a reflection.
        """
        num = int(num)
        
        # Get old reflection values
        ([oldh, oldk, oldl], oldExternalAngles, oldEnergy, oldTag, oldT) = self._ubcalc.getReflectionInExternalAngles(num)
        del oldT # current time will be used.
        
        h = promptForNumber('h', oldh)
        k = promptForNumber('k', oldk)
        l = promptForNumber('l', oldl)
        if None in (h, k, l):
            self.handleInputError("h,k and l must all be numbers")
        reply = promptForInput('update position with current hardware setting', 'n')
        if reply in ('y', 'Y', 'yes'):
            positionList = self._hardware.getPosition()
            energy = self._hardware.getEnergy()
        else:
            positionList = []
            for i, angleName in enumerate(self._hardware.getPhysicalAngleNames()):
                val = promptForNumber(angleName.rjust(7), oldExternalAngles[i])
                if val is None:
                    self.handleInputError("Please enter a number, or press Return to accept default!")
                    return
                positionList.append(val)
            energy = promptForNumber('energy', oldEnergy)
            if val is None:
                self.handleInputError("Please enter a number, or press Return to accept default!")
                return
            energy = energy * self._hardware.energyScannableMultiplierToGetKeV
        tag = promptForInput("tag", oldTag)
        if tag == '':tag = None
        pos = self._geometry.physicalAnglesToInternalPosition(positionList)
        self._ubcalc.editReflection(num, h, k, l, pos, energy, tag, datetime.now())    


    @UbCommand
    def delref(self, num):
        """delref num -- deletes a reflection (numbered from 1)
        """
        self._ubcalc.delReflection(int(num))
        
    @UbCommand
    def swapref(self, num1=None, num2=None):
        """swapref -- swaps first two reflections used for calulating U matrix
        swapref num1 num2 -- swaps two reflections (numbered from 1)
        """
        if num1 is None and num2 is None:
            self._ubcalc.swapReflections(1, 2)
        elif isinstance(num1, int) and isinstance(num2, int):
            self._ubcalc.swapReflections(num1, num2)
        else:
            raise TypeError()

### UB calculations ###
    _ubcalcCommandHelp.append('ub')
    @UbCommand
    def setu(self, U=None):
        """setu [((,,),(,,),(,,))] --- manually set u matrix
        """
        if U is None:
            U = self._promptFor3x3MatrixDefaultingToIdentity()
            if U is None:
                return # an error will have been printed or thrown
        if self.__is3x3TupleOrList(U):
            self._ubcalc.setUManually(U)
        else:
            raise TypeError("U must be given as 3x3 list or tuple")

        
    @UbCommand
    def setub(self, UB=None):
        """setub [((,,),(,,),(,,))] -- manually set ub matrix"""
        if UB is None:
            UB = self._promptFor3x3MatrixDefaultingToIdentity()
            if UB is None:
                return # an error will have been printed or thrown
        if self.__is3x3TupleOrList(UB):
            self._ubcalc.setUBManually(UB)
        else:
            raise TypeError("UB must be given as 3x3 list or tuple")


    def _promptFor3x3MatrixDefaultingToIdentity(self):
        estring = "Please enter a number, or press Return to accept default!"
        row1 = promptForList("row1", (1, 0, 0))
        if row1 is None:
            self.handleInputError(estring)
            return None
        row2 = promptForList("row2", (0, 1, 0))
        if row2 is None:
            self.handleInputError(estring)
            return None
        row3 = promptForList("row3", (0, 0, 1))
        if row3 is None:
            self.handleInputError(estring)
            return None
        return [row1, row2, row3]

    @UbCommand
    def calcub(self):
        """calcub -- (re)calculate u matrix from ref1 and ref2.
        """
        self._ubcalc.calculateUB()

    @UbCommand
    def trialub(self):
        """trialub -- (re)calculate u matrix from ref1 only (check carefully).
        """
        self._ubcalc.calculateUBFromPrimaryOnly()


    def __is3x3TupleOrList(self, m):
        if type(m) not in (list, tuple): return False
        if len(m) != 3: return False
        for mrow in m:
            if type(mrow) not in (list, tuple): return False
            if len(mrow) != 3: return False
        return True
