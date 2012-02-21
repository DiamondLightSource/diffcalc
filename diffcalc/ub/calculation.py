from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.ub.persistence import UBCalculationPersister
from diffcalc.ub.reflections import ReflectionList
from diffcalc.utils import DiffcalcException, MIRROR, cross3, dot3
from math import acos, cos, sin, pi

try:
    from numpy import matrix, hstack
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix, hstack
    from numjy.linalg import norm

SMALL = 1e-7

TODEG = 180/pi


class PaperSpecificUbCalcStrategy(object):
    
    def calculate_q_phi(self, pos):
        """Calculate hkl in the phi frame in units of 2 * pi / lambda from pos object
        in radians"""
        raise Exception("Abstract")

class UBCalculation:
    """A UB matrix calculation for an experiment.
    
    Contains the parameters for the _crystal under test, a list of measured reflections
    and, if its been calculated, a UB matrix to be used by the rest of the code.
    """
    
    def __init__(self, hardwareMonitorObject, diffractometerPluginObject, persister=None, strategy=None):
        
        # The diffractometer geometry is required to map the internal angles
        # into those used by this diffractometer (for display only)
    
        self._name = None
        self._crystal = None
        self._reflist = None
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
            state['u'] = self._U.tolist()
        else:
            state['u'] = None
        
        if self._ubSetManually:
            state['ub'] = self._UB.tolist()
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
        self._crystal = None
        self._reflist = None
        self._okayToAutoCalculateUB = True
        self._uSetManually = False
        self._ubSetManually = False
        self._tau = 0 # degrees
        self._sigma = 0 # degrees
        
    def __str__(self):
        if self._name != None:
            result = "UBCalc:     %s\n" % self._name
            result += "======\n\n"
            result += "Crystal\n-------\n"
            if self._crystal is None:
                result += "   none specified\n"
            else:
                result += self._crystal.__str__()
            result += "\nReflections\n-----------\n"
            result += self._reflist.__str__()
            result += "\nUB matrix\n---------\n"
            if self._UB is None:
                result += "   none calculated"
            else:
                ub = self._UB
                result += "\t       % 18.13f% 18.13f% 18.12f\n" % (ub[0, 0], ub[0, 1], ub[0, 2])
                result += "\t       % 18.13f% 18.13f% 18.12f\n" % (ub[1, 0], ub[1, 1], ub[1, 2])
                result += "\t       % 18.13f% 18.13f% 18.12f\n" % (ub[2, 0], ub[2, 1], ub[2, 2])
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
        self._setLatticeWithoutSaving(name, *shortform)
        self.save()

    def _setLatticeWithoutSaving(self, name, *shortform):
        if len(shortform) == 1:
            fullform = (shortform[0], shortform[0], shortform[0], 90., 90., 90.) # cubic
        elif len(shortform) == 2:
            fullform = (shortform[0], shortform[0], shortform[1], 90., 90., 90.) # tetragonal
        elif len(shortform) == 3:
            fullform = (shortform[0], shortform[1], shortform[2], 90., 90., 90.) # ortho
        elif len(shortform) == 4:
            fullform = (shortform[0], shortform[1], shortform[2], 90., 90., shortform[3]) # mon/hex gam different from 90
        elif len(shortform) == 5:
            raise ValueError("wrong length input to setLattice")                                                                    # (not supported)
        elif len(shortform) == 6:
            fullform = shortform                                                         # triclinic/arbitrary
        else:
            raise ValueError("wrong length input to setLattice")
        self._setLattice(name, *fullform)
        
    def _setLattice(self, name, a, b, c, alpha, beta, gamma):
        """setLattice( name, a,b,c,alpha,beta,gamma ) -- set lattice parameters in degrees"""
        if self._name is None:
            raise DiffcalcException("Cannot set lattice until a UBCalcaluation has been started with newubcalc")
        self._crystal = CrystalUnderTest(name, a, b, c, alpha, beta, gamma)
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
        if self._reflist is None:
            return "No UBCalculation loaded"
        else:
            return self._reflist.toStringWithExternalAngles()
    
    def addReflection(self, h, k, l, position, energy, tag, time):
        """addReflection(h, k, l, position, tag=None) -- adds a reflection
        
        position is in degrees and in the systems internal representation.
        """
        if self._reflist is None:
            raise DiffcalcException("No UBCalculation loaded")
        self._reflist.addReflection(h, k, l, position, energy, tag, time)
        self.save() # incase autocalculateUbAndReport fails    

        # If second reflection has just been added then calculateUB
        if len(self._reflist) == 2:
            self._autocalculateUbAndReport()
        self.save()
        
    def editReflection(self, num, h, k, l, position, energy, tag, time):
        """editReflection(num, h, k, l, position, tag=None) -- adds a reflection
        
        position is in degrees and in the systems internal representation.
        """
        if self._reflist is None:
            raise DiffcalcException("No UBCalculation loaded")
        self._reflist.editReflection(num, h, k, l, position, energy, tag, time)
        
        # If first or second reflection has been changed and there are at least two reflections
        # then recalculate  UB
        if (num == 1 or num == 2) and len(self._reflist) >= 2:
            self._autocalculateUbAndReport()    
        self.save()

    def getReflectionInExternalAngles(self, num):
        """getReflection(num) --> ( [h, k, l], (angle1...angleN), energy, tag ) -- num starts at 1
        position in degrees"""
        return self._reflist.getReflectionInExternalAngles(num)

    def delReflection(self, reflectionNumber):
        self._reflist.removeReflection(reflectionNumber)
        if (reflectionNumber == 1 or reflectionNumber == 2) and (self._U != None):
            self._autocalculateUbAndReport()
        self.save()
        
    def swapReflections(self, num1, num2):
        self._reflist.swapReflections(num1, num2)
        if (num1 == 1 or num1 == 2 or num2 == 1 or num2 == 2) and (self._U != None):
            self._autocalculateUbAndReport()
        self.save()

    def _autocalculateUbAndReport(self):
        if len(self._reflist) < 2:
            pass
        elif self._crystal is None:
            print "Not calculating UB matrix as no lattice parameters have been specified."
        elif not self._okayToAutoCalculateUB:
            print "Not calculating UB matrix as it has been manually set. Use 'calcub' to explicitly recalculate it."
        else: # okay to autocalculate
            if self._UB is None:
                print "Calculating UB matrix."
            else:
                print "Recalculating UB matrix."
            self.calculateUB()
    
    def getReflist(self):
        return self._reflist
### Calculations ###

    def setUManually(self, m):
        """Manually sets U. matrix must be 3*3 Jama or python matrix.
        Turns off aution UB calcualtion."""
        
        # Check matrix is a 3*3 Jama matrix
        if m.__class__ != matrix:
            m = matrix(m) # assume its a python matrix
        if m.shape[0] != 3 or m.shape[1] != 3:
            raise  ValueError("Expects 3*3 matrix")
        
        self._U = m
        if self._crystal is None:
            raise DiffcalcException("A crystal must be specified before manually setting U")
        self._UB = self._U * self._crystal.getBMatrix()
        if self._UB is None:
            print "Calculating UB matrix."
        else:
            print "Recalculating UB matrix."
        print """NOTE: A new UB matrix will not be automatically calculated when
the orientation reflections are modified."""
        self._okayToAutoCalculateUB = False
        self._uSetManually = True
        self._ubSetManually = False
        self.save()
        
        
    def setUBManually(self, m):
        """Manually sets UB. matrix must be 3*3 Jama or python matrix.
        Turns off aution UB calcualtion."""
        
        # Check matrix is a 3*3 Jama matrix
        if m.__class__ != matrix:
            m = matrix(m) # assume its a python matrix
        if m.shape[0] != 3 or m.shape[1] != 3:
            raise  ValueError("Expects 3*3 matrix")
        
        self._UB = m
        self._okayToAutoCalculateUB = False
        self._uSetManually = False
        self._ubSetManually = True
        self.save()
        
    def setTrialUMatrix(self, omega_u): #add chi_u, phi_u for surface diff
        print "Sorry, this command is not hooked up to anything yet"

        
    def getUMatrix(self):
        if self._U is None:
            raise DiffcalcException("No U matrix has been calculated during this ub calculation")
        return self._U
        
    def getUBMatrix(self):
        if self._UB is None:
            raise DiffcalcException("No UB matrix has been calculated during this ub calculation")
        if self._geometry.mirrorInXzPlane:
            return MIRROR * self._UB
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
        if self._reflist is None:
            raise DiffcalcException("Cannot calculate a u matrix until a UBCalcaluation has been started with newub")
        try:
            (h1, pos1, _, _, _) = self._reflist.getReflection(1)
            (h2, pos2, _, _, _) = self._reflist.getReflection(2)
        except IndexError:
            raise DiffcalcException("Two reflections are required to calculate a u matrix")
        h1 = matrix([h1]).T # row->column
        h2 = matrix([h2]).T
        pos1.changeToRadians()
        pos2.changeToRadians()
        
        # Compute the two reflections' reciprical lattice vectors in the cartesian crystal frame        
        B = self._crystal.getBMatrix()
        h1c = B * h1 
        h2c = B * h2 
        
        # Build the plane normal directions in alpha-axis coordinate frame
        #u1a = Matrix([[ sin(pos1.delta)*cos(pos1.gamma) ], \
        #              [ cos(pos1.delta)*cos(pos1.gamma) - cos(pos1.alpha) ], \
        #              [ sin(pos1.gamma) + sin(pos1.alpha) ]])
        #
        #u2a = Matrix([[ sin(pos2.delta)*cos(pos2.gamma) ], \
        #              [ cos(pos2.delta)*cos(pos2.gamma) - cos(pos2.alpha) ], \
        #              [ sin(pos2.gamma) + sin(pos2.alpha) ]])
        
        u1p = self._strategy.calculate_q_phi(pos1)
        u2p = self._strategy.calculate_q_phi(pos2)
        
        # Create modified unit vectors t1, t2 and t3 in crystal and phi systems...
        t1c = h1c    
        t3c = cross3(h1c, h2c)
        t2c = cross3(t3c, t1c)
        
        t1p = u1p # FIXED from h1c 9July08
        t3p = cross3(u1p, u2p)
        t2p = cross3(t3p, t1p)

        # ...and nornmalise and check that the reflections used are appropriate
        SMALL = 1e-4 # Taken from Vlieg's code
        e = DiffcalcException("Invalid orientation reflection(s)")
        
        d = norm(t1c); t1c = t1c * (1 / d)
        if d < SMALL: raise e
        d = norm(t2c); t2c = t2c * (1 / d) #TODO: should be no need to normalise
        if d < SMALL: raise e
        d = norm(t3c); t3c = t3c * (1 / d)
        if d < SMALL: raise e
        
        d = norm(t1p); t1p = t1p * (1 / d)
        if d < SMALL: raise e
        d = norm(t2p); t2p = t2p * (1 / d) #TODO: should be no need to normalise
        if d < SMALL: raise e
        d = norm(t3p); t3p = t3p * (1 / d)
        if d < SMALL: raise e
    
        # Create Tc and Tp
        Tc = hstack([t1c, t2c, t3c])
#        Tc.setMatrix([0, 1, 2], [0], t1c)
#        Tc.setMatrix([0, 1, 2], [1], t2c)
#        Tc.setMatrix([0, 1, 2], [2], t3c)
        
        Tp = hstack([t1p, t2p, t3p])
#        Tp.setMatrix([0, 1, 2], [0], t1p)
#        Tp.setMatrix([0, 1, 2], [1], t2p)
#        Tp.setMatrix([0, 1, 2], [2], t3p)
    
        # Compute orientation matrix (!)
        self._U = Tp * Tc.I
        
        # Compute UB matrix
        self._UB = self._U * B 

        self.save()
    
    def calculateUBFromPrimaryOnly(self):
        """ Calculate orientation matrix with the shortest absolute angle change. Uses first orientation reflection"""
        
        # Algorithm from http://www.j3d.org/matrix_faq/matrfaq_latest.html
        
        # Get hkl and angle values for the first two refelctions
        if self._reflist is None:
            raise DiffcalcException("Cannot calculate a u matrix until a UBCalcaluation has been started with newub")
        try:
            (h, pos, _, _, _) = self._reflist.getReflection(1)
        except IndexError:
            raise DiffcalcException("One reflection is required to calculate a u matrix")
        
        h = matrix([h]).T # row->column
        pos.changeToRadians()
        B = self._crystal.getBMatrix()
        h_crystal = B * h 
        h_crystal = h_crystal * (1 / norm(h_crystal))
        
        q_measured_phi = self._strategy.calculate_q_phi(pos)
        q_measured_phi = q_measured_phi * (1 / norm(q_measured_phi))
        
        rotation_axis = cross3( h_crystal, q_measured_phi)
        rotation_axis = rotation_axis * (1 / norm(rotation_axis))
        
        cos_rotation_angle = dot3(h_crystal, q_measured_phi)
        rotation_angle = acos(cos_rotation_angle)
        
        uvw = rotation_axis.T.tolist()[0]  # TODO: cleanup
        print "resulting U angle: %.5f deg" % (rotation_angle * TODEG)
        print "resulting U axis direction: [%s]" % (', '.join(['% .5f'%el for el in uvw]))

        u, v, w = uvw
        rcos = cos(rotation_angle);
        rsin = sin(rotation_angle);
        m = [[0,0,0],[0,0,0],[0,0,0]] # TODO: tidy
        m[0][0] =      rcos + u*u*(1-rcos)
        m[1][0] =  w * rsin + v*u*(1-rcos)
        m[2][0] = -v * rsin + w*u*(1-rcos)
        m[0][1] = -w * rsin + u*v*(1-rcos)
        m[1][1] =      rcos + v*v*(1-rcos)
        m[2][1] =  u * rsin + w*v*(1-rcos)
        m[0][2] =  v * rsin + u*w*(1-rcos)
        m[1][2] = -u * rsin + v*w*(1-rcos)
        m[2][2] =      rcos + w*w*(1-rcos)
       
        # Set orientation matrix (!)
        self._U = matrix(m)
        
        # Compute UB matrix
        self._UB = self._U * B



        if self._UB is None:
            print "Calculating UB matrix from the first reflection only."
        else:
            print "Recalculating UB matrix from the first reflection only."
        print """NOTE: A new UB matrix will not be automatically calculated when
the orientation reflections are modified."""
        self._okayToAutoCalculateUB = False
        self._uSetManually = False
        self._ubSetManually = False

        self.save()
        
    
    def getHklPlaneDistance(self, hkl):
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
#        if name is None:
#            name = self.__latticeName
#            
#        self.__library.addCrystal(name, (self.__a, self.__b, self.__c, self.__alpha, self.__beta, self.__gamma))
