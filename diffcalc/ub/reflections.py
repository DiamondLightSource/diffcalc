from copy import deepcopy
import datetime  # @UnusedImport for the eval below

from diffcalc.utils import DiffcalcException
from diffcalc.hkl.vlieg.position import VliegPosition


class Reflection:
    """A reflection"""
    def __init__(self, h, k, l, position, energy, tag, time):

        self.h = float(h)
        self.k = float(k)
        self.l = float(l)
        self.pos = position
        self.tag = tag
        self.energy = float(energy)      # energy=12.39842/lambda
        self.wavelength = 12.3984 / self.energy
        self.time = time

    def __str__(self):
        return ("energy=%-6.3f h=%-4.2f k=%-4.2f l=%-4.2f  alpha=%-8.4f "
                "delta=%-8.4f gamma=%-8.4f omega=%-8.4f chi=%-8.4f "
                "phi=%-8.4f  %-s %s" % (self.energy, self.h, self.k, self.l,
                self.pos.alpha, self.pos.delta, self.pos.gamma, self.pos.omega,
                self.pos.chi, self.pos.phi, self.tag, self.time))

    def getStateDict(self):
        return {
            'h': self.h,
            'k': self.k,
            'l': self.l,
            'position': self.pos.totuple(),
            'energy': self.energy,
            'tag': self.tag,
            'time': self.time
        }


class ReflectionList:

    def __init__(self, diffractometerPluginObject, externalAngleNames):
        self._geometry = diffractometerPluginObject
        self._reflist = []   # Will be a list of Reflections
        self._externalAngleNames = externalAngleNames

    def addReflection(self, h, k, l, position, energy, tag, time):
        """adds a reflection, position in degrees
        """
        if type(position) in (list, tuple):
            try:
                position = self._geometry.create_position(*position)
            except AttributeError:
                position = VliegPosition(*position)
        self._reflist += [Reflection(h, k, l, position, energy, tag,
                                     time.__repr__())]

    def editReflection(self, num, h, k, l, position, energy, tag, time):
        """num starts at 1"""
        if type(position) in (list, tuple):
            position = VliegPosition(*position)
        try:
            self._reflist[num - 1] = Reflection(h, k, l, position, energy, tag,
                                                time.__repr__())
        except IndexError:
            raise DiffcalcException("There is no reflection " + repr(num)
                                     + " to edit.")

    def getReflection(self, num):
        """
        getReflection(num) --> ( [h, k, l], position, energy, tag, time ) --
        num starts at 1 position in degrees
        """
        r = deepcopy(self._reflist[num - 1])  # for convenience
        return [r.h, r.k, r.l], deepcopy(r.pos), r.energy, r.tag, eval(r.time)

    def getReflectionInExternalAngles(self, num):
        """getReflection(num) --> ( [h, k, l], (angle1...angleN), energy, tag )
        -- num starts at 1 position in degrees"""
        r = deepcopy(self._reflist[num - 1])  # for convenience
        externalAngles = self._geometry.internalPositionToPhysicalAngles(r.pos)
        result = [r.h, r.k, r.l], externalAngles, r.energy, r.tag, eval(r.time)
        return result

    def removeReflection(self, num):
        del self._reflist[num - 1]

    def swapReflections(self, num1, num2):
        orig1 = self._reflist[num1 - 1]
        self._reflist[num1 - 1] = self._reflist[num2 - 1]
        self._reflist[num2 - 1] = orig1

    def __len__(self):
        return len(self._reflist)

    def __str__(self):
        return self.toStringWithExternalAngles()

    def toStringWithExternalAngles(self):
        circleNames = self._externalAngleNames
        format = ("      %-6s %-4s %-4s %-4s  " + "%-8s " * len(circleNames) +
                  " tag\n")
        values = ('energy', 'h', 'k', 'l') + circleNames

        result = format % values
        #if len(self._reflist)==0:
        #    result += "<<empty>>"
        for n in range(len(self._reflist)):
            [h, k, l], externalAngles, energy, tag, _ = \
                self.getReflectionInExternalAngles(n + 1)
            if tag is None:
                tag = ""
            format = ("   %-2d %-6.3f %-4.2f %-4.2f %-4.2f  " +
                      "%-8.4f " * len(circleNames) + " %-s\n")
            values = (n + 1, energy, h, k, l) + externalAngles + (tag,)
            result += format % values
        return result

    def soStringWithInternalAngles(self):
        toReturn = ("      %-6s %-4s %-4s %-4s  %-8s %-8s %-8s %-8s %-8s %-8s "
                    " tag\n" % ('energy', 'h', 'k', 'l', 'alpha', 'delta',
                    'gamma', 'omega', 'chi', 'phi'))
        for n in range(len(self._reflist)):
            ref = self._reflist[n]
            pos = ref.pos
            if ref.tag is None:
                tag = ""
            else:
                tag = ref.tag
            toReturn += ("   %-2d %-6.3f %-4.2f %-4.2f %-4.2f  %-8.4f %-8.4f "
                         "%-8.4f %-8.4f %-8.4f %-8.4f  %-s\n" %
                         (n + 1, ref.energy, ref.h, ref.k, ref.l, pos.alpha,
                         pos.delta, pos.gamma, pos.omega, pos.chi, pos.phi,
                         tag))
        return toReturn

    def getStateDict(self):
        """returns dict of form:
        {
        'ref_0' : reflectionDict0,
        'ref_1' : reflectionDict1 ...
        }
        """
        state = {}
        for n, ref in enumerate(self._reflist):
            state['ref_' + str(n)] = ref.getStateDict()
        return state

    def restoreFromStateDict(self, dictOfReflectionDicts):
        keys = dictOfReflectionDicts.keys()
        keys.sort()
        for key in keys:
            reflectionDict = dictOfReflectionDicts[key]
            reflectionDict['time'] = eval(reflectionDict['time'])
            self.addReflection(**reflectionDict)
