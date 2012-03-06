from diffcalc.hkl.common import getNameFromScannableOrString
from diffcalc.util import command


class WillmottHklCommands(object):

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
        """
        print self._report_constraints()

    def _report_constraints(self):
        return (self._hklcalc.constraints.build_display_table() + '\n\n' +
               self._hklcalc.constraints._report_constraints())
