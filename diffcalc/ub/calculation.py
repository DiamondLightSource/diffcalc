from diffcalc.ub.paperspecific import VliegUbCalcStrategy
from diffcalc.ub.persistence import UBCalculationPersister
from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.ub.reflections import ReflectionList
from diffcalc.utils import DiffcalcException, MIRROR, cross3
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix


def matrixTo3x3ListOfLists(m):
    r = list(m.array)
    r[0] = list(r[0])
    r[1] = list(r[1])
    r[2] = list(r[2])
    return r
    

    
class UBCalculation:
    """A UB matrix calculation for an experiment.
    
    Contains the parameters for the _crystal under test, a list of measured reflections
    and, if its been calculated, a UB matrix to be used by the rest of the code.
    """
    
    def __init__(self, hardwareMonitorObject, diffractometerPluginObject, persister = None, strategy = VliegUbCalcStrategy()):
        
        # The diffractometer geometry is required to map the internal angles
        # into those used by this diffractometer (for display only)
    
        self._name = None
        self._crystal  = None
        self._reflist  = None
        self._U = None
        self._UB = None
        self._hardware = hardwareMonitorObject
        self._geometry = diffractometerPluginObject
        self._okayToAutoCalculateUB = True   # True unless U or UB set manualy. Reset to False 
        self._uSetManually = False
        self._ubSetManually = False
        if persister is None:
            self._persister = UBCalculationPersister()
        else:
            self._persister = persister
        self._strategy = strategy
                                                           # when calclulateUB called manualy.
        
        # The UB matrix is used to find or set the orientation of a set of planes
        # described by an hkl vector. The U matrix can be used to find or set
        # the orientation of the crystal lattices' y axis. If there is crystal miscut
        # the crystal lattices y axis is not parallel to the crystals optical
        # surface normal. For surface diffraction experiments, where not only the
        # crystal lattice must be oriented appropriately but so must the crystal's 
        # optical surface, two angles tau and sigma are used to describe the difference
        # between the two. Sigma is (minus) the ammount of chi axis rotation and tau
        # (minus) the ammount of phi axis rotation needed to move the surface normal
        # into the direction of the omega circle axis.
        self._tau = 0 # degrees
        self._sigma = 0 # degrees

### State ###
    def newCalculation(self, name):
        """newCalculation(name) --- creates a new blank ub calculation"""
        # Create storage object if name does not exist (TODO)
        if name in self._persister.list():
            print "No UBCalculation started: There is already a calculation called: " + name
            print "Saved calculations: " + `self._persister.list()`        
        self._newCalculationWithoutSaving(name)
        self.save()

    def _newCalculationWithoutSaving(self, name):
            
        # NOTE the Diffraction calculator is expecting this object to exist
        # in the long run. I.e we can't remove this entire object, and recreate it.
        # It also contains a link to the angle calculator that can't be removed.
        self.reInit()    
        self._name = name
        # Create empty reflection list
        self._reflist = ReflectionList(self._geometry, self._hardware.getPhysicalAngleNames())
        # Clear the _crystal
        self._crystal = None
            
    def load(self, name):
        state = self._persister.load(name)
        self.restoreState(state) # takes a dictionary

    def save(self):
        self.saveas(self._name)

    def saveas(self, name):
        state = self.getState()
        self._name = name
        self._persister.save(state, name)
        
    def listub(self):
        return self._persister.list()
    
    def remove(self, name):
        self._persister.remove(name)
        
    def getState(self):
        state = {
            'name' : self._name,
            'tau' : self._tau,
            'sigma' : self._sigma,
            
            }
        if self._crystal is not None:
            state['crystal'] = self._crystal.getStateDict()
        else:
            state['crystal'] = None
            
        if self._reflist is not None:
            state['reflist'] = self._reflist.getStateDict()
        else:
            state['reflist'] = None    
        
        if self._uSetManually:
            state['u'] = matrixTo3x3ListOfLists(self._U)
        else:
            state['u'] = None
        
        if self._ubSetManually:
            state['ub'] = matrixTo3x3ListOfLists(self._UB)
        else:
            state['ub'] = None
        
        return state
        
    def restoreState(self, state):
        self._newCalculationWithoutSaving(state['name'])
        if state['crystal'] is not None:
            self._setLattice(**state['crystal'])
        self._reflist.restoreFromStateDict(state['reflist'])
        self._tau = state['tau']
        self._sigma = state['sigma']
        if state['u'] is not None:
            self.setUManually(state['u'])
        if state['ub'] is not None:
            self.setUBManually(state['ub'])

    def reInit(self):
        self._U = None
        self._UB = None
        self._name = None
        self._crystal  = None
        self._reflist  = None
        self._okayToAutoCalculateUB = True
        self._uSetManually = False
        self._ubSetManually = False
        self._tau = 0 # degrees
        self._sigma = 0 # degrees
        
    def __str__(self):
        if self._name != None:
            result =  "UBCalc:     %s\n" % self._name
            result += "======\n\n"
            result += "Crystal\n-------\n"
            if self._crystal==None:
                result += "   none specified\n"
            else:
                result += self._crystal.__str__()
            result += "\nReflections\n-----------\n"
            result += self._reflist.__str__()
            result += "\nUB matrix\n---------\n"
            if self._UB==None:
                result += "   none calculated"
            else:
                ub = self._UB.getArray()
                result += "\t       % 18.13f% 18.13f% 18.12f\n" % (ub[0][0], ub[0][1], ub[0][2])
                result += "\t       % 18.13f% 18.13f% 18.12f\n" % (ub[1][0], ub[1][1], ub[1][2])
                result += "\t       % 18.13f% 18.13f% 18.12f\n" % (ub[2][0], ub[2][1], ub[2][2])
                if self._geometry.mirrorInXzPlane:
                    print "   (The effect of the configured mirror is not shown here)"
            result += "\n     Sigma: %f\n" % self._sigma
            result += "         Tau: %f\n" % self._tau
                
        else:
            result = "No UB calculation started.\n" 
        return result

    def getName(self):
        return self._name
### Lattice ###

    def setLattice(self, name, *shortform):    
        """
        Converts a list shortform crystal parameter specification to a six-long-tuple returned as
        . Returns None if wrong number of input args. See setLattice()
        for a description of the shortforms supported.
        
        shortformLattice -- a tuple as follows:
             [a]         - assumes cubic
           [a,b])       - assumes tetragonal
           [a,b,c])     - assumes ortho
           [a,b,c,gam]) - assumes mon/hex gam different from 90.
           [a,b,c,alp,bet,gam]) - for arbitrary
           where all measurements in angstroms and angles in degrees
        """
        self._setLatticeWithoutSaving(name, *shortform )
        self.save()

    def _setLatticeWithoutSaving(self, name, *shortform ):
        if len(shortform)==1:
            fullform = (shortform[0], shortform[0], shortform[0], 90., 90., 90.) # cubic
        elif len(shortform)==2:
            fullform = (shortform[0], shortform[0], shortform[1], 90., 90., 90.) # tetragonal
        elif len(shortform)==3:
            fullform = (shortform[0], shortform[1], shortform[2], 90., 90., 90.) # ortho
        elif len(shortform)==4:
            fullform = (shortform[0], shortform[1], shortform[2], 90., 90., shortform[3]) # mon/hex gam different from 90
        elif len(shortform)==5:
            raise ValueError("wrong length input to setLattice")                                                                    # (not supported)
        elif len(shortform)==6:
            fullform = shortform                                                         # triclinic/arbitrary
        else:
            raise ValueError("wrong length input to setLattice")
        self._setLattice(name, *fullform)
        
    def _setLattice(self, name, a,b,c,alpha,beta,gamma ):
        """setLattice( name, a,b,c,alpha,beta,gamma ) -- set lattice parameters in degrees"""
        if self._name==None:
            raise DiffcalcException("Cannot set lattice until a UBCalcaluation has been started with newubcalc")
        self._crystal = CrystalUnderTest(name, a,b,c,alpha,beta,gamma )
        # Clear U and UB if these exist
        if self._U != None: #(UB will also exist)
            self._U = None
            self._UB = None
            print "Warning: the old UB calculation has been cleared. Use 'calcub' to recalculate with old reflection list."
    
        
    def dispLattice(self):
        print self._crystal.__str__()

### Surface normal stuff ###
    def getTau(self):
        """Returns tau (in degrees): the (minus) ammount of phi axis rotation , that 
        together with some chi axis rotation (minus sigma) brings the optical surface
        normal parallelto the omega axis.
        """
        return self._tau
    
    def setTau(self, tau):
        self._tau = tau
        self.save()

    def getSigma(self):
        """Returns sigma (in degrees): the (minus) ammount of phi axis rotation , that 
        together with some phi axis rotation (minus tau) brings the optical surface
        normal parallelto the omega axis.
        """
        return self._sigma
    
    def setSigma(self, sigma):
        self._sigma = sigma
        self.save()
        
### Reflections ###
        
    def dispReflectionList(self):
        if self._reflist == None:
            return "No UBCalculation loaded"
        else:
            return self._reflist.toStringWithExternalAngles()
    
    def addReflection(self, h, k, l, position, energy, tag, time):
        """addReflection(h, k, l, position, tag=None) -- adds a reflection
        
        position is in degrees and in the systems internal representation.
        """
        if self._reflist == None:
            raise DiffcalcException("No UBCalculation loaded")
        self._reflist.addReflection(h, k, l, position, energy, tag, time)
        self.save() # incase autocalculateUbAndReport fails    

        # If second reflection has just been added then calculateUB
        if len(self._reflist)==2:
            self._autocalculateUbAndReport()
        self.save()
        
    def editReflection(self, num, h, k, l, position, energy, tag, time):
        """editReflection(num, h, k, l, position, tag=None) -- adds a reflection
        
        position is in degrees and in the systems internal representation.
        """
        if self._reflist == None:
            raise DiffcalcException("No UBCalculation loaded")
        self._reflist.editReflection(num, h, k, l, position, energy, tag, time)
        
        # If first or second reflection has been changed and there are at least two reflections
        # then recalculate  UB
        if (num==1 or num==2) and len(self._reflist)>=2:
            self._autocalculateUbAndReport()    
        self.save()

    def getReflectionInExternalAngles(self, num):
        """getReflection(num) --> ( [h, k, l], (angle1...angleN), energy, tag ) -- num starts at 1
        position in degrees"""
        return self._reflist.getReflectionInExternalAngles(num)

    def delReflection(self, reflectionNumber):
        self._reflist.removeReflection(reflectionNumber)
        if (reflectionNumber==1 or reflectionNumber==2) and (self._U != None):
            self._autocalculateUbAndReport()
        self.save()
        
    def swapReflections(self, num1, num2):
        self._reflist.swapReflections(num1, num2)
        if (num1==1 or num1==2 or num2==1 or num2==2) and (self._U != None):
            self._autocalculateUbAndReport()
        self.save()

    def _autocalculateUbAndReport(self):
        if len(self._reflist)<2:
            pass
        elif self._crystal==None:
            print "Not calculating UB matrix as no lattice parameters have been specified."
        elif not self._okayToAutoCalculateUB:
            print "Not calculating UB matrix as it has been manually set. Use 'calcub' to explicitly recalculate it."
        else: # okay to autocalculate
            if self._UB == None:
                print "Calculating UB matrix."
            else:
                print "Recalculating UB matrix."
            self.calculateUB()
    
    def getReflist(self):
        return self._reflist
### Calculations ###

    def setUManually(self, matrix):
        """Manually sets U. matrix must be 3*3 Jama or python matrix.
        Turns off aution UB calcualtion."""
        
        # Check matrix is a 3*3 Jama matrix
        if matrix.__class__ != Matrix:
            matrix = Matrix(matrix) # assume its a python matrix
        if matrix.getRowDimension()!=3 or matrix.getColumnDimension()!=3:
            raise  ValueError("Expects 3*3 matrix")
        
        self._U = matrix
        if self._crystal==None:
            raise DiffcalcException("A crystal must be specified before manually setting U")
        self._UB = self._U.times(self._crystal.getBMatrix())
        if self._UB == None:
            print "Calculating UB matrix."
        else:
            print "Recalculating UB matrix."
        print """NOTE: A new UB matrix will not be automatically calculated when
the orientation reflections are modified."""
        self._okayToAutoCalculateUB = False
        self._uSetManually = True
        self._ubSetManually = False
        self.save()
        
        
    def setUBManually(self, matrix):
        """Manually sets UB. matrix must be 3*3 Jama or python matrix.
        Turns off aution UB calcualtion."""
        
        # Check matrix is a 3*3 Jama matrix
        if matrix.__class__ != Matrix:
            matrix = Matrix(matrix) # assume its a python matrix
        if matrix.getRowDimension()!=3 or matrix.getColumnDimension()!=3:
            raise  ValueError("Expects 3*3 matrix")
        
        self._UB = matrix
        self._okayToAutoCalculateUB = False
        self._uSetManually = False
        self._ubSetManually = True
        self.save()
        
    def setTrialUMatrix(self, omega_u): #add chi_u, phi_u for surface diff
        print "Sorry, this command is not hooked up to anything yet"

        
    def getUMatrix(self):
        if self._U == None:
            raise DiffcalcException("No U matrix has been calculated during this ub calculation")
        return self._U
        
    def getUBMatrix(self):
        if self._UB == None:
            raise DiffcalcException("No UB matrix has been calculated during this ub calculation")
        if self._geometry.mirrorInXzPlane:
            return MIRROR.times(self._UB)
        else:
            return self._UB
    
    def calculateUB(self):
        """ Calculate orientation matrix. Uses first two orientation reflections
        as in busang and Levy, but for the diffractometer in Lohmeier and Vlieg."""
        
        # Major variables:
        # h1, h2        user input reciprical lattice vectors of the two reflections
        # h1c, h2c        user input vectors in cartesian crystal plane        
        # pos1, pos2    measured diffractometer positions of the two reflections
        # u1a, u2a        measured reflection vectors in alpha frame
        # u1p, u2p        measured reflection vectors in phi frame
        # B                B matrix from crystal under test
        
        self._okayToAutoCalculateUB = True
        self._uSetManually = False
        self._ubSetManually = False
        
        # Get hkl and angle values for the first two refelctions
        if self._reflist == None:
            raise DiffcalcException("Cannot calculate a u matrix until a UBCalcaluation has been started with newub")
        try:
            (h1, pos1, energy1, tag1, time1) = self._reflist.getReflection(1)
            (h2, pos2, energy2, tag2, time2) = self._reflist.getReflection(2)
        except IndexError:
            raise DiffcalcException("Two reflections are required to calculate a u matrix")
        del time1, time2
        del tag1, tag2, energy1, energy2
        h1 = Matrix([h1]).transpose() # row->column
        h2 = Matrix([h2]).transpose()
        pos1.changeToRadians()
        pos2.changeToRadians()
        
        # Compute the two reflections' reciprical lattice vectors in the cartesian crystal frame        
        B = self._crystal.getBMatrix()
        h1c = B.times(h1)
        h2c = B.times(h2)
        
        # Build the plane normal directions in alpha-axis coordinate frame
        #u1a = Matrix([[ sin(pos1.delta)*cos(pos1.gamma) ], \
        #              [ cos(pos1.delta)*cos(pos1.gamma) - cos(pos1.alpha) ], \
        #              [ sin(pos1.gamma) + sin(pos1.alpha) ]])
        #
        #u2a = Matrix([[ sin(pos2.delta)*cos(pos2.gamma) ], \
        #              [ cos(pos2.delta)*cos(pos2.gamma) - cos(pos2.alpha) ], \
        #              [ sin(pos2.gamma) + sin(pos2.alpha) ]])
        
        u1p = self._strategy.calculateObserveredPlaneNormalInPhiFrame(pos1)
        u2p = self._strategy.calculateObserveredPlaneNormalInPhiFrame(pos2)
        
        # Create modified unit vectors t1, t2 and t3 in crystal and phi systems...
        t1c = h1c    
        t3c = cross3(h1c, h2c)
        t2c = cross3(t3c, t1c)
        
        t1p = u1p # FIXED from h1c 9July08
        t3p = cross3(u1p, u2p)
        t2p = cross3(t3p, t1p)

        # ...and nornmalise and check that the reflections used are appropriate
        SMALL = 1e-4 # Taken from Vlieg's code
        e=DiffcalcException("Invalid orientation reflection(s)")
        
        d = t1c.normF(); t1c = t1c.times(1/d);
        if d < SMALL: raise e
        d = t2c.normF(); t2c = t2c.times(1/d); #TODO: should be no need to normalise
        if d < SMALL: raise e
        d = t3c.normF(); t3c = t3c.times(1/d);
        if d < SMALL: raise e
        
        d = t1p.normF(); t1p = t1p.times(1/d);
        if d < SMALL: raise e
        d = t2p.normF(); t2p = t2p.times(1/d); #TODO: should be no need to normalise
        if d < SMALL: raise e
        d = t3p.normF(); t3p = t3p.times(1/d);
        if d < SMALL: raise e
    
        # Create Tc and Tp
        Tc = Matrix(3,3)
        Tc.setMatrix([0,1,2],[0], t1c)
        Tc.setMatrix([0,1,2],[1], t2c)
        Tc.setMatrix([0,1,2],[2], t3c)
        
        Tp = Matrix(3,3)
        Tp.setMatrix([0,1,2],[0], t1p)
        Tp.setMatrix([0,1,2],[1], t2p)
        Tp.setMatrix([0,1,2],[2], t3p)
    
        # Compute orientation matrix (!)
        self._U = Tp.times(Tc.inverse())
        
        # Compute UB matrix
        self._UB = self._U.times(B)

        self.save()
        
    def getHklPlaneDistance(self,hkl):
        '''Calculates and returns the distance between planes at a given hkl=[h,k,l]'''
        return self._crystal.getHklPlaneDistance(hkl)


#    def getLattice(self):
#        """getLattice -> (a,b,c,alpha,beta,gamma) -- get lattice parameters"""
#        return self._crystal.getLattice()
    
#    def loadLatticeFromLibrary(self, name):
#        '''
#        Loads the lattice name if it exists.
#        '''
#        self.setLattice(name, self.__library.getCrystal(name))
#    
#    def saveLatticeToLibrary(self, name=None):
#        '''
#        Saves the current lattice as name. Uses curent current name if none given.
#        '''
#        if name == None:
#            name = self.__latticeName
#            
#        self.__library.addCrystal(name, (self.__a, self.__b, self.__c, self.__alpha, self.__beta, self.__gamma))
