from diffcalc.geometry.sixc import SixCircleYouGeometry
from diffcalc.tools import matrixeq_
from diffcalc.ub.calculation import UBCalculation
from diffcalc.ub.paperspecific import YouUbCalcStrategy
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.utils import Position
from math import pi
from mock import Mock

try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix



#newub 'cubic'                   <-->  reffile('cubic) 
#setlat 'cubic' 1 1 1 90 90 90   <-->  latt([1,1,1,90,90,90])
#pos wl 1                        <-->  BLi.setWavelength(1)
#                                <-->  c2th([0,0,1]) --> 60
#pos sixc [0 60 0 30 1 1]        <-->  pos euler [1 1 30 0 60 0]
#addref 1 0 0                    <-->  saveref('100',[1, 0, 0])
#pos chi 91                      <-->  
#addref 0 0 1                    <-->  saveref('100',[1, 0, 0]) ; showref()
#                                      ubm('100','001')
#                                      ubm() -> array('d', [0.9996954135095477, -0.01745240643728364, -0.017449748351250637, 0.01744974835125045, 0.9998476951563913, -0.0003045864904520898, 0.017452406437283505, -1.1135499981271473e-16, 0.9998476951563912])


def posFromI16sEuler(phi, chi, eta, mu, delta, gamma):
    return Position(mu, delta, gamma, eta, chi, phi)

UB1 = Matrix(
             ((0.9996954135095477, -0.01745240643728364, -0.017449748351250637),
              (0.01744974835125045, 0.9998476951563913, -0.0003045864904520898),
              (0.017452406437283505, -1.1135499981271473e-16, 0.9998476951563912))
             ).times(2 * pi)
             
EN1 = 12.39842
REF1a = posFromI16sEuler(1, 1, 30, 0, 60, 0)
REF1b = posFromI16sEuler(1, 91, 30, 0, 60, 0)


class TestUBCalculationWithYouStrategy():
    """Testing the math only here.
    """
    
    def setUp(self):    
        geometry = SixCircleYouGeometry() # pass through
        hardware = Mock()
        hardware.getPhysicalAngleNames.return_value = ('m', 'd', 'n', 'e', 'c', 'p')
        self.ubcalc = UBCalculation(hardware, geometry, UbCalculationNonPersister(),
                                     YouUbCalcStrategy())
        
    def testAgainstI16Results(self):
        self.ubcalc.newCalculation('cubcalc')
        self.ubcalc.setLattice('latt', 1, 1, 1, 90, 90, 90)
        self.ubcalc.addReflection(1, 0, 0, REF1a, EN1, '100', None)
        self.ubcalc.addReflection(0, 0, 1, REF1b, EN1, '001', None)
        self.ubcalc.calculateUB()
        matrixeq_(self.ubcalc.getUBMatrix(), UB1)
