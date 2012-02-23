class MockDiffcalc:

    def __init__(self, numberAngles):
        self.numberAngles = numberAngles
        self.params = {}

    def _hklToAngles(self, h, k, l):
        params = {}
        params['theta'] = 1.
        params['2theta'] = 12.
        params['Bin'] = 123.
        params['Bout'] = 1234.
        params['azimuth'] = 12345.
        return ([h] * self.numberAngles, params)

    def _anglesToHkl(self, pos):
        if len(pos) != self.numberAngles: raise ValueError
        params = {}
        params['theta'] = 1.
        params['2theta'] = 12.
        params['Bin'] = 123.
        params['Bout'] = 1234.
        params['azimuth'] = 12345.
        return ([pos[0]] * 3, params)

    def _setParameter(self, name, value):
        self.params[name] = value

    def _getParameter(self, name):
        return self.params[name]
