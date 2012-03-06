def getNameFromScannableOrString(o):
        try:  # it may be a scannable
            return o.getName()
        except AttributeError:
            return str(o)
            raise TypeError()


class DummyParameterManager(object):

    def getParameterDict(self):
        return {}

    def _setParameter(self, name, value):
        raise KeyError(name)

    def _getParameter(self, name):
        raise KeyError(name)

    def update_tracked(self):
        pass
