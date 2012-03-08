try:
    from gda.device.scannable.scannablegroup import \
        ScannableMotionWithScannableFieldsBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import \
        ScannableMotionWithScannableFieldsBase

from diffcalc.util import getMessageFromException, DiffcalcException


class _DynamicDocstringMetaclass(type):

    def _get_doc(self):
        return Hkl.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment


class Hkl(ScannableMotionWithScannableFieldsBase):

    #__metaclass__ = _DynamicDocstringMetaclass  # TODO: Removed to fix Jython

    dynamic_docstring = 'Hkl Scannable'

    def _get_doc(self):
        return Hkl.dynamic_docstring

    __doc__ = property(_get_doc)  # @ReservedAssignment

    def __init__(self, name, diffractometerObject, diffcalcObject,
                 virtualAnglesToReport=None):
        self.diffhw = diffractometerObject
        self._diffcalc = diffcalcObject
        if type(virtualAnglesToReport) is str:
            virtualAnglesToReport = (virtualAnglesToReport,)
        self.vAngleNames = virtualAnglesToReport

        self.setName(name)
        self.setInputNames(['h', 'k', 'l'])
        self.setOutputFormat(['%7.5f'] * 3)
        if self.vAngleNames:
            self.setExtraNames(self.vAngleNames)
            self.setOutputFormat(['%7.5f'] * (3 + len(self.vAngleNames)))

        self.completeInstantiation()
        self.setAutoCompletePartialMoveToTargets(True)
        self.dynamic_class_doc = 'Hkl Scannable xyz'

    def rawAsynchronousMoveTo(self, hkl):
        if len(hkl) != 3: raise ValueError('Hkl device expects three inputs')
        try:
            (pos, _) = self._diffcalc.hkl_to_angles(hkl[0], hkl[1], hkl[2])
        except DiffcalcException, e:
            raise DiffcalcException(e.message)
        self.diffhw.asynchronousMoveTo(pos)

    def rawGetPosition(self):
        pos = self.diffhw.getPosition()
        (hkl , params) = self._diffcalc.angles_to_hkl(pos)
        result = list(hkl)
        if self.vAngleNames:
            for vAngleName in self.vAngleNames:
                result.append(params[vAngleName])
        return result

    def getFieldPosition(self, i):
        return self.getPosition()[i]

    def isBusy(self):
        return self.diffhw.isBusy()

    def waitWhileBusy(self):
        return self.diffhw.waitWhileBusy()

    def simulateMoveTo(self, hkl):
        if type(hkl) not in (list, tuple):
            raise ValueError('Hkl device expects three inputs')
        if len(hkl) != 3:
            raise ValueError('Hkl device expects three inputs')
        (pos, params) = self._diffcalc.hkl_to_angles(hkl[0], hkl[1], hkl[2])

        width = max(len(k) for k in (params.keys() + list(self.diffhw.getInputNames())))
        fmt = '  %' + str(width) + 's : % 9.4f'

        lines = [self.diffhw.getName() + ' would move to:']
        for idx, name in enumerate(self.diffhw.getInputNames()):
            lines.append(fmt % (name, pos[idx]))
        lines[-1] = lines[-1] + '\n'
        for k in sorted(params):
            lines.append(fmt % (k, params[k]))
        return '\n'.join(lines)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        lines = ['hkl:']
        pos = self.diffhw.getPosition()
        try:
            (hkl, params) = self._diffcalc.angles_to_hkl(pos)
        except Exception, e:
            return "<hkl: %s>" % getMessageFromException(e)

        width = max(len(k) for k in params)
        lines.append('  ' + 'hkl'.rjust(width) + ' : %9.4f  %.4f  %.4f' % (hkl[0], hkl[1], hkl[2]))
        lines[-1] = lines[-1] + '\n'
        fmt = '  %' + str(width) + 's : % 9.4f'
        for k in sorted(params):
            lines.append(fmt % (k, params[k]))
        return '\n'.join(lines)
