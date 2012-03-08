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

        lines = []
        constraints = self._hklcalc.constraints
        lines.extend(constraints.build_display_table_lines())
        lines.append("")
        lines.extend(constraints.report_constraints_lines())
        lines.append("")
        if (constraints.is_fully_constrained() and
            not constraints.is_current_mode_implemented()):
            lines.append(
                "    Sorry, this constraint combination is not implemented")
            lines.append("    Type 'help cons' for available combinations")
        else:
            lines.append("    Type 'help cons' for instructions")  # okay
        print '\n'.join(lines)
