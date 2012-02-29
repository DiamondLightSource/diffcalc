from diffcalc.hkl.you.position import YouPosition


class YouGeometry(object):

    def __init__(self, name):
        self.name = name

    def physical_angles_to_internal_position(self, physicalAngles):
        raise NotImplementedError()

    def internal_position_to_physical_angles(self, physicalAngles):
        raise NotImplementedError()

    def create_position(self, *args):
        return YouPosition(*args)


class SixCircle(YouGeometry):
    def __init__(self):
        YouGeometry.__init__(self, name='sixc_you')

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        return YouPosition(*physical_angle_tuple)

    def internal_position_to_physical_angles(self, internal_position):
        return internal_position.totuple()
