from diffcalc.utils import DiffcalcException


def filter_dict(d, keys):
    """Return a copy of d containing only keys that are in keys"""
    ##return {k: d[k] for k in keys} # requires Python 2.6
    return dict((k, d[k]) for k in keys if k in d.keys())


det_constraints = ('delta', 'nu', 'qaz', 'naz')
ref_constraints = ('a_eq_b', 'alpha', 'beta', 'psi')
samp_constraints = ('mu', 'eta', 'chi', 'phi', 'mu_is_nu')

trackable_constraints = ('delta', 'nu', 'mu', 'eta', 'chi', 'phi')
valueless_constraints = ('a_eq_b', 'mu_is_nu')
all_constraints = det_constraints + ref_constraints + samp_constraints


class ConstraintManager(object):

    def __init__(self, hardware):
        self._hardware = hardware
        self._constrained = {}
        self._tracking = []

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

    def is_constrained(self, name):
        return name in self._constrained

    def is_tracking(self, name):
        return name in self._tracking

    def get_value(self, name):
        return self._constrained[name]

    def _build_display_table(self):
        constraint_types = (det_constraints, ref_constraints,
                            samp_constraints)
        num_rows = max([len(col) for col in constraint_types])
        max_name_width = max(
            [len(name) for name in sum(constraint_types[:2], ())])
        s = '    ' + 'DET'.ljust(max_name_width) + ' '
        s += '    ' + 'REF'.ljust(max_name_width) + ' '
        s += '    ' + 'SAMP' + '\n'
        s += (('    ' + '=' * max_name_width + ' ') * 3).rstrip() + '\n'
        for n_row in range(num_rows):
            for col in constraint_types:
                name = col[n_row] if n_row < len(col) else ''
                s += self._label_constraint(name)
                s += ('%-' + str(max_name_width) + 's ') % name
            s = s.rstrip()
            s += '\n'
        return s

    def _label_constraint(self, name):
        if name == '':
            label = '    '
        elif self.is_tracking(name):  # implies constrained
            label = '~~> '
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
        elif name in det_constraints:
            return self._constrain_detector(name)
        elif name in ref_constraints:
            return self._constrain_reference(name)
        elif name in samp_constraints:
            return self._constrain_sample(name)
        else:
            raise DiffcalcException('%s is not a valid constraint name')

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
        return DiffcalcException(
"""%s could not be constrained. First un-constrain one of as the angles %s,
%s or %s (with 'uncon')""" % ((name.capitalize(),) + self.constrained_names))

    def _constrain_reference(self, name):
        if self.reference:
            constrained_name = self.reference.keys()[0]
            del self._constrained[constrained_name]
            self._constrained[name] = None
            return '%s constraint replaced.' % constrained_name.capitalize()
        elif len(self.all) == 3:  # and no reference
            raise self._could_not_constrain_exception(name)
        else:
            self._constrained[name] = None

    def _constrain_sample(self, name):
        if len(self._constrained) < 3:
            # okay, more to add
            self._constrained[name] = None
        # else: three constraints are set
        elif len(self.sample) == 1:
            # (detector and reference constraints set)
            # it is clear which sample constraint to remove
            constrained_name = self.sample.keys()[0]
            del self._constrained[constrained_name]
            self._constrained[name] = None
            return '%s constraint replaced.' % constrained_name.capitalize()
        else:
            raise self._could_not_constrain_exception(name)

    def unconstrain(self, name):
        if name in self._constrained:
            del self._constrained[name]
        else:
            return "%s was not already constrained." % name.capitalize()

    def _check_constraint_settable_or_trackable(self, name, verb):
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

    def set(self, name, value):  # @ReservedAssignment
        self._check_constraint_settable_or_trackable(name, 'set')
        if name in self._tracking:
            raise DiffcalcException(
                "Could not set %s as this constraint is configured to track "
                "its associated\nphysical angle. First remove this tracking "
                "(use 'untrack %s').""" % (name, name))
        old_value = self.all[name]
        old = str(old_value) if old_value is not None else '---'
        self._constrained[name] = float(value)
        new = str(value)
        return "%(name)s : %(old)s --> %(new)s" % locals()

    def track(self, name):
        self._check_constraint_settable_or_trackable(name, 'track')
        if name not in trackable_constraints:
            raise DiffcalcException(
"""Could not configure %s to track as this constraint is not associated with a
physical angle.""" % name)
        elif name in self._tracking:
            return "%s was already configured to track." % name.capitalize()
        else:
            old_value = self.all[name]
            old = str(old_value) if old_value is not None else '---'
            self._tracking.append(name)
            self.update_tracked()
            new = str(self.all[name])
            return "%(name)s : %(old)s ~~> %(new)s (tracking)" % locals()

    def untrack(self, name):
        if name not in self._tracking:
            return "%s was not configured to track." % name.capitalize()
        self._tracking.remove(name)

    def update_tracked(self):
        if self._tracking:
            physical_angles = tuple(self._hardware.getPosition())
            angle_names = tuple(self._hardware.getPhysicalAngleNames())
            for name in self._tracking:
                self._constrained[name] = \
                    physical_angles[list(angle_names).index(name)]
