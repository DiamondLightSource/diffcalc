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

from diffcalc.util import command

from copy import copy
from math import pi

from diffcalc.hkl.vlieg.geometry import VliegPosition as P

SMALL = 1e-10


class Transform(object):

    def transform(self, pos):
        raise RuntimeError('Not implemented')


### Transforms, currently for definition and testing the theory only

class TransformC(Transform):
    '''Flip omega, invert chi and flip phi
    '''
    def transform(self, pos):
        pos = pos.clone()
        pos.omega -= 180
        pos.chi *= -1
        pos.phi -= 180
        return pos


class TransformB(Transform):
    '''Flip chi, and invert and flip omega
    '''
    def transform(self, pos):
        pos = pos.clone()
        pos.chi -= 180
        pos.omega = 180 - pos.omega
        return pos


class TransformA(Transform):
    '''Invert scattering plane: invert delta and omega and flip chi'''
    def transform(self, pos):
        pos = pos.clone()
        pos.delta *= -1
        pos.omega *= -1
        pos.chi -= 180
        return pos


class TransformCInRadians(Transform):
    '''
    Flip omega, invert chi and flip phi. Using radians and keeping
    -pi<omega<=pi and 0<=phi<=360
    '''
    def transform(self, pos):
        pos = pos.clone()
        if pos.omega > 0:
            pos.omega -= pi
        else:
            pos.omega += pi
        pos.chi *= -1
        pos.phi += pi
        return pos


###

transformsFromSector = {
    0: (),
    1: ('c',),
    2: ('a',),
    3: ('a', 'c'),
    4: ('b', 'c'),
    5: ('b',),
    6: ('a', 'b', 'c'),
    7: ('a', 'b')
}

sectorFromTransforms = {}
for k, v in transformsFromSector.iteritems():
    sectorFromTransforms[v] = k


class VliegPositionTransformer(object):

    def __init__(self, geometry, hardware, solution_transformer):
        self._geometry = geometry
        self._hardware = hardware
        self._solution_transformer = solution_transformer
        solution_transformer.limitCheckerFunction = self.is_position_within_limits

    def transform(self, pos):
        # 1. Choose the correct sector/transforms
        return self._solution_transformer.transformPosition(pos)

    def is_position_within_limits(self, position):
        '''where position is Position object in degrees'''
        angleTuple = self._geometry.internal_position_to_physical_angles(position)
        angleTuple = self._hardware.cut_angles(angleTuple)
        return self._hardware.is_position_within_limits(angleTuple)


class VliegTransformSelector(object):
    '''All returned angles are between -180. and 180. -180.<=angle<180.
    '''
### basic sector selection

    def __init__(self):
        self.transforms = []
        self.autotransforms = []
        self.autosectors = []
        self.limitCheckerFunction = None  # inject
        self.sector = None
        self.setSector(0)

    def setSector(self, sector):
        if not 0 <= sector <= 7:
            raise ValueError('%i must between 0 and 7.' % sector)
        self.sector = sector
        self.transforms = list(transformsFromSector[sector])

    def setTransforms(self, transformList):
        transformList = list(transformList)
        transformList.sort()
        self.sector = sectorFromTransforms[tuple(transformList)]
        self.transforms = transformList

    def addTransorm(self, transformName):
        if transformName not in ('a', 'b', 'c'):
            raise ValueError('%s is not a recognised transform. Try a, b or c'
                             % transformName)
        if transformName in self.transforms:
            print "WARNING, transform %s is already selected"
        else:
            self.setTransforms(self.transforms + [transformName])

    def removeTransorm(self, transformName):
        if transformName not in ('a', 'b', 'c'):
            raise ValueError('%s is not a recognised transform. Try a, b or c'
                             % transformName)
        if transformName in self.transforms:
            new = copy(self.transforms)
            new.remove(transformName)
            self.setTransforms(new)
        else:
            print "WARNING, transform %s was not selected" % transformName

    def addAutoTransorm(self, transformOrSector):
        '''
        If input is a string (letter), tags one of the transofrms as being a
        candidate for auto application. If a number, tags a sector as being a
        candidate for auto application, and removes similar tags for any
        transforms (as the two are incompatable).
        '''
        if type(transformOrSector) == str:
            transform = transformOrSector
            if transform not in ('a', 'b', 'c'):
                raise ValueError(
                    '%s is not a recognised transform. Try a, b or c' %
                    transform)
            if transform not in self.autotransforms:
                self.autosectors = []
                self.autotransforms.append(transform)
            else:
                print "WARNING: %s is already set to auto apply" % transform
        elif type(transformOrSector) == int:
            sector = transformOrSector
            if not 0 <= sector <= 7:
                raise ValueError('%i must between 0 and 7.' % sector)
            if sector not in self.autosectors:
                self.autotransforms = []
                self.autosectors.append(sector)
            else:
                print "WARNING: %i is already set to auto apply" % sector
        else:
            raise ValueError("Input must be 'a', 'b' or 'c', "
                             "or 1,2,3,4,5,6 or 7.")

    def removeAutoTransform(self, transformOrSector):
        if type(transformOrSector) == str:
            transform = transformOrSector
            if transform not in ('a', 'b', 'c'):
                raise ValueError("%s is not a recognised transform. "
                                 "Try a, b or c" % transform)
            if transform in self.autotransforms:
                self.autotransforms.remove(transform)
            else:
                print "WARNING: %s is not set to auto apply" % transform
        elif type(transformOrSector) == int:
            sector = transformOrSector
            if not 0 <= sector <= 7:
                raise ValueError('%i must between 0 and 7.' % sector)
            if sector in self.autosectors:
                self.autosectors.remove(sector)
            else:
                print "WARNING: %s is not set to auto apply" % sector
        else:
            raise ValueError("Input must be 'a', 'b' or 'c', "
                             "or 1,2,3,4,5,6 or 7.")

    def setAutoSectors(self, sectorList):
        for sector in sectorList:
            if not 0 <= sector <= 7:
                raise ValueError('%i must between 0 and 7.' % sector)
        self.autosectors = list(sectorList)

    def transformPosition(self, pos):
        pos = self.transformNWithoutCut(self.sector, pos)
        cutpos = self.cutPosition(pos)
        # -180 <= cutpos < 180, NOT the externally applied cuts
        if len(self.autosectors) > 0:
            if self.is_position_within_limits(cutpos):
                return cutpos
            else:
                return self.autoTransformPositionBySector(cutpos)
        if len(self.autotransforms) > 0:
            if self.is_position_within_limits(cutpos):
                return cutpos
            else:
                return self.autoTransformPositionByTransforms(pos)
        #else
        return cutpos

    def transformNWithoutCut(self, n, pos):

        if n == 0:
            return P(pos.alpha, pos.delta, pos.gamma,
                     pos.omega, pos.chi, pos.phi)
        if n == 1:
            return P(pos.alpha, pos.delta, pos.gamma,
                     pos.omega - 180., -pos.chi, pos.phi - 180.)
        if n == 2:
            return P(pos.alpha, -pos.delta, pos.gamma,
                     -pos.omega, pos.chi - 180., pos.phi)
        if n == 3:
            return P(pos.alpha, -pos.delta, pos.gamma,
                     180. - pos.omega, 180. - pos.chi, pos.phi - 180.)
        if n == 4:
            return P(pos.alpha, pos.delta, pos.gamma,
                     -pos.omega, 180. - pos.chi, pos.phi - 180.)
        if n == 5:
            return P(pos.alpha, pos.delta, pos.gamma,
                     180. - pos.omega, pos.chi - 180., pos.phi)
        if n == 6:
            return P(pos.alpha, -pos.delta, pos.gamma,
                     pos.omega, -pos.chi, pos.phi - 180.)
        if n == 7:
            return P(pos.alpha, -pos.delta, pos.gamma,
                     pos.omega - 180., pos.chi, pos.phi)
        else:
            raise Exception("sector must be between 0 and 7")

### autosector

    def hasAutoSectorsOrTransformsToApply(self):
        return len(self.autosectors) > 0 or len(self.autotransforms) > 0

    def autoTransformPositionBySector(self, pos):
        okaysectors = []
        okaypositions = []
        for sector in self.autosectors:
            newpos = self.transformNWithoutCut(sector, pos)
            if self.is_position_within_limits(newpos):
                okaysectors.append(sector)
                okaypositions.append(newpos)
        if len(okaysectors) == 0:
            raise Exception(
                "Autosector could not find a sector (from %s) to move %s into "
                "limits." % (self.autosectors, str(pos)))
        if len(okaysectors) > 1:
            print ("WARNING: Autosector found multiple sectors that would "
                   "move %s to move into limits: %s" % (str(pos), okaysectors))

        print ("INFO: Autosector changed sector from %i to %i" %
               (self.sector, okaysectors[0]))
        self.sector = okaysectors[0]
        return okaypositions[0]

    def autoTransformPositionByTransforms(self, pos):
        possibleTransforms = self.createListOfPossibleTransforms()
        okaytransforms = []
        okaypositions = []
        for transforms in possibleTransforms:
            sector = sectorFromTransforms[tuple(transforms)]
            newpos = self.cutPosition(self.transformNWithoutCut(sector, pos))
            if self.is_position_within_limits(newpos):
                okaytransforms.append(transforms)
                okaypositions.append(newpos)
        if len(okaytransforms) == 0:
            raise Exception(
                "Autosector could not find a sector (from %r) to move %r into "
                "limits." % (self.autosectors, pos))
        if len(okaytransforms) > 1:
            print ("WARNING: Autosector found multiple sectors that would "
                   "move %s to move into limits: %s" %
                   (repr(pos), repr(okaytransforms)))

        print ("INFO: Autosector changed selected transforms from %r to %r" %
               (self.transforms, okaytransforms[0]))
        self.setTransforms(okaytransforms[0])
        return okaypositions[0]

    def createListOfPossibleTransforms(self):
        def vary(possibleTransforms, name):
            result = []
            for transforms in possibleTransforms:
                # add the original.
                result.append(transforms)
                # add a modified one
                toadd = list(copy(transforms))
                if name in transforms:
                    toadd.remove(name)
                else:
                    toadd.append(name)
                toadd.sort()
                result.append(toadd)
            return result
        # start with the currently selected list of transforms
        if len(self.transforms) == 0:
            possibleTransforms = [()]
        else:
            possibleTransforms = copy(self.transforms)

        for name in self.autotransforms:
            possibleTransforms = vary(possibleTransforms, name)

        return possibleTransforms

    def is_position_within_limits(self, pos):
        '''where pos os a poistion object in degrees'''
        return self.limitCheckerFunction(pos)

    def __repr__(self):
        def createPrefix(transform):
            if transform in self.transforms:
                s = '*on* '
            else:
                s = 'off  '
            if len(self.autotransforms) > 0:
                if transform in self.autotransforms:
                    s += '*auto*'
                else:
                    s += '      '
            return s
        s = 'Transforms/sector:\n'
        s += ('  %s (a transform) Invert scattering plane: invert delta and '
              'omega and flip chi\n' % createPrefix('a'))
        s += ('  %s (b transform) Flip chi, and invert and flip omega\n' %
              createPrefix('b'))
        s += ('  %s (c transform) Flip omega, invert chi and flip phi\n' %
              createPrefix('c'))
        s += '  Current sector: %i (Spec fourc equivalent)\n' % self.sector
        if len(self.autosectors) > 0:
            s += '  Auto sectors: %s\n' % self.autosectors
        return s

    def cutPosition(self, position):
        '''Cuts angles at -180.; moves each argument between -180. and 180.
        '''
        def cut(a):
            if a is None:
                return None
            else:
                if a < (-180. - SMALL):
                    return a + 360.
                if a > (180. + SMALL):
                    return a - 360.
            return a
        return P(cut(position.alpha), cut(position.delta), cut(position.gamma),
                 cut(position.omega), cut(position.chi), cut(position.phi))


def getNameFromScannableOrString(o):
        try:  # it may be a scannable
            return o.getName()
        except AttributeError:
            return str(o)


class TransformCommands(object):

    def __init__(self, sector_selector):
        self._sectorSelector = sector_selector
        self.commands = ['Transform',
                         self.transform,
                         self.transforma,
                         self.transformb,
                         self.transformc]

    @command
    def transform(self):
        """transform  -- show transform configuration"""
        print self._sectorSelector.__repr__()

    @command
    def transforma(self, *args):
        """transforma {on|off|auto|manual} -- configure transform A application
        """
        self._transform('transforma', 'a', args)

    @command
    def transformb(self, *args):
        """transformb {on|off|auto|manual} -- configure transform B application
        """
        self._transform('transformb', 'b', args)

    @command
    def transformc(self, *args):
        """transformc {on|off|auto|manual} -- configure transform C application
        """

        self._transform('transformc', 'c', args)

    def _transform(self, commandName, transformName, args):
        if len(args) == 0:
            print self._sectorSelector.__repr__()
            return
        # get name
        if len(args) != 1:
            raise TypeError()
        if type(args[0]) is not str:
            raise TypeError()

        ss = self._sectorSelector
        if args[0] == 'on':
            ss.addTransorm(transformName)
        elif args[0] == 'off':
            ss.removeTransorm(transformName)
        elif args[0] == 'auto':
            ss.addAutoTransorm(transformName)
        elif args[0] == 'manual':
            ss.removeAutoTransform(transformName)
        else:
            raise TypeError()
        print self._sectorSelector.__repr__()

    @command
    def sector(self, sector=None):
        """sector {0-7} -- Select or display sector (a la Spec)
        """
        if sector is None:
            print self._sectorSelector.__repr__()
        else:
            if type(sector) is not int and not (0 <= sector <= 7):
                raise TypeError()
            self._sectorSelector.setSector(sector)
            print self._sectorSelector.__repr__()

    @command
    def autosector(self, *args):
        """autosector [None] [0-7] [0-7]... -- Set sectors that might be automatically applied""" #@IgnorePep8
        if len(args) == 0:
            print self._sectorSelector.__repr__()
        elif len(args) == 1 and args[0] is None:
            self._sectorSelector.setAutoSectors([])
            print self._sectorSelector.__repr__()
        else:
            sectorList = []
            for arg in args:
                if type(arg) is not int:
                    raise TypeError()
                sectorList.append(arg)
            self._sectorSelector.setAutoSectors(sectorList)
            print self._sectorSelector.__repr__()



