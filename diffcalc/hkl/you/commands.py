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

from diffcalc.hkl.common import getNameFromScannableOrString
from diffcalc.util import command


class YouHklCommands(object):

    def __init__(self, hklcalc):
        self._hklcalc = hklcalc
        self.commands = ['CONSTRAINTS',
                         self.con,
                         self.uncon,
                         self.cons]

    def __str__(self):
        return self._hklcalc.__str__()

    @command
    def con(self, scn_or_string, value=None):
        """con <constraint> {value}-- constrains and optionally sets constraint
        """
        name = getNameFromScannableOrString(scn_or_string)
        self._hklcalc.constraints.constrain(name)
        if value is not None:
            self._hklcalc.constraints.set_constraint(name, value)
        print '\n'.join(self._hklcalc.constraints.report_constraints_lines())

    @command
    def uncon(self, scn_or_string):
        """uncon <constraint> -- remove constraint
        """
        name = getNameFromScannableOrString(scn_or_string)
        self._hklcalc.constraints.unconstrain(name)
        print '\n'.join(self._hklcalc.constraints.report_constraints_lines())

    @command
    def cons(self):
        """cons -- list available constraints and values

        Select three constraints using 'con' and 'uncon'. Choose up to one
        from each of the sample and detector columns and up to three from
        the sample column.

        Not all constraint combinations are currently available:

            1 x samp:              all 80 of 80
            2 x samp and 1 x ref:  chi & phi
                                   mu & eta
                                   chi=90 & mu=0 (2.5 of 6)
            2 x samp and 1 x det:  0 of 6
            3 x samp:              0 of 4

        See also 'con' and 'uncon'
        """
        print self._hklcalc.constraints
