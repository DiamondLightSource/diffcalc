from diffcalc.hkl.common import getNameFromScannableOrString
from diffcalc.util import command


class YouHklCommands(object):

    def __init__(self, hklcalc):
        self._hklcalc = hklcalc
        self.commands = [self.con,
                         self.uncon,
                         self.cons]

    def __str__(self):
        return self._hklcalc.__str__()

    @command
    def con(self, scn_or_string):
        """con <constraint> -- constrains constraint
        """
        name = getNameFromScannableOrString(scn_or_string)
        self._hklcalc.constraints.constrain(name)
        print self._report_constraints()

    @command
    def uncon(self, scn_or_string):
        """uncon <constraint> -- unconstrains constraint
        """
        name = getNameFromScannableOrString(scn_or_string)
        self._hklcalc.constraints.unconstrain(name)
        print self._report_constraints()

    @command
    def cons(self):
        """cons -- list available constraints and values

        Select three constraints using 'con' and 'uncon'. Choose up to one
        from each of the sample and detector columns and up to three from
        the sample column.

        Not all constraint combinations are currently available:

            1 x samp:              all 80 of 80
            2 x samp and 1 x ref:  chi & phi, mu & eta and chi=90 & mu=0 (2.5 of 6)
            2 x samp and 1 x det:  0 of 6
            3 x samp:              0 of 4

        See also 'con' and 'uncon'
        """
        lines = []
        lines.append(self._hklcalc.constraints.build_display_table())
        lines.append("")
        lines.append(self._hklcalc.constraints.report_constraints())
        lines.append("")
        lines.append("Type 'help cons' for instructions")
        print '\n'.join(lines)

    def _report_constraints(self):
        return (self._hklcalc.constraints.build_display_table() + '\n\n' +
               self._hklcalc.constraints.report_constraints())
