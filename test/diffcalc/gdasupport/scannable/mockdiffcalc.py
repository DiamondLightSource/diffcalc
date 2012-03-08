class MockParameterManager:

    def __init__(self):
        self.params = {}

    def set_parameter(self, name, value):
        self.params[name] = value

    def get(self, name):
        return self.params[name]


class MockDiffcalc:

    def __init__(self, numberAngles):
        self.numberAngles = numberAngles
        self.parameter_manager = MockParameterManager()

    def hkl_to_angles(self, h, k, l):
        params = {}
        params['theta'] = 1.
        params['2theta'] = 12.
        params['Bin'] = 123.
        params['Bout'] = 1234.
        params['azimuth'] = 12345.
        return ([h] * self.numberAngles, params)

    def angles_to_hkl(self, pos):
        if len(pos) != self.numberAngles: raise ValueError
        params = {}
        params['theta'] = 1.
        params['2theta'] = 12.
        params['Bin'] = 123.
        params['Bout'] = 1234.
        params['azimuth'] = 12345.
        return ([pos[0]] * 3, params)

