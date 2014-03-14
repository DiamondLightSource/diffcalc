###
# Copyright 2008-2011 Diamond Light Source Ltd.
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

from math import pi, acos, cos, sin
from functools import wraps
import textwrap

try:
    from gda.jython.commands.InputCommands import requestInput as raw_input
except ImportError:
    pass  # raw_input unavailable in gda
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


RAISE_EXCEPTIONS_FOR_ALL_ERRORS = False
DEBUG = False


class ExternalCommand(object):
    """Instances found in a command_list by format_command_help will
    result in documentation for a command without there actually being one.
    """
    def __init__(self, docstring):
        """Set the docstring that will be pulled off by format_command_help.
        """
        self.__doc__ = docstring
        self.__name__ = ''


def format_command_help(command_list):
    lines = []
    for obj in command_list:

        if isinstance(obj, basestring):  # group heading
            lines.extend(['', obj.upper(), ''])

        else:  # individual command
            doc_before_empty_line = obj.__doc__.split('\n\n')[0]
            doc_lines = [s.strip() for s in doc_before_empty_line.split('\n')]
            for doc_line in doc_lines:
                if doc_line == '':
                    continue
                name, args, desc = _split_doc_line(doc_line)
                desc_lines = textwrap.wrap(desc, 45)
                line = ('   ' + name + ' ' + args).ljust(35)
                if obj.__name__ in ('ub', 'hkl'):
                    continue
                if not desc_lines:
                    raise AssertionError()
                if len(line) <= 35:
                    line += (desc_lines.pop(0))  # first line
                lines.append(line)
                for desc_line in desc_lines:
                    lines.append(' ' * 35 + desc_line)
#                lines.append('')
    return '\n'.join(lines)


def _split_doc_line(docLine):
    name, _, right = docLine.partition(' ')
    args, _, desc = right.partition('-- ')
    return name, args, desc


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
    except TypeError:
        # NOTE: TypeErrors resulting from bugs in the core code will be
        # erroneously caught here! TODO: check depth of TypeError stack
        raise TypeError('\n\nUSAGE:\n' + f.__doc__)
    except DiffcalcException, e:
        # TODO: log and create a new one to shorten stack trace for user
        raise DiffcalcException(e.message)
