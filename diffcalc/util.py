###
# Copyright 2008-2019 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

import os
from math import pi, acos, cos, sin, sqrt
from functools import wraps
import textwrap

GDA = os.name == 'java'

try:
    from numpy import matrix
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix
    from numjy.linalg import norm


# from http://physics.nist.gov/
h_in_eV_per_s = 4.135667516E-15
c = 299792458
TWELVEISH = c * h_in_eV_per_s  # 12.39842


SMALL = 1e-10
TORAD = pi / 180
TODEG = 180 / pi


COLOURISE_TERMINAL_OUTPUT = not GDA

def bold(s):
    if not COLOURISE_TERMINAL_OUTPUT:
        return s
    else:    
        BOLD = '\033[1m'
        END = '\033[0m'
        return BOLD + s + END


def x_rotation(th):
    return matrix(((1, 0, 0), (0, cos(th), -sin(th)), (0, sin(th), cos(th))))


def y_rotation(th):
    return matrix(((cos(th), 0, sin(th)), (0, 1, 0), (-sin(th), 0, cos(th))))


def z_rotation(th):
    return matrix(((cos(th), -sin(th), 0), (sin(th), cos(th), 0), (0, 0, 1)))


def xyz_rotation(u, angle):
    u = [list(u), [0, 0, 0], [0, 0, 0]]
    u = matrix(u) / norm(matrix(u))
    e11=u[0,0]**2+(1-u[0,0]**2)*cos(angle)
    e12=u[0,0]*u[0,1]*(1-cos(angle))-u[0,2]*sin(angle)
    e13=u[0,0]*u[0,2]*(1-cos(angle))+u[0,1]*sin(angle)
    e21=u[0,0]*u[0,1]*(1-cos(angle))+u[0,2]*sin(angle)
    e22=u[0,1]**2+(1-u[0,1]**2)*cos(angle)
    e23=u[0,1]*u[0,2]*(1-cos(angle))-u[0,0]*sin(angle)
    e31=u[0,0]*u[0,2]*(1-cos(angle))-u[0,1]*sin(angle)
    e32=u[0,1]*u[0,2]*(1-cos(angle))+u[0,0]*sin(angle)
    e33=u[0,2]**2+(1-u[0,2]**2)*cos(angle)
    return matrix([[e11,e12,e13],[e21,e22,e23],[e31,e32,e33]])


class CoordinateConverter(object):
    """Class for converting matrix objects between coordinate frames"""

    def __init__(self, transform=None):
        if transform is None:
            self.R = None
        elif type(transform) in (list, tuple, matrix):
            self.R = matrix(transform)
            self.nrow, self.ncol = self.R.shape
            if self.nrow != self.ncol:
                raise TypeError('Transformation matrix shape is invalid: %d x %d' % (self.nrow, self.ncol))
        else:
            raise TypeError('Invalid object type %s' % str(type(transform)))

    def transform(self, v, inv=False):
        if type(v) in (list, tuple, matrix):
            m = matrix(v)
        else:
            raise TypeError('Invalid object type %s' % str(type(m)))
        if self.R is None:
            return m
        nr, nc = m.shape
        if nc == 1:
            if nr != self.nrow:
                raise TypeError('Invalid number of rows: %d != %d'% (nr, self.nrow))
            if inv:
                return self.R.I * m
            else:
                return self.R * m
        elif nr == 1:
            if nc != self.ncol:
                raise TypeError('Invalid number of columns: %d != %d' % (nc, self.ncol))
            if inv:
                return m * self.R.I
            else:
                return m * self.R
        elif m.shape == self.R.shape:
            if inv:
                return self.R.I * m * self.R
            else:
                return self.R * m * self.R.I
        raise TypeError('Invalid matrix shape: %d x %d' % (nr, nc))


class DiffcalcException(Exception):
    """Error caused by user misuse of diffraction calculator.
    """
    def __str__(self):
        lines = []
        for msg_line in self.message.split('\n'):
            lines.append('* ' + msg_line)
        width = max(len(l) for l in lines)
        lines.insert(0, '\n\n' + '*' * width)
        lines.append('*' * width)
        return '\n'.join(lines)


class AbstractPosition(object):

    def inRadians(self):
        pos = self.clone()
        pos.changeToRadians()
        return pos

    def inDegrees(self):
        pos = self.clone()
        pos.changeToDegrees()
        return pos

    def changeToRadians(self):
        raise NotImplementedError()

    def changeToDegrees(self):
        raise NotImplementedError()

    def totuple(self):
        raise NotImplementedError()


### Matrices

def cross3(x, y):
    """z = cross3(x ,y) -- where x, y & z are 3*1 Jama matrices"""
    [[x1], [x2], [x3]] = x.tolist()
    [[y1], [y2], [y3]] = y.tolist()
    return matrix([[x2 * y3 - x3 * y2],
                   [x3 * y1 - x1 * y3],
                   [x1 * y2 - x2 * y1]])


def dot3(x, y):
    """z = dot3(x ,y) -- where x, y are 3*1 Jama matrices"""
    return x[0, 0] * y[0, 0] + x[1, 0] * y[1, 0] + x[2, 0] * y[2, 0]


def norm3(x):
    """z = norm3(x) -- where x is 3*1 Jama matrix"""
    return norm(x)


def angle_between_vectors(a, b):
    costheta = dot3(a * (1 / norm(a)), b * (1 / norm(b)))
    return acos(bound(costheta))


## Math

def bound(x):
    """
    moves x between -1 and 1. Used to correct for rounding errors which may
    have moved the sin or cosine of a value outside this range.
    """
    if abs(x) > (1 + SMALL):
        raise AssertionError(
            "The value (%f) was unexpectedly too far outside -1 or 1 to "
            "safely bound. Please report this." % x)
    if x > 1:
        return 1
    if x < -1:
        return -1
    return x


def matrixToString(m):
    ''' str = matrixToString(m) --- displays a Jama matrix m as a string
    '''
    toReturn = ''
    for row in m.array:
        for el in row:
            toReturn += str(el) + '\t'
        toReturn += '\n'
    return toReturn


def nearlyEqual(first, second, tolerance):
    if type(first) in (int, float):
        return abs(first - second) <= tolerance

    if type(first) != type(matrix([[1]])):
        # lists
        first = matrix([list(first)])
        second = matrix([list(second)])
    diff = first - (second)
    return norm(diff) <= tolerance


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
            raise TypeError(
                "If first is an int or float, so must second. "
                "first=%s, second=%s" & (repr(first), repr(second)))
        first = [first]
        second = [second]
        nonArray = True
    if not isinstance(first, matrix):
        first = matrix([list(first)])
    if not isinstance(second, matrix):
        second = matrix([list(second)])
    diff = first - second
    if norm(diff) >= tolerance:
        if nonArray:
            return ('%s!=%s' %
                    (repr(first.tolist()[0][0]), repr(second.tolist()[0][0])))
        return ('%s!=%s' %
                (repr(tuple(first.tolist()[0])),
                repr(tuple(second.tolist()[0]))))
    return False


### user input

def getInputWithDefault(prompt, default=""):
    """
    Prompts user for input and returns if possible a float or a list of floats,
    or if failing this a string.    default may be a number, array of numbers,
    or string.
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
    try:  # Jython
        return e.args[0]
    except:
        try:  # Python
            return e.message
        except:
            # Java
            return e.args[0]


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


DEBUG = False



def command(f):
    """A decorator to wrap a command method or function.

    Calls to the decorated method or function are wrapped by call_command.
    """
    # TODO: remove one level of stack trace by not using wraps
    @wraps(f)
    def wrapper(*args, **kwds):
        return call_command(f, args)

    return wrapper


def call_command(f, args):

    if DEBUG:
        return f(*args)
    try:
        return f(*args)
    except TypeError, e:
        # NOTE: TypeErrors resulting from bugs in the core code will be
        # erroneously caught here! TODO: check depth of TypeError stack
        raise TypeError(e.message + '\n\nUSAGE:\n' + f.__doc__)
    except DiffcalcException, e:
        # TODO: log and create a new one to shorten stack trace for user
        raise DiffcalcException(e.message)

def solve_h_fixed_q(h, qval, B, coeff):
    '''Find list of all hkl values with a given h and scattering vector amplitude
    that match linear hkl constraint a*h + b*k + c*l = d'''
    B00, B10, B20 = B[0,0], B[1,0], B[2,0]
    B01, B11, B21 = B[0,1], B[1,1], B[2,1]
    B02, B12, B22 = B[0,2], B[1,2], B[2,2]
    a, b, c, d = coeff
    if b != 0:
        try:
            l1 = -(((B01*B02 + B11*B12 + B21*B22)*b - (B01**2 + B11**2 + B21**2)*c)*d - \
                  ((B01*B02 + B11*B12 + B21*B22)*a*b - (B00*B02 + B10*B12 + B20*B22)*b**2 - \
                   ((B01**2 + B11**2 + B21**2)*a - (B00*B01 + B10*B11 + B20*B21)*b)*c)*h + \
                  sqrt(-(B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                         2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*d**2 + \
                         2*((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                             2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a - \
                             (B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*b + \
                             (B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                              (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                              ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*c)*d*h - \
                         ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                           2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                           2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                           (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                            2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                           (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                            2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                           2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                               (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                               ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                               (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*h**2 + \
                         ((B02**2 + B12**2 + B22**2)*b**2 - 2*(B01*B02 + B11*B12 + B21*B22)*b*c + \
                          (B01**2 + B11**2 + B21**2)*c**2)*qval)*b)/((B02**2 + B12**2 + B22**2)*b**2 - \
                                                                     2*(B01*B02 + B11*B12 + B21*B22)*b*c + (B01**2 + B11**2 + B21**2)*c**2)
            l2 = -(((B01*B02 + B11*B12 + B21*B22)*b - (B01**2 + B11**2 + B21**2)*c)*d - \
                    ((B01*B02 + B11*B12 + B21*B22)*a*b - (B00*B02 + B10*B12 + B20*B22)*b**2 - \
                     ((B01**2 + B11**2 + B21**2)*a - (B00*B01 + B10*B11 + B20*B21)*b)*c)*h - \
                    sqrt(-(B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                           2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*d**2 + \
                           2*((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                               2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a - \
                               (B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                                (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                                ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*b + \
                               (B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                                (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                                ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*c)*d*h - \
                           ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                             2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                             2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                                (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                                ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                             (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                              2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                             (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                              2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                             2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                                 (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                                 ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                                 (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                  (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                  ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*h**2 + \
                           ((B02**2 + B12**2 + B22**2)*b**2 - 2*(B01*B02 + B11*B12 + B21*B22)*b*c + \
                            (B01**2 + B11**2 + B21**2)*c**2)*qval)*b)/((B02**2 + B12**2 + B22**2)*b**2 - \
                                                                       2*(B01*B02 + B11*B12 + B21*B22)*b*c + (B01**2 + B11**2 + B21**2)*c**2)
            k1 = (d - a * h - c * l1) / b
            k2 = (d - a * h - c * l2) / b
            return [(h, k1 ,l1), (h, k2, l2)]
        except ValueError:
            raise DiffcalcException("Couldn't find solution for h=%f with the given hkl constraints" % h)
    elif c != 0:
        try:
            k1 = (((B02**2 + B12**2 + B22**2)*b - (B01*B02 + B11*B12 + B21*B22)*c)*d - \
                  ((B02**2 + B12**2 + B22**2)*a*b + (B00*B01 + B10*B11 + B20*B21)*c**2 - \
                   ((B01*B02 + B11*B12 + B21*B22)*a + (B00*B02 + B10*B12 + B20*B22)*b)*c)*h - \
                  sqrt(-(B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                         2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*d**2 + \
                         2*((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                             2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a - \
                             (B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*b + \
                             (B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                              (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                              ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*c)*d*h - \
                         ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                           2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                           2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                           (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                            2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                           (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                            2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                           2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                               (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                               ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                               (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*h**2 + \
                         ((B02**2 + B12**2 + B22**2)*b**2 - 2*(B01*B02 + B11*B12 + B21*B22)*b*c + \
                          (B01**2 + B11**2 + B21**2)*c**2)*qval)*c)/((B02**2 + B12**2 + B22**2)*b**2 - \
                                                                     2*(B01*B02 + B11*B12 + B21*B22)*b*c + (B01**2 + B11**2 + B21**2)*c**2)
            k2 = (((B02**2 + B12**2 + B22**2)*b - (B01*B02 + B11*B12 + B21*B22)*c)*d - \
                  ((B02**2 + B12**2 + B22**2)*a*b + (B00*B01 + B10*B11 + B20*B21)*c**2 - \
                   ((B01*B02 + B11*B12 + B21*B22)*a + (B00*B02 + B10*B12 + B20*B22)*b)*c)*h + \
                  sqrt(-(B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                         2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*d**2 + \
                         2*((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                             2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a - \
                             (B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*b + \
                             (B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                              (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                              ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*c)*d*h - \
                         ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                           2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                           2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                           (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                            2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                           (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                            2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                           2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                               (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                               ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                               (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*h**2 + \
                         ((B02**2 + B12**2 + B22**2)*b**2 - 2*(B01*B02 + B11*B12 + B21*B22)*b*c + \
                          (B01**2 + B11**2 + B21**2)*c**2)*qval)*c)/((B02**2 + B12**2 + B22**2)*b**2 - \
                                                                     2*(B01*B02 + B11*B12 + B21*B22)*b*c + (B01**2 + B11**2 + B21**2)*c**2)
            l1 = (d - a * h - b * k1) / c
            l2 = (d - a * h - b * k2) / c
            return [(h, k1 ,l1), (h, k2, l2)]
        except ValueError:
            raise DiffcalcException("Couldn't find solution for h=%f with the given hkl constraints" % h)
    else:
        raise DiffcalcException("Value of h is fixed to a constant by the constraint on hkl")

def solve_k_fixed_q(k, qval, B, coeff):
    '''Find list of all hkl values with a given k and scattering vector amplitude
    that match linear hkl constraint a*h + b*k + c*l = d'''
    B00, B10, B20 = B[0,0], B[1,0], B[2,0]
    B01, B11, B21 = B[0,1], B[1,1], B[2,1]
    B02, B12, B22 = B[0,2], B[1,2], B[2,2]
    a, b, c, d = coeff
    if a != 0:
        try:
            l1 = -(((B00*B02 + B10*B12 + B20*B22)*a - (B00**2 + B10**2 + B20**2)*c)*d + \
                   ((B01*B02 + B11*B12 + B21*B22)*a**2 - (B00*B02 + B10*B12 + B20*B22)*a*b - \
                    ((B00*B01 + B10*B11 + B20*B21)*a - (B00**2 + B10**2 + B20**2)*b)*c)*k + \
                   sqrt(-(B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                          2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*d**2 - \
                          2*((B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a - \
                              (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                               2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b + \
                              (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                               (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                               ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*c)*d*k - \
                          ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                            2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                            2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                               (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                               ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                            (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                             2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                            (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                             2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                            2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                                (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                                ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                                (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                 (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                 ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*k**2 + \
                          ((B02**2 + B12**2 + B22**2)*a**2 - 2*(B00*B02 + B10*B12 + B20*B22)*a*c + \
                           (B00**2 + B10**2 + B20**2)*c**2)*qval)*a)/((B02**2 + B12**2 + B22**2)*a**2 - \
                                                                      2*(B00*B02 + B10*B12 + B20*B22)*a*c + (B00**2 + B10**2 + B20**2)*c**2)
            l2 = -(((B00*B02 + B10*B12 + B20*B22)*a - (B00**2 + B10**2 + B20**2)*c)*d + \
                   ((B01*B02 + B11*B12 + B21*B22)*a**2 - (B00*B02 + B10*B12 + B20*B22)*a*b - \
                    ((B00*B01 + B10*B11 + B20*B21)*a - (B00**2 + B10**2 + B20**2)*b)*c)*k - \
                   sqrt(-(B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                          2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*d**2 - \
                          2*((B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a - \
                              (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                               2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b + \
                              (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                               (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                               ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*c)*d*k - \
                          ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                            2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                            2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                               (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                               ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                            (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                             2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                            (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                             2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                            2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                                (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                                ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                                (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                 (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                 ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*k**2 + \
                          ((B02**2 + B12**2 + B22**2)*a**2 - 2*(B00*B02 + B10*B12 + B20*B22)*a*c + \
                           (B00**2 + B10**2 + B20**2)*c**2)*qval)*a)/((B02**2 + B12**2 + B22**2)*a**2 - \
                                                                      2*(B00*B02 + B10*B12 + B20*B22)*a*c + (B00**2 + B10**2 + B20**2)*c**2)
            h1 = (d - b * k - c * l1) / a
            h2 = (d - b * k - c * l2) / a
            return [(h1, k ,l1), (h2, k, l2)]
        except ValueError:
            raise DiffcalcException("Couldn't find solution for k=%f with the given hkl constraints" % k)
    elif c != 0:
        try:
            h1 = (((B02**2 + B12**2 + B22**2)*a - (B00*B02 + B10*B12 + B20*B22)*c)*d - \
                  ((B02**2 + B12**2 + B22**2)*a*b + (B00*B01 + B10*B11 + B20*B21)*c**2 - \
                   ((B01*B02 + B11*B12 + B21*B22)*a + (B00*B02 + B10*B12 + B20*B22)*b)*c)*k - \
                  sqrt(-(B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                         2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*d**2 - \
                         2*((B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                             (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                             ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a - \
                             (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                              2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b + \
                             (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                              (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                              ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*c)*d*k - \
                         ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                           2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                           2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                           (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                            2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                           (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                            2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                           2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                               (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                               ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                               (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*k**2 + \
                         ((B02**2 + B12**2 + B22**2)*a**2 - 2*(B00*B02 + B10*B12 + B20*B22)*a*c + \
                          (B00**2 + B10**2 + B20**2)*c**2)*qval)*c)/((B02**2 + B12**2 + B22**2)*a**2 - \
                                                                     2*(B00*B02 + B10*B12 + B20*B22)*a*c + (B00**2 + B10**2 + B20**2)*c**2)
            h2 = (((B02**2 + B12**2 + B22**2)*a - (B00*B02 + B10*B12 + B20*B22)*c)*d - \
                  ((B02**2 + B12**2 + B22**2)*a*b + (B00*B01 + B10*B11 + B20*B21)*c**2 - \
                   ((B01*B02 + B11*B12 + B21*B22)*a + (B00*B02 + B10*B12 + B20*B22)*b)*c)*k + \
                  sqrt(-(B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                         2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*d**2 - \
                         2*((B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                             (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                             ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a - \
                             (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                              2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b + \
                             (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                              (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                              ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*c)*d*k - \
                         ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                           2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                           2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                           (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                            2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                           (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                            2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                           2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                               (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                               ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                               (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*k**2 + \
                         ((B02**2 + B12**2 + B22**2)*a**2 - 2*(B00*B02 + B10*B12 + B20*B22)*a*c + \
                          (B00**2 + B10**2 + B20**2)*c**2)*qval)*c)/((B02**2 + B12**2 + B22**2)*a**2 - \
                                                                     2*(B00*B02 + B10*B12 + B20*B22)*a*c + (B00**2 + B10**2 + B20**2)*c**2)
            l1 = (d - a * h1 - b * k) / c
            l2 = (d - a * h2 - b * k) / c
            return [(h1, k ,l1), (h2, k, l2)]
        except ValueError:
            raise DiffcalcException("Couldn't find solution for k=%f with the given hkl constraints" % k)
    else:
        raise DiffcalcException("Value of k is fixed to a constant by the constraint on hkl")

def solve_l_fixed_q(l, qval, B, coeff):
    '''Find list of all hkl values with a given l and scattering vector amplitude
    that match linear hkl constraint a*h + b*k + c*l = d'''
    B00, B10, B20 = B[0,0], B[1,0], B[2,0]
    B01, B11, B21 = B[0,1], B[1,1], B[2,1]
    B02, B12, B22 = B[0,2], B[1,2], B[2,2]
    a, b, c, d = coeff
    if a != 0:
        try:
            k1 = -(((B00*B01 + B10*B11 + B20*B21)*a - (B00**2 + B10**2 + B20**2)*b)*d + \
                    ((B01*B02 + B11*B12 + B21*B22)*a**2 - (B00*B02 + B10*B12 + B20*B22)*a*b - \
                     ((B00*B01 + B10*B11 + B20*B21)*a - (B00**2 + B10**2 + B20**2)*b)*c)*l + \
                    sqrt(-(B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                           2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*d**2 + \
                           2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                               (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                               ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                               (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b + \
                               (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                                2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c)*d*l - \
                           ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                             2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                             2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                                (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                                ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                             (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                              2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                             (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                              2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                             2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                                 (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                                 ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                                 (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                  (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                  ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*l**2 + \
                           ((B01**2 + B11**2 + B21**2)*a**2 - 2*(B00*B01 + B10*B11 + B20*B21)*a*b + \
                            (B00**2 + B10**2 + B20**2)*b**2)*qval)*a)/((B01**2 + B11**2 + B21**2)*a**2 - \
                                                                       2*(B00*B01 + B10*B11 + B20*B21)*a*b + (B00**2 + B10**2 + B20**2)*b**2)
            k2 = -(((B00*B01 + B10*B11 + B20*B21)*a - (B00**2 + B10**2 + B20**2)*b)*d + \
                   ((B01*B02 + B11*B12 + B21*B22)*a**2 - (B00*B02 + B10*B12 + B20*B22)*a*b - \
                    ((B00*B01 + B10*B11 + B20*B21)*a - (B00**2 + B10**2 + B20**2)*b)*c)*l - \
                   sqrt(-(B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                          2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*d**2 + \
                          2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                              (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                              ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                              (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                               (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                               ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b + \
                              (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                               2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c)*d*l - \
                          ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                            2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                            2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                               (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                               ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                            (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                             2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                            (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                             2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                            2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                                (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                                ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                                (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                 (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                 ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*l**2 + \
                          ((B01**2 + B11**2 + B21**2)*a**2 - 2*(B00*B01 + B10*B11 + B20*B21)*a*b + \
                           (B00**2 + B10**2 + B20**2)*b**2)*qval)*a)/((B01**2 + B11**2 + B21**2)*a**2 - \
                                                                      2*(B00*B01 + B10*B11 + B20*B21)*a*b + (B00**2 + B10**2 + B20**2)*b**2)
            h1 = (d - b * k1 - c * l) / a
            h2 = (d - b * k2 - c * l) / a
            return [(h1, k1 ,l), (h2, k2, l)]
        except ValueError:
            raise DiffcalcException("Couldn't find solution for l=%f with the given hkl constraints" % l)
    elif b != 0:
        try:
            h1 = (((B01**2 + B11**2 + B21**2)*a - (B00*B01 + B10*B11 + B20*B21)*b)*d + \
                  ((B01*B02 + B11*B12 + B21*B22)*a*b - (B00*B02 + B10*B12 + B20*B22)*b**2 - \
                   ((B01**2 + B11**2 + B21**2)*a - (B00*B01 + B10*B11 + B20*B21)*b)*c)*l - \
                  sqrt(-(B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                         2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*d**2 + \
                         2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                             (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                             ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                             (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                              (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                              ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b + \
                             (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                              2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c)*d*l - \
                         ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                           2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                           2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                           (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                            2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                           (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                            2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                           2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                               (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                               ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                               (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*l**2 + \
                         ((B01**2 + B11**2 + B21**2)*a**2 - 2*(B00*B01 + B10*B11 + B20*B21)*a*b + \
                          (B00**2 + B10**2 + B20**2)*b**2)*qval)*b)/((B01**2 + B11**2 + B21**2)*a**2 - \
                                                                     2*(B00*B01 + B10*B11 + B20*B21)*a*b + (B00**2 + B10**2 + B20**2)*b**2)
            h2 = (((B01**2 + B11**2 + B21**2)*a - (B00*B01 + B10*B11 + B20*B21)*b)*d + \
                  ((B01*B02 + B11*B12 + B21*B22)*a*b - (B00*B02 + B10*B12 + B20*B22)*b**2 - \
                   ((B01**2 + B11**2 + B21**2)*a - (B00*B01 + B10*B11 + B20*B21)*b)*c)*l + \
                  sqrt(-(B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                         2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*d**2 + \
                         2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                             (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                             ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                             (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                              (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                              ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b + \
                             (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                              2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c)*d*l - \
                         ((B02**2*B11**2 - 2*B01*B02*B11*B12 + B01**2*B12**2 + (B02**2 + B12**2)*B21**2 - \
                           2*(B01*B02 + B11*B12)*B21*B22 + (B01**2 + B11**2)*B22**2)*a**2 - \
                           2*(B02**2*B10*B11 + B00*B01*B12**2 + (B02**2 + B12**2)*B20*B21 + \
                              (B00*B01 + B10*B11)*B22**2 - (B01*B02*B10 + B00*B02*B11)*B12 - \
                              ((B01*B02 + B11*B12)*B20 + (B00*B02 + B10*B12)*B21)*B22)*a*b + \
                           (B02**2*B10**2 - 2*B00*B02*B10*B12 + B00**2*B12**2 + (B02**2 + B12**2)*B20**2 - \
                            2*(B00*B02 + B10*B12)*B20*B22 + (B00**2 + B10**2)*B22**2)*b**2 + \
                           (B01**2*B10**2 - 2*B00*B01*B10*B11 + B00**2*B11**2 + (B01**2 + B11**2)*B20**2 - \
                            2*(B00*B01 + B10*B11)*B20*B21 + (B00**2 + B10**2)*B21**2)*c**2 + \
                           2*((B01*B02*B10*B11 - B00*B02*B11**2 + (B01*B02 + B11*B12)*B20*B21 - \
                               (B00*B02 + B10*B12)*B21**2 - (B01**2*B10 - B00*B01*B11)*B12 - \
                               ((B01**2 + B11**2)*B20 - (B00*B01 + B10*B11)*B21)*B22)*a - \
                               (B01*B02*B10**2 - B00*B02*B10*B11 + (B01*B02 + B11*B12)*B20**2 - \
                                (B00*B02 + B10*B12)*B20*B21 - (B00*B01*B10 - B00**2*B11)*B12 - \
                                ((B00*B01 + B10*B11)*B20 - (B00**2 + B10**2)*B21)*B22)*b)*c)*l**2 + \
                         ((B01**2 + B11**2 + B21**2)*a**2 - 2*(B00*B01 + B10*B11 + B20*B21)*a*b + \
                          (B00**2 + B10**2 + B20**2)*b**2)*qval)*b)/((B01**2 + B11**2 + B21**2)*a**2 - \
                                                                     2*(B00*B01 + B10*B11 + B20*B21)*a*b + (B00**2 + B10**2 + B20**2)*b**2)
            k1 = (d - a * h1 - c * l) / b
            k2 = (d - a * h2 - c * l) / b
            return [(h1, k1 ,l), (h2, k2, l)]
        except ValueError:
            raise DiffcalcException("Couldn't find solution for l=%f with the given hkl constraints" % l)
    else:
        raise DiffcalcException("Value of l is fixed to a constant by the constraint on hkl")
