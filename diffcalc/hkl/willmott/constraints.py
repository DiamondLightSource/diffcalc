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

from diffcalc.util import DiffcalcException


def filter_dict(d, keys):
    """Return a copy of d containing only keys that are in keys"""
    ##return {k: d[k] for k in keys} # requires Python 2.6
    return dict((k, d[k]) for k in keys if k in d.keys())


ref_constraints = ('betain', 'betaout', 'bin_eq_bout')
valueless_constraints = ('bin_eq_bout')
all_constraints = ref_constraints


class WillmottConstraintManager(object):
    """Constraints in degrees.
    """

    def __init__(self):
        self._constrained = {'bin_eq_bout': None}

    @property
    def available_constraint_names(self):
        """list of all available constraints"""
        return all_constraints

    @property
    def all(self):  # @ReservedAssignment
        """dictionary of all constrained values"""
        return self._constrained.copy()

    @property
    def reference(self):
        """dictionary of constrained reference circles"""
        return filter_dict(self.all, ref_constraints)

    @property
    def constrained_names(self):
        """ordered tuple of constained circles"""
        names = self.all.keys()
        names.sort(key=lambda name: list(all_constraints).index(name))
        return tuple(names)

    def is_constrained(self, name):
        return name in self._constrained

    def get_value(self, name):
        return self._constrained[name]

    def _build_display_table(self):
        constraint_types = (ref_constraints,)
        num_rows = max([len(col) for col in constraint_types])
        max_name_width = max(
            [len(name) for name in sum(constraint_types[:2], ())])
        # headings
        lines = ['    ' + 'REF'.ljust(max_name_width)]
        lines.append('    ' + '=' * max_name_width + ' ')

        # constraint rows
        for n_row in range(num_rows):
            cells = []
            for col in constraint_types:
                name = col[n_row] if n_row < len(col) else ''
                cells.append(self._label_constraint(name))
                cells.append(('%-' + str(max_name_width) + 's ') % name)
            lines.append(''.join(cells))
        lines.append
        return '\n'.join(lines)

    def _report_constraints(self):
        if not self.reference:
            return "!!! No reference constraint set"
        name, val = self.reference.items()[0]
        if name in valueless_constraints:
            return "    %s" % name
        else:
            if val is None:
                return "!!! %s: ---" % name
            else:
                return "    %s: %.4f" % (name, val)

    def _label_constraint(self, name):
        if name == '':
            label = '    '
        elif (self.is_constrained(name) and (self.get_value(name) is None) and
            name not in valueless_constraints):
            label = 'o-> '
        elif self.is_constrained(name):
            label = '--> '
        else:
            label = '    '
        return label

    def constrain(self, name):
        if name in self.all:
            return "%s is already constrained." % name.capitalize()
        elif name in ref_constraints:
            return self._constrain_reference(name)
        else:
            raise DiffcalcException('%s is not a valid constraint name')

    def _constrain_reference(self, name):
        if self.reference:
            constrained_name = self.reference.keys()[0]
            del self._constrained[constrained_name]
            self._constrained[name] = None
            return '%s constraint replaced.' % constrained_name.capitalize()
        else:
            self._constrained[name] = None

    def unconstrain(self, name):
        if name in self._constrained:
            del self._constrained[name]
        else:
            return "%s was not already constrained." % name.capitalize()

###
    def _check_constraint_settable(self, name, verb):
        if name not in all_constraints:
            raise DiffcalcException(
                'Could not %(verb)s %(name)s as this is not an available '
                'constraint.' % locals())
        elif name not in self.all.keys():
            raise DiffcalcException(
                'Could not %(verb)s %(name)s as this is not currently '
                'constrained.' % locals())
        elif name in valueless_constraints:
            raise DiffcalcException(
                'Could not %(verb)s %(name)s as this constraint takes no '
                'value.' % locals())

    def set_constraint(self, name, value):  # @ReservedAssignment
        self._check_constraint_settable(name, 'set')
        old_value = self.all[name]
        old = str(old_value) if old_value is not None else '---'
        self._constrained[name] = float(value)
        new = str(value)
        return "%(name)s : %(old)s --> %(new)s" % locals()
