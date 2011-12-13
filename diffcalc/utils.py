try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix
try:
    from gda.jython.commands.InputCommands import requestInput as raw_input
except ImportError:
    pass # raw_input won't work in the gda so use this instead (if it is there)
from math import cos, sin, pi, acos


MIRROR = Matrix([[1, 0, 0],
                 [0, -1, 0],
                 [0, 0, 1]
                ])

# from http://physics.nist.gov/
h_in_eV_per_s = 4.135667516E-15
c = 299792458
TWELVEISH = c * h_in_eV_per_s#12.39842


SMALL = 1e-10
TORAD = pi / 180
TODEG = 180 / pi

class Position(object):
    """The position of all six diffractometer axis"""
    def __init__(self, alpha_mu=None, delta=None, gamma_nu=None, omega_eta=None, chi=None, phi=None):
        self._alpha_mu = alpha_mu
        self.delta = delta
        self._gamma_nu = gamma_nu
        self._omega_eta = omega_eta
        self.chi = chi
        self.phi = phi
        self.is_you = False
    
    def _get_alpha_mu(self):
        return self._alpha_mu
    
    def _set_alpha_mu(self, alpha_mu):
        self._alpha_mu = alpha_mu
        
    def _get_gamma_nu(self):
        return self._gamma_nu

    def _set_gamma_nu(self, gamma_nu):
        self._gamma_nu = gamma_nu    
        
    def _get_omega_eta(self):
        return self._omega_eta
    
    def _set_omega_eta(self, omega_eta):
        self._omega_eta = omega_eta
        
    alpha = mu = property(_get_alpha_mu, _set_alpha_mu)
    
    gamma = nu = property(_get_gamma_nu, _set_gamma_nu)
    
    omega = eta = property(_get_omega_eta, _set_omega_eta)
        
    
    def clone(self):
        return Position(self._alpha_mu, self.delta, self._gamma_nu, self._omega_eta, self.chi, self.phi)
        
    def changeToRadians(self):
        self._alpha_mu *= TORAD
        self.delta *= TORAD
        self._gamma_nu *= TORAD
        self._omega_eta *= TORAD
        self.chi *= TORAD
        self.phi *= TORAD

    def changeToDegrees(self):
        self._alpha_mu *= TODEG
        self.delta *= TODEG
        self._gamma_nu *= TODEG
        self._omega_eta *= TODEG
        self.chi *= TODEG
        self.phi *= TODEG
        
    def inRadians(self):
        pos = self.clone()
        pos.changeToRadians()
        return pos
        
    def inDegrees(self):
        pos = self.clone()
        pos.changeToDegrees()
        return pos

    def nearlyEquals(self, pos2, maxnorm):
        pos1 = Matrix([[self._alpha_mu, self.delta, self._gamma_nu, self._omega_eta, self.chi, self.phi]])
        pos2 = Matrix([[pos2._alpha_mu, pos2.delta, pos2._gamma_nu, pos2._omega_eta, pos2.chi, pos2.phi]])
        return pos1.minus(pos2).normF() <= maxnorm
    
    def totuple(self):
        return (self._alpha_mu, self.delta, self._gamma_nu, self._omega_eta, self.chi, self.phi)
    
    def __str__(self):
        return "Position(alpha %s delta: %s gamma: %s omega: %s chi: %s  phi: %s)" % \
              (`self._alpha_mu`, `self.delta`, `self._gamma_nu`, `self._omega_eta`, `self.chi`, `self.phi`)
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, b):
        return self.nearlyEquals(b, .001)

class YouPosition(Position):
    
        def __init__(self, mu=None, delta=None, nu=None, eta=None, chi=None, phi=None):
            Position.__init__(self, mu, delta, nu, eta, chi, phi)

        def __str__(self):
            return "Position(mu: %s delta: %s nu: %s eta: %s chi: %s  phi: %s)" % \
                  (`self._alpha_mu`, `self.delta`, `self._gamma_nu`, `self._omega_eta`, `self.chi`, `self.phi`)
                  
        def clone(self):
            return YouPosition(self._alpha_mu, self.delta, self._gamma_nu, self._omega_eta, self.chi, self.phi)
        

class DiffcalcException(Exception):
    "Error caused by user misuse of diffraction calculator"

# TODO: Remove (nasty) check function
def check(condition, ErrorOrStringOrCallable, *args):
    """fail = check(condition, ErrorOrString) -- if condition is false raises the Exception
    passed in, or creates one from a string. If a callable function is passed in this is
    called with any args specified and the thing returns false.
    """
    if condition == False:
        if callable(ErrorOrStringOrCallable):
            ErrorOrStringOrCallable(*args)
            return False
        elif isinstance(ErrorOrStringOrCallable, str):
            raise Exception(ErrorOrStringOrCallable)
        else: # assume input is an exception
            raise ErrorOrStringOrCallable
    return True

def bound(x):
    """
    moves x between -1 and 1. Used to correct for rounding errors which may have moved
    the sin or cosine of a value outside this range.
    """
    if abs(x) > (1 + SMALL):
        raise AssertionError(
"""The value (%f) was unexpectedly too far outside -1 or 1 to safely bound.
Please report this.""" % x)
    if x > 1: return 1
    if x < -1: return -1
    return x


        
def cross3(x, y):
    """z = cross3(x ,y) -- where x, y & z are 3*1 Jama matrices"""
    [[x1], [x2], [x3]] = x.getArray()
    [[y1], [y2], [y3]] = y.getArray()
    return Matrix([[x2 * y3 - x3 * y2], [x3 * y1 - x1 * y3], [x1 * y2 - x2 * y1]])

def dot3(x, y):
    """z = dot3(x ,y) -- where x, y are 3*1 Jama matrices"""
    [[x1], [x2], [x3]] = x.getArray()
    [[y1], [y2], [y3]] = y.getArray()
    return x1 * y1 + x2 * y2 + x3 * y3

def angle_between_vectors(a, b):
    costheta = dot3(a.times(1 / a.normF()), b.times(1 / b.normF()))
    return acos(bound(costheta))

#H. You's matrices

def x_rotation(th):
    return Matrix(((1, 0, 0), (0, cos(th), -sin(th)), (0, sin(th), cos(th))))

def y_rotation(th):
    return Matrix(((cos(th), 0, sin(th)), (0, 1, 0), (-sin(th), 0, cos(th))))

def z_rotation(th):
    return Matrix(((cos(th), -sin(th), 0), (sin(th), cos(th), 0), (0, 0, 1)))


def createYouMatrices(mu=None, delta=None, nu=None, eta=None, chi=None, phi=None):
    """    
    Return transformation matrices from H. You's paper.
    """    
    MU = None if mu is None else calcMU(mu)
    DELTA = None if delta is None else calcDELTA(delta)
    NU = None if nu is None else calcNU(nu)
    ETA = None if eta is None else calcETA(eta)
    CHI = None if chi is None else calcCHI(chi)
    PHI = None if phi is None else calcPHI(phi)
    return MU, DELTA, NU, ETA, CHI, PHI


def calcNU(nu):
    return x_rotation(nu)

def calcDELTA(delta):
    return z_rotation(-delta)

def calcMU(mu_or_alpha):
    return x_rotation(mu_or_alpha)

def calcETA(eta):
    return z_rotation(-eta)

def calcCHI(chi):
    return y_rotation(chi)

def calcPHI(phi):
    return z_rotation(-phi)

def createVliegMatrices(alpha=None, delta=None, gamma=None, omega=None, chi=None, phi=None):
    """[ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI] =     
    createVliegMatrices(self, alpha, delta, gamma, omega, chi, phi)
    
    angles in radians
    """
    ALPHA = None if alpha is None else calcALPHA(alpha)
    DELTA = None if delta is None else calcDELTA(delta)
    GAMMA = None if gamma is None else calcGAMMA(gamma)
    OMEGA = None if omega is None else calcOMEGA(omega)
    CHI = None if chi is None else calcCHI(chi)
    PHI = None if phi is None else calcPHI(phi)
    return ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI

calcALPHA = calcNU

calcOMEGA = calcETA

def calcGAMMA(gamma):
    return Matrix([[1, 0, 0], [0, cos(gamma), -sin(gamma)], [0, sin(gamma), cos(gamma)] ])

def createVliegsSurfaceTransformationMatrices(sigma, tau):
    """[SIGMA, TAU] = createVliegsSurfaceTransformationMatrices(sigma, tau)
    angles in radians
    """
    SIGMA = Matrix([[cos(sigma), 0, sin(sigma)], \
                    [0, 1, 0], \
                    [-sin(sigma), 0, cos(sigma)] ])
        
    TAU = Matrix([[cos(tau), sin(tau) , 0], \
                  [-sin(tau), cos(tau), 0], \
                  [0, 0, 1] ])
    return(SIGMA, TAU)

def createVliegsPsiTransformationMatrix(psi):
    """PSI = createPsiTransformationMatrices(psi)
    angles in radians
    """
    return Matrix([[1, 0, 0], \
                   [0, cos(psi), sin(psi)], \
                   [0, -sin(psi), cos(psi) ]])

def matrixToString(m):
    ''' str = matrixToString(m) --- displays a Jama matrix m as a string
    '''
    toReturn = ''
    for row in m.array:
        for el in row:
            toReturn += str(el) + '\t'
        toReturn += '\n'
    return toReturn

def sign(x):
    if x < 0:
        return -1
    else:
        return 1
    
    
RECORDFILE = None #Hack!
def getInputWithDefault(prompt, default=""):
    """Prompts user for input and returns if possible a float or a list of floats,
    or if failing this a string.    default may be a number, array of numbers, or string.
    """
    if default is not "":
        # Generate default string
        if type(default) in (list, tuple):
            defaultString = ""
            for val in default:
                defaultString += str(val) + ' '
            defaultString = defaultString.strip()
        else:
            defaultString = str(default)
        prompt = str(prompt) + '[' + defaultString + ']: '
    else:
        prompt = str(prompt) + ': '
        
    rawresult = raw_input(prompt)
    if RECORDFILE:
        RECORDFILE.write(rawresult + "\n")
    
    # Return default if no input provided
    if rawresult == "":
        return default
    
    # Try to process result into list of numbers
    try:
        result = []
        for val in rawresult.split():
            result.append(float(val))
    except ValueError:
        # return a string
        return rawresult
    if len(result) == 1:
        result = result[0]
    return result

class MockRawInput(object):
    def __init__(self, toReturnList):
        if type(toReturnList) != list:
            toReturnList = [toReturnList]
        self.toReturnList = toReturnList

    def __call__(self, prompt):
        toReturn = self.toReturnList.pop(0)
        if type(toReturn) != str:
            raise TypeError
        print prompt + toReturn
        return toReturn

def getMessageFromException(e):
    try: # Jython
        return e.args[0]
    except:
        try: # Python
            return e.message
        except:
            # Java
            return e.args[0]

def nearlyEqual(first, second, tolerance):
    if type(first) in (int, float):
        return abs(first - second) <= tolerance
    
    if type(first) != type(Matrix([[1]])):
        # lists
        first = Matrix([list(first)])
        second = Matrix([list(second)])
    diff = first.minus(second)
    return diff.normF() <= tolerance

def radiansEquivilant(first, second, tolerance):
    if abs(first - second) <= tolerance:
        return True
    if abs((first - 2 * pi) - second) <= tolerance:
        return True    
    if abs((first + 2 * pi) - second) <= tolerance:
        return True
    if abs(first - (second - 2 * pi)) <= tolerance:
        return True    
    if abs(first - (second + 2 * pi)) <= tolerance:
        return True
    
    return False
    
def degreesEquivilant(first, second, tolerance):
    return radiansEquivilant(first * TORAD, second * TORAD, tolerance)
    
def differ(first, second, tolerance):
        """Returns error message if the norm of the difference between two arrays
        or numbers is greater than the given tolerance. Else returns False.
        """
        # TODO: Fix spaghetti
        nonArray = False
        if type(first) in (int, float):
            if type(second) not in (int, float):
                raise TypeError, "If first is an int or float, so must second. first=%s, second=%s" & (`first`, `second`)
            first = [first]
            second = [second]
            nonArray = True
        if not isinstance(first, Matrix):
            first = Matrix([list(first)])
        if not isinstance(second, Matrix):
            second = Matrix([list(second)])
        diff = first.minus(second)
        if diff.normF() >= tolerance:
            if nonArray:
                return '%s!=%s' % (`first.array[0][0]`, `second.array[0][0]`)
            return '%s!=%s' % (`tuple(first.array[0])`, `tuple(second.array[0])`)
        return False

def promptForNumber(prompt, default=""):
    val = getInputWithDefault(prompt, default)
    if type(val) not in (float, int):
        return None
    return val

def promptForList(prompt, default=""):
    val = getInputWithDefault(prompt, default)
    if type(val) not in (list, tuple):
        return None
    return val

def isnum(o):
    return isinstance(o, (int, float))

def allnum(l):
    return not [o for o in l if not isnum(o)]

## http://docs.python.org/dev/library/collections.html#ordereddict-objects
## {{{ http://code.activestate.com/recipes/576693/ (r6)
from UserDict import DictMixin

class OrderedDict(dict, DictMixin):

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__end
        except AttributeError:
            self.clear()
        self.update(*args, **kwds)

    def clear(self):
        self.__end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.__map = {}                 # key --> [key, prev, next]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            end = self.__end
            curr = end[1]
            curr[2] = end[1] = self.__map[key] = [key, curr, end]
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        key, prev, next = self.__map.pop(key)
        prev[2] = next
        next[1] = prev

    def __iter__(self):
        end = self.__end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.__end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        if last:
            key = reversed(self).next()
        else:
            key = iter(self).next()
        value = self.pop(key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__end
        del self.__map, self.__end
        inst_dict = vars(self).copy()
        self.__map, self.__end = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def keys(self):
        return list(self)

    setdefault = DictMixin.setdefault
    update = DictMixin.update
    pop = DictMixin.pop
    values = DictMixin.values
    items = DictMixin.items
    iterkeys = DictMixin.iterkeys
    itervalues = DictMixin.itervalues
    iteritems = DictMixin.iteritems

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            return len(self) == len(other) and self.items() == other.items()
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other
## end of http://code.activestate.com/recipes/576693/ }}}
