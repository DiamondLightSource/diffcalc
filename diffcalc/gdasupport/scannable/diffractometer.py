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

try:
    from gda.device.scannable import ScannableMotionBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import \
        Scannable as ScannableMotionBase

from diffcalc.util import getMessageFromException

# TODO: Split into a base class when making other scannables


class DiffractometerScannableGroup(ScannableMotionBase):
    """"
    Wraps up a scannableGroup of axis to tweak the way the resulting
    object is displayed and to add a simulate move to method.

    The scannable group should have the same geometry as that expected
    by the diffractometer hardware geometry used in the diffraction
    calculator.

    The optional parameter slaveDriver can be used to provide a
    slave_driver. This is useful for triggering a move of an incidental
    axis whose position depends on that of the diffractometer, but whose
    position need not be included in the DiffractometerScannableGroup
    itself. This parameter is exposed as a field and can be set or
    cleared to null at will without effecting the core calculation code.
    """

    def __init__(self, name, diffcalcObject, scannableGroup,
                 slave_driver=None):
        # if motorList is None, will create a dummy __group
        self.diffcalc = diffcalcObject
        self.__group = scannableGroup
        self.slave_driver = slave_driver
        self.setName(name)

    def getInputNames(self):
        return self.__group.getInputNames()

    def getExtraNames(self):
        if self.slave_driver is None:
            return []
        else:
            return self.slave_driver.getScannableNames()

    def getOutputFormat(self):
        if self.slave_driver is None:
            slave_formats = []
        else:
            slave_formats = self.slave_driver.getScannableNames()
        return list(self.__group.getOutputFormat()) + slave_formats

    def asynchronousMoveTo(self, position):
        self.__group.asynchronousMoveTo(position)
        if self.slave_driver is not None:
            self.slave_driver.triggerAsynchronousMove(position)

    def getPosition(self):
        if self.slave_driver is None:
            slave_positions = []
        else:
            slave_positions = self.slave_driver.getPositions()
        return list(self.__group.getPosition()) + list(slave_positions)

    def isBusy(self):
        if self.slave_driver is None:
            return self.__group.isBusy()
        else:
            return self.__group.isBusy() or self.slave_driver.isBusy()

    def waitWhileBusy(self):
        self.__group.waitWhileBusy()
        if self.slave_driver is not None:
            self.slave_driver.waitWhileBusy()

    def simulateMoveTo(self, pos):
        if len(pos) != len(self.getInputNames()):
            raise ValueError('Wrong number of inputs')
        try:
            (hkl, params) = self.diffcalc.angles_to_hkl(pos)
        except Exception, e:
            return "Error: %s" % getMessageFromException(e)
        width = max(len(k) for k in params)

        lines = (['  ' + 'hkl'.rjust(width) + ' : % 9.4f  %.4f  %.4f' %
                  (hkl[0], hkl[1], hkl[2])])
        lines[-1] = lines[-1] + '\n'
        fmt = '  %' + str(width) + 's : % 9.4f'
        for k in sorted(params):
            lines.append(fmt % (k, params[k]))
        return '\n'.join(lines)

    def __repr__(self):
        position = self.getPosition()
        names = list(self.getInputNames()) + list(self.getExtraNames())

        lines = [self.name + ':']
        width = max(len(k) for k in names)
        fmt = '  %' + str(width) + 's : % 9.4f'
        for name, pos in zip(names, position):
            lines.append(fmt % (name, pos))
        lines[len(self.getInputNames())] += '\n'
        return '\n'.join(lines)
