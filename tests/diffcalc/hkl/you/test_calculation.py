from diffcalc.hkl.you.calculation import youAnglesToHkl, YouHklCalculator
from diffcalc.tools import arrayeq_, assert_array_almost_equal, \
    assert_second_dict_almost_in_first
from diffcalc.utils import Position
from math import pi
from nose.plugins.skip import SkipTest
from tests.diffcalc.hkl.test_calcvlieg import createMockDiffractometerGeometry, \
    createMockHardwareMonitor, createMockUbcalc

try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

TORAD = pi / 180
TODEG = 180 / pi

UB1 = Matrix(
             ((0.9996954135095477, -0.01745240643728364, -0.017449748351250637),
              (0.01744974835125045, 0.9998476951563913, -0.0003045864904520898),
              (0.017452406437283505, -1.1135499981271473e-16, 0.9998476951563912))
            ).times(2 * pi)
             
EN1 = 12.39842


def posFromI16sEuler(phi, chi, eta, mu, delta, gamma):
    return Position(mu, delta, gamma, eta, chi, phi)

class TestAnglesToHklI16Examples():

    def test_anglesToHkl_mu_0_gam_0(self):
        pos = posFromI16sEuler(1, 1, 30, 0, 60, 0).inRadians()
        arrayeq_(youAnglesToHkl(pos, EN1, UB1), [1, 0, 0])
    
    def test_anglesToHkl_mu_0_gam_10(self):
        pos = posFromI16sEuler(1, 1, 30, 0, 60, 10).inRadians()
        arrayeq_(youAnglesToHkl(pos, EN1, UB1), [1.00379806, -0.006578435, 0.08682408])
        
    def test_anglesToHkl_mu_10_gam_0(self):
        pos = posFromI16sEuler(1, 1, 30, 10, 60, 0).inRadians()
        arrayeq_(youAnglesToHkl(pos, EN1, UB1), [0.99620193, 0.0065784359, 0.08682408])
        
    def test_anglesToHkl_arbitrary(self):
        pos = posFromI16sEuler(1.9, 2.9, 30.9, 0.9, 60.9, 2.9).inRadians()
        arrayeq_(youAnglesToHkl(pos, EN1, UB1), [1.01174189, 0.02368622, 0.06627361])
    

class TestCalc():
    
    def __init__(self):
        self.calc = YouHklCalculator(createMockUbcalc(None),
                                     createMockDiffractometerGeometry(),
                                     createMockHardwareMonitor())
        
    def setub(self, a1, a2=None):
        ub = Matrix(a1) if a2 is None else Matrix(a1).times(Matrix(a2))
        self.calc._ubcalc.getUBMatrix.return_value = ub
          
    def setconstraints(self, d):
        self.calc.constraints._constrained = d  
    
    
    def checkAnglesToVirtualAngles(self, pos_tuple, energy, virtual_e):
        pos = Position(*pos_tuple)
        assert_second_dict_almost_in_first(self.calc.anglesToVirtualAngles(pos, energy),
                                 virtual_e)
    
    def checkAnglesToHkl(self, postuple, energy, hkl_e, virtual_e):
        pos = Position(*postuple)
        hkl, virtual = self.calc.anglesToHkl(pos, energy)
        assert_array_almost_equal(hkl, hkl_e, 5)
        assert_second_dict_almost_in_first(virtual, virtual_e)
    
    def checkHklToAngles(self, hkl, energy, postuple_e, virtual_e):
        postuple, virtual = self.calc.hklToAngles(hkl[0], hkl[1], hkl[2], energy)
        assert_array_almost_equal(postuple.totuple(), postuple_e)
        assert_second_dict_almost_in_first(virtual, virtual_e)


class TestCalc_CubicFromBlissTutorial(TestCalc):
    
    def __init__(self):
        TestCalc.__init__(self)
        self.setub(((1, 0, 0), (0, -1, 0), (0, 0, -1)),
                   ((4.07999, 0, 0), (0, 4.07999, 0), (0, 0, 4.07999)))
        self.setconstraints({'a_eq_b': None, 'mu':0, 'nu':0})
        self.e = 12.39842 / 1.54
    
    def test1(self):
        raise SkipTest()
        self.setconstraints({'a_eq_b': None, 'mu':0, 'nu':0})
        hkl = 0.7, 0.9, 1.3,
        postuple = 0, 119.669750, 0, 59.834875, -48.747500, 307.87498365109815
        energy = self.e
        virtual = {}
        yield self.checkAnglesToVirtualAngles, postuple, energy, virtual
        yield self.checkAnglesToHkl, postuple, energy, hkl, virtual
        yield self.checkHklToAngles, hkl, energy, postuple, virtual

#constraints = {'a_eq_b': None, 'mu':0, 'n':0}
#calcs = []
#calcs.append(energy, (0.7, 0.9, 1.3),
#             (0.000000, 27.352179, 0.000000, 13.676090, 37.774500, 53.965500),
#             {'alpha':8.3284 ,'beta':8.3284 ,'twotheta':27.3557})#  'rho':36.5258 , 'eta':0.1117
#        
#        
#scenarios.append
#ac.hklList=[]
#ac.hklList.append( (0.7, 0.9, 1.3) )
#ac.posList.append(P(0.000000, 27.352179, 0.000000, 13.676090, 37.774500, 53.965500))
#ac.paramList.append({'Bin':8.3284 ,'Bout':8.3284 , 'rho':36.5258 , 'eta':0.1117 ,'twotheta':27.3557})
#
#ac.hklList.append( (1,0,0) )
#ac.posList.append(P(0.000000, 18.580230, 0.000000, 9.290115, -2.403500, 3.589000))
#ac.paramList.append({'Bin': -0.3880,'Bout': -0.3880, 'rho':-2.3721 , 'eta': -0.0089,'twotheta':18.5826})
#
#ac.hklList.append( (0,1,0) )
#ac.posList.append(P(0.000000, 18.580230, 0.000000, 9.290115, 0.516000, 93.567000))
#ac.paramList.append({'Bin': 0.0833 ,'Bout': 0.0833, 'rho': 0.5092, 'eta': -0.0414 ,'twotheta':18.5826})
#
#ac.hklList.append( (1, 1, 0) )
#ac.posList.append(P(0.000000, 26.394192, 0.000000, 13.197096, -1.334500, 48.602000))
#ac.paramList.append({'Bin': -0.3047,'Bout': -0.3047, 'rho': -1.2992, 'eta': -0.0351 ,'twotheta':26.3976})
#
############################# SESSION3 ############################
## AngleCalc scenarios from SPEC sixc. using crystal and alignment
#session3 = SessionScenario()
#session3.name = "spec_sixc_b16_270608"
#session3.time = datetime.now()
#session3.lattice = ((3.8401, 3.8401, 5.43072, 90, 90, 90))
#session3.bmatrix = (((1.636204, 0, 0),(0, 1.636204, 0), (0, 0, 1.156971)))
#session3.umatrix =  ( (0.997161, -0.062217,  0.042420),
#               (0.062542,  0.998022, -0.006371),
#               (-0.041940,  0.009006,  0.999080) )        
#session3.ref1 = Reflection(1, 0, 1.0628, Position(5.000, 22.790, 0.000, 1.552, 22.400, 14.255), 12.39842/1.24, 'ref1', session3.time)
#session3.ref2 = Reflection(0, 1, 1.0628, Position(5.000, 22.790, 0.000, 4.575, 24.275, 101.320), 12.39842/1.24, 'ref2', session3.time)
#session3.ref1calchkl = (1, 0, 1.0628)
#session3.ref2calchkl = (-0.0329, 1.0114, 1.04)
## sixc-0a : fixed omega = 0
#ac = CalculationScenario('sixc-0a', 'sixc', '0', 12.39842/1.24, '4cBeq',1)
#ac.alpha=0; ac.gamma=0
#ac.w = 0
#### with 'omega_low':-90, 'omega_high':270, 'phi_low':-180, 'phi_high':180
#ac.hklList=[]
#ac.hklList.append( (0.7, 0.9, 1.3) )
#ac.posList.append(P(0.000000, 27.352179, 0.000000, 13.676090, 37.774500, 53.965500))
#ac.paramList.append({'Bin':8.3284 ,'Bout':8.3284 , 'rho':36.5258 , 'eta':0.1117 ,'twotheta':27.3557})
#
#ac.hklList.append( (1,0,0) )
#ac.posList.append(P(0.000000, 18.580230, 0.000000, 9.290115, -2.403500, 3.589000))
#ac.paramList.append({'Bin': -0.3880,'Bout': -0.3880, 'rho':-2.3721 , 'eta': -0.0089,'twotheta':18.5826})
#
#ac.hklList.append( (0,1,0) )
#ac.posList.append(P(0.000000, 18.580230, 0.000000, 9.290115, 0.516000, 93.567000))
#ac.paramList.append({'Bin': 0.0833 ,'Bout': 0.0833, 'rho': 0.5092, 'eta': -0.0414 ,'twotheta':18.5826})
#
#ac.hklList.append( (1, 1, 0) )
#ac.posList.append(P(0.000000, 26.394192, 0.000000, 13.197096, -1.334500, 48.602000))
#ac.paramList.append({'Bin': -0.3047,'Bout': -0.3047, 'rho': -1.2992, 'eta': -0.0351 ,'twotheta':26.3976})
#
#session3.calculations.append(ac)
#
#



############################ SESSION1 ############################









########################################################################
#def sessions():
#    return (session1, session2, session3)

