''' Contains the lattice parameters and calculated B matrix for the crytsal under test. Also
Calculates the distance between planes at a given hkl value.

The lattice paraemters can be specified and then if desired saved to a __library to be loaded 
later. The parameters are persisted across restarts.  Lattices stored in 
config/var/crystals.xml .
'''


from math import pi, cos, sin, acos, sqrt
try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

TORAD = pi / 180
TODEG = 180 / pi

class CrystalUnderTest:
    def __init__(self, name, a, b, c, alpha, beta, gamma):
        '''Creates a new lattice and calculates related values.
        
        Note: uses the convention where reciprical lattice vectors include 2pi factor
        
        Keyword arguments:
            name -- a string
            a,b,c,alpha,beta,gamma -- lengths and angles (in degrees) 
        '''
        
        self._name = name
                
        # Set the lattice parameters
        self._a1 = a1 = a
        self._a2 = a2 = b
        self._a3 = a3 = c
        self._alpha1 = alpha1 = alpha * TORAD
        self._alpha2 = alpha2 = beta * TORAD
        self._alpha3 = alpha3 = gamma * TORAD

        # Calculate the reciprical lattice paraemeters from the direct parameters
        self._beta1 = acos((cos(alpha2) * cos(alpha3) - cos(alpha1)) / (sin(alpha2) * sin(alpha3)))
        self._beta2 = acos((cos(alpha1) * cos(alpha3) - cos(alpha2)) / (sin(alpha1) * sin(alpha3)))
        self._beta3 = acos((cos(alpha1) * cos(alpha2) - cos(alpha3)) / (sin(alpha1) * sin(alpha2)))
        
        volume = a1 * a2 * a3 * sqrt(1 + 2 * cos(alpha1) * cos(alpha2) * cos(alpha3) - pow((cos(alpha1)), 2) - pow(cos(alpha2), 2) - pow(cos(alpha3), 2))
        self._b1 = 2 * pi * a2 * a3 * sin(alpha1) / volume;
        self._b2 = 2 * pi * a1 * a3 * sin(alpha2) / volume;
        self._b3 = 2 * pi * a1 * a2 * sin(alpha3) / volume;

        # Calculate the BMatrix from the direct and reciprical lattice parameters.
        # Reference: Busang and Levy (1967)
        self._bMatrix = matrix([[self._b1, self._b2 * cos(self._beta3), self._b3 * cos(self._beta2)],
                                 [0.0, self._b2 * sin(self._beta3), -self._b3 * sin(self._beta2) * cos(self._alpha1)],
                                [0.0, 0.0, 2 * pi / self._a3]])


    def getBMatrix(self):
        '''getBmatrix() --> 3*3 JAMA matrix
        
        Returns the B matrix, may be null if crystal is not set, or if there was a problem
        calculating this'''        
        return self._bMatrix


    def getHklPlaneDistance(self, hkl):
        '''Calculates and returns the distance between planes at a given hkl=[h,k,l]'''
        h, k, l = hkl
        c1 = self._a1 * self._a2 * cos(self._beta3)
        c2 = self._a1 * self._a3 * cos(self._beta2)
        c3 = self._a2 * self._a3 * cos(self._beta1)
        return sqrt(1.0 / (h ** 2 * self._a1 ** 2 + k ** 2 * self._a2 ** 2 + l ** 2 * self._a3 ** 2 + 2 * h * k * c1 + 2 * h * l * c2 + 2 * k * l * c3))



    def __str__(self):
        '''    Returns lattice name and all set and calculated parameters'''
        
        # Assume that if name is set, everything has been calculated
        if self._name is None:
            return "   none specified\n" 
        
        b = self._bMatrix
        
        result = "   crystal:       %s\n\n" % self._name
        result += "   lattice:                a ,b ,c  = % 9.5f, % 9.5f, % 9.5f\n" % (self._a1, self._a2, self._a3)
        result += "                alpha, beta, gamma  = % 9.5f, % 9.5f, % 9.5f\n" % (self._alpha1 * TODEG, self._alpha2 * TODEG, self._alpha3 * TODEG)
        result += "\n"
        result += "   reciprical:          b1, b2, b3  = % 9.5f, % 9.5f, % 9.5f\n" % (self._b1, self._b2, self._b3)
        result += "               beta1, beta2, beta3  = % 9.5f, % 9.5f, % 9.5f\n" % (self._beta1, self._beta2, self._beta3)
        result += "\n"
        result += "   B matrix:   % 18.13f% 18.13f% 18.12f\n" % (b[0, 0], b[0, 1], b[0, 2])
        result += "               % 18.13f% 18.13f% 18.12f\n" % (b[1, 0], b[1, 1], b[1, 2])
        result += "               % 18.13f% 18.13f% 18.12f\n" % (b[2, 0], b[2, 1], b[2, 2])    
        return result
    
    def getLattice(self):
        return(self._name, self._a1, self._a2, self._a3, self._alpha1 * TODEG, self._alpha2 * TODEG, self._alpha3 * TODEG)

    def getStateDict(self):
        return {
            'name': self._name,
            'a' : self._a1,
            'b' : self._a2,
            'c' : self._a3,
            'alpha' : self._alpha1 * TODEG,
            'beta' : self._alpha2 * TODEG,
            'gamma':self._alpha3 * TODEG
        }
