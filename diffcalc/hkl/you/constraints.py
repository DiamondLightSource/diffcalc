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

from math import pi
from diffcalc import settings

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.util import DiffcalcException, bold
from diffcalc.settings import NUNAME

TODEG = 180 / pi
TORAD = pi / 180

def filter_dict(d, keys):
    """Return a copy of d containing only keys that are in keys"""
    ##return {k: d[k] for k in keys} # requires Python 2.6
    return dict((k, d[k]) for k in keys if k in d.keys())


det_constraints = ('delta', NUNAME, 'qaz', 'naz')
if settings.include_reference:
    ref_constraints = ('a_eq_b', 'alpha', 'beta', 'psi', 'bin_eq_bout', 'betain', 'betaout')
    valueless_constraints = ('a_eq_b', 'bin_eq_bout', 'mu_is_' + NUNAME, 'bisect')
else:
    ref_constraints = ('bin_eq_bout', 'betain', 'betaout')
    valueless_constraints = ('bin_eq_bout', 'mu_is_' + NUNAME, 'bisect')
samp_constraints = ('mu', 'eta', 'chi', 'phi', 'mu_is_' + NUNAME, 'bisect', 'omega')

all_constraints = det_constraints + ref_constraints + samp_constraints


number_single_sample = (len(det_constraints) * len(ref_constraints) *
                        len(samp_constraints))


class YouConstraintManager(object):

    def __init__(self, fixed_constraints = {}):
        self._constrained = {}
#        self._tracking = []
        self.n_phi = matrix([[0], [0], [1]])
        self._hide_detector_constraint = False # default
        self._fixed_samp_constraints = ()
        self._fix_constraints(fixed_constraints)

    def __str__(self):
        lines = []
#        TODO: Put somewhere with access to UB matrix!
#        WIDTH = 13
#        n_phi = self.n_phi
#        fmt = "% 9.5f % 9.5f % 9.5f"
#        lines.append("   n_phi:".ljust(WIDTH) +
#                     fmt % (n_phi[0, 0], n_phi[1, 0], n_phi[2, 0]))
#        if self._getUBMatrix():
#            n_cryst = self._getUMatrix().I * self.n_phi
#            lines.append("   n_cryst:".ljust(WIDTH) +
#                         fmt % (n_cryst[0, 0], n_cryst[1, 0], n_cryst[2, 0]))
#            n_recip = self._getUBMatrix().I * self.n_phi
#            lines.append("   n_recip:".ljust(WIDTH) +
#                         fmt % (n_recip[0, 0], n_recip[1, 0], n_recip[2, 0]))
#        else:
#            lines.append(
#                "   n_cryst:".ljust(WIDTH) + ' "<<< No  U matrix >>>"')
#            lines.append(
#                "   n_recip:".ljust(WIDTH) + ' "<<< No UB matrix >>>"')

        lines.extend(self.build_display_table_lines())
        lines.append("")
        lines.extend(self.report_constraints_lines())
        lines.append("")
        if (self.is_fully_constrained() and
            not self.is_current_mode_implemented()):
            lines.append(
                "    Sorry, this constraint combination is not implemented")
            lines.append("    Type 'help con' for available combinations")
        else:
            lines.append("    Type 'help con' for instructions")  # okay
        return '\n'.join(lines)

    @property
    def available_constraint_names(self):
        """list of all available constraints"""
        return all_constraints

    @property
    def settable_constraint_names(self):
        """list of all available constraints that have settable values"""
        all_copy = list(all_constraints)
        for valueless in valueless_constraints:
            all_copy.remove(valueless)
        return all_copy

    @property
    def all(self):  # @ReservedAssignment
        """dictionary of all constrained values"""
        return self._constrained.copy()

    @property
    def detector(self):
        """dictionary of constrained detector circles"""
        return filter_dict(self.all, det_constraints[:-1])

    @property
    def reference(self):
        """dictionary of constrained reference circles"""
        return filter_dict(self.all, ref_constraints)

    @property
    def sample(self):
        """dictionary of constrained sample circles"""
        return filter_dict(self.all, samp_constraints)

    @property
    def naz(self):
        """dictionary with naz and value if constrained"""
        return filter_dict(self.all, ('naz',))

    @property
    def constrained_names(self):
        """ordered tuple of constained circles"""
        names = self.all.keys()
        names.sort(key=lambda name: list(all_constraints).index(name))
        return tuple(names)

    @property
    def available_names(self):
        """ordered tuple of fixed circles"""
        names = [name for name in self.all.keys() if not self.is_constraint_fixed(name)]
        names.sort(key=lambda name: list(all_constraints).index(name))
        return tuple(names)

    def _fix_constraints(self, fixed_constraints):
        for name in fixed_constraints:
            self.constrain(name)
            self.set_constraint(name, fixed_constraints[name])
        
        if self.detector or self.naz:    
            self._hide_detector_constraint = True
        
        fixed_samp_constraints = list(self.sample.keys())
        if 'mu' in self.sample or NUNAME in self.detector:
            fixed_samp_constraints.append('mu_is_' + NUNAME)
        self._fixed_samp_constraints = tuple(fixed_samp_constraints)
        

    def is_constrained(self, name):
        return name in self._constrained

    def get_value(self, name):
        return self._constrained[name]

    def build_display_table_lines(self):
        unfixed_samp_constraints = list(samp_constraints)
        for name in self._fixed_samp_constraints:
            unfixed_samp_constraints.remove(name)
        if self._hide_detector_constraint:
            constraint_types = (ref_constraints, unfixed_samp_constraints)
        else:
            constraint_types = (det_constraints, ref_constraints,
                                unfixed_samp_constraints)
        num_rows = max([len(col) for col in constraint_types])
        max_name_width = max(
            [len(name) for name in sum(constraint_types[:-1], ())])
        
        cells = []
        
        header_cells = []
        if not self._hide_detector_constraint:
            header_cells.append(bold('    ' + 'DET'.ljust(max_name_width)))
        header_cells.append(bold('    ' + 'REF'.ljust(max_name_width)))
        header_cells.append(bold('    ' + 'SAMP'))
        cells.append(header_cells)
        
        underline_cells = ['    ' + '-' * max_name_width] * len(constraint_types)
        cells.append(underline_cells)
        
        for n_row in range(num_rows):
            row_cells = []
            for col in constraint_types:
                name = col[n_row] if n_row < len(col) else ''
                row_cells.append(self._label_constraint(name))
                ext_name = settings.geometry.map_to_external_name(name)
                row_cells.append(('%-' + str(max_name_width) + 's') % ext_name)
            cells.append(row_cells)
        
        lines = [' '.join(row_cells).rstrip() for row_cells in cells]
        return lines

    def _report_constraint(self, name):
        val = self.get_constraint(name)
        ext_name = settings.geometry.map_to_external_name(name)
        if name in valueless_constraints:
            return "    %s" % ext_name
        else:
            if val is None:
                return "!   %-5s: ---" % ext_name
            else:
                ext_name, ext_val = settings.geometry.map_to_external_position(name, val)
                return "    %-5s: %.4f" % (ext_name, ext_val)

    def report_constraints_lines(self):
        lines = []
        required = 3 - len(self.all)
        if required == 0:
            pass
        elif required == 1:
            lines.append('!   1 more constraint required')
        else:
            lines.append('!   %d more constraints required' % required)
        lines.extend([self._report_constraint(name) for name in self.available_names])
        return lines

    def is_fully_constrained(self):
        return len(self.all) == 3

    def is_current_mode_implemented(self):
        if not self.is_fully_constrained():
            raise ValueError("Three constraints required")
        
        if len(self.sample) == 3:
            if (set(self.sample.keys()) == set(['chi', 'phi', 'eta']) or
               set(self.sample.keys()) == set(['chi', 'phi', 'mu']) or
               set(self.sample.keys()) == set(['chi', 'eta', 'mu']) or
               set(self.sample.keys()) == set(['phi', 'eta', 'mu'])):
                return True
            return False

        if len(self.sample) == 1:
            return ('omega' not in set(self.sample.keys()) and
                    'bisect' not in set(self.sample.keys()))

        if len(self.reference) == 1:
            return (set(self.sample.keys()) == set(['chi', 'phi']) or
                    set(self.sample.keys()) == set(['chi', 'eta']) or
                    set(self.sample.keys()) == set(['chi', 'mu']) or
                    set(self.sample.keys()) == set(['mu', 'eta']) or
                    set(self.sample.keys()) == set(['mu', 'phi']) or
                    set(self.sample.keys()) == set(['eta', 'phi']))

        if len(self.detector) == 1:
            return (set(self.sample.keys()) == set(['chi', 'phi']) or
                    set(self.sample.keys()) == set(['mu', 'eta']) or
                    set(self.sample.keys()) == set(['mu', 'phi']) or
                    set(self.sample.keys()) == set(['mu', 'chi']) or
                    set(self.sample.keys()) == set(['eta', 'phi']) or
                    set(self.sample.keys()) == set(['eta', 'chi']) or
                    set(self.sample.keys()) == set(['mu', 'bisect']) or
                    set(self.sample.keys()) == set(['eta', 'bisect']) or
                    set(self.sample.keys()) == set(['omega', 'bisect']))
        
        return False
        

    def _label_constraint(self, name):
        if name == '':
            label = '   '
#        elif self.is_tracking(name):  # implies constrained
#            label = '~~> '
        elif (self.is_constrained(name) and (self.get_value(name) is None) and
            name not in valueless_constraints):
            label = 'o->'
        elif self.is_constrained(name):
            label = '-->'
        else:
            label = '   '
        return label

    def constrain(self, name):
        ext_name = settings.geometry.map_to_external_name(name)
        if self.is_constraint_fixed(name):
            raise DiffcalcException('%s constraint cannot be changed' % ext_name)
        if name in self.all:
            return "%s is already constrained." % ext_name.capitalize()
        elif name in det_constraints:
            return self._constrain_detector(name)
        elif name in ref_constraints:
            return self._constrain_reference(name)
        elif name in samp_constraints:
            return self._constrain_sample(name)
        else:
            raise DiffcalcException("%s is not a valid constraint name. Type 'con' for a table of constraint name" % ext_name)

    def is_constraint_fixed(self, name):
        return ((name in det_constraints and self._hide_detector_constraint) or
                (name in samp_constraints and name in self._fixed_samp_constraints))

    def _constrain_detector(self, name):
        if self.naz:
            del self._constrained['naz']
            self._constrained[name] = None
            return 'Naz constraint replaced.'
        elif self.detector:
            constrained_name = self.detector.keys()[0]
            del self._constrained[constrained_name]
            self._constrained[name] = None
            return'%s constraint replaced.' % constrained_name.capitalize()
        elif len(self.all) == 3:  # and no detector
            raise self._could_not_constrain_exception(name)
        else:
            self._constrained[name] = None

    def _could_not_constrain_exception(self, name):
        ext_name = settings.geometry.map_to_external_name(name)
        names = [settings.geometry.map_to_external_name(nm) for nm in self.available_names]
        if len(names) > 1:
            names_fmt = 'one of the\nangles ' + ', '.join(names[:-1]) + ' or ' + names[-1]
        else:
            names_fmt = 'angle ' + names[0]
        return DiffcalcException(
            "%s could not be constrained. First un-constrain %s "
            "(with 'uncon')" %
            (ext_name.capitalize(), names_fmt))

    def _constrain_reference(self, name):
        if self.reference:
            constrained_name = self.reference.keys()[0]
        elif len(self._constrained) < 3:
            constrained_name = None
        elif len(self.available_names) == 1:
            constrained_name = self.available_names[0]
        else:
            raise self._could_not_constrain_exception(name)
        try:
            del self._constrained[constrained_name]
            self._constrained[name] = None
            ext_constrained_name = settings.geometry.map_to_external_name(constrained_name)
            return '%s constraint replaced.' % ext_constrained_name.capitalize()
        except KeyError:
            self._constrained[name] = None

    def _constrain_sample(self, name):
        if len(self._constrained) < 3:
            constrained_name = None
        elif len(self.available_names) == 1:
            # Only one settable constraint
            constrained_name = self.available_names[0]
        elif len(self.sample) == 1:
            # (detector and reference constraints set)
            # it is clear which sample constraint to remove
            constrained_name = self.sample.keys()[0]
            if self.is_constraint_fixed(constrained_name):
                raise self._could_not_constrain_exception(name)
        else:
            # else: three constraints are set
            raise self._could_not_constrain_exception(name)
        try:
            del self._constrained[constrained_name]
            self._constrained[name] = None
            ext_constrained_name = settings.geometry.map_to_external_name(constrained_name)
            return '%s constraint replaced.' % ext_constrained_name.capitalize()
        except KeyError:
            self._constrained[name] = None

    def unconstrain(self, name):
        ext_name = settings.geometry.map_to_external_name(name)
        if self.is_constraint_fixed(name):
            raise DiffcalcException('%s constraint cannot be removed' % ext_name)
        if name in self._constrained:
            del self._constrained[name]
        else:
            return "%s was not already constrained." % ext_name.capitalize()

    def _check_constraint_settable(self, name):
        ext_name = settings.geometry.map_to_external_name(name)
        if name not in all_constraints:
            raise DiffcalcException(
                'Could not set %(ext_name)s. This is not an available '
                'constraint.' % locals())
        elif name not in self.all.keys():
            raise DiffcalcException(
                'Could not set %(ext_name)s. This is not currently '
                'constrained.' % locals())
        elif name in valueless_constraints:
            raise DiffcalcException(
                'Could not set %(ext_name)s. This constraint takes no '
                'value.' % locals())

    def clear_constraints(self):
        self._constrained = {}

    def set_constraint(self, name, value):  # @ReservedAssignment
        ext_name = settings.geometry.map_to_external_name(name)
        if self.is_constraint_fixed(name):
            raise DiffcalcException('%s constraint cannot be changed' % ext_name)
        self._check_constraint_settable(name)
#        if name in self._tracking:
#            raise DiffcalcException(
#                "Could not set %s as this constraint is configured to track "
#                "its associated\nphysical angle. First remove this tracking "
#                "(use 'untrack %s').""" % (name, name))
        old_value = self.get_constraint(name)
        try:
            old_str = '---' if old_value is None else str(old_value)
        except Exception:
            old_str = '---'
        try:
            self._constrained[name] = float(value) * TORAD
        except Exception:
            raise DiffcalcException('Cannot set %s constraint. Invalid input value.' % ext_name)
        try:
            new_str = '---' if value is None else str(value)
        except Exception:
            new_str = '---'
        return "%s : %s --> %s" % (name, old_str, new_str)

    def get_constraint(self, name):
        value = self.all[name]
        return None if value is None else value * TODEG
    