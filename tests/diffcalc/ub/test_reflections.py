from datetime import datetime
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.ub.reflections import ReflectionList
from diffcalc.hkl.vlieg.position  import VliegPosition
import unittest


class TestReflectionList(unittest.TestCase):
    
    def setUp(self):
        self._geometry = SixCircleGammaOnArmGeometry()
        self.reflist = ReflectionList(self._geometry, ['a', 'd', 'g', 'o', 'c', 'p'])
        self.time = datetime.now()
        self.reflist.addReflection(1, 2, 3, VliegPosition(0.1, 0.2, 0.3, 0.4, 0.5, 0.6), 10000, "ref1", self.time)
        self.reflist.addReflection(1.1, 2.2, 3.3, VliegPosition(0.11, 0.22, 0.33, 0.44, 0.55, 0.66), 11000, "ref2", self.time)

    def testAddReflection(self):
        self.assert_(len(self.reflist) == 2, "addReflection or __len__ failed")

    def testGetReflection(self):
        answered = self.reflist.getReflection(1)
        desired = ([1, 2, 3], VliegPosition(0.1, 0.2, 0.3, 0.4, 0.5, 0.6), 10000, "ref1", self.time)
        self.assert_(answered == desired, "GetReflection/SetReflection pair failed")
        
    def testRemoveReflection(self):
        self.reflist.removeReflection(1)
        answered = self.reflist.getReflection(1)
        desired = ([1.1, 2.2, 3.3], VliegPosition(0.11, 0.22, 0.33, 0.44, 0.55, 0.66), 11000, "ref2", self.time)
        self.assert_(answered == desired, "removeReflection failed")
        
    def testEditReflection(self):
        self.reflist.editReflection(1, 10, 20, 30, VliegPosition(0.1, 0.2, 0.3, 0.4, 0.5, 0.6), 100000, "newref1", self.time)
        self.assertEqual(self.reflist.getReflection(1),
                     ([10, 20, 30], VliegPosition(0.1, 0.2, 0.3, 0.4, 0.5, 0.6), 100000, "newref1", self.time))
        self.assertEqual(self.reflist.getReflection(2),
                     ([1.1, 2.2, 3.3], VliegPosition(0.11, 0.22, 0.33, 0.44, 0.55, 0.66), 11000, "ref2", self.time))
        
    def testSwapReflection(self):
        self.reflist.swapReflections(1, 2)
        self.assertEqual(self.reflist.getReflection(1),
                     ([1.1, 2.2, 3.3], VliegPosition(0.11, 0.22, 0.33, 0.44, 0.55, 0.66), 11000, "ref2", self.time))
        self.assertEqual(self.reflist.getReflection(2),
                     ([1, 2, 3], VliegPosition(0.1, 0.2, 0.3, 0.4, 0.5, 0.6), 10000, "ref1", self.time))

    def createRefStateDicts(self):
        ref_0 = {
            'h' : 1,
            'k' : 2,
            'l' : 3,
            'position' : (0.1, 0.2, 0.3, 0.4, 0.5, 0.6),
            'energy' : 10000,
            'tag' : "ref1",
            'time' : `self.time`
        }
        ref_1 = {
            'h' : 1.1,
            'k' : 2.2,
            'l' : 3.3,
            'position' : (0.11, 0.22, 0.33, 0.44, 0.55, 0.66),
            'energy' : 11000,
            'tag' : "ref2",
            'time' : `self.time`
        }
        return ref_0, ref_1

    def testGetState(self):
        ref_0, ref_1 = self.createRefStateDicts()
        expected = {'ref_0': ref_0, 'ref_1': ref_1}
        self.assertEqual(expected, self.reflist.getStateDict())
        
    def testRestoreFromStateDict(self):
        ref_0, ref_1 = self.createRefStateDicts()
        stateDict = {'ref_0': ref_0, 'ref_1': ref_1}
        self.reflist = ReflectionList(self._geometry, ['a', 'd', 'g', 'o', 'c', 'p'])
        self.reflist.restoreFromStateDict(stateDict)
        ref_0, ref_1 = self.createRefStateDicts()
        stateDict = {'ref_0': ref_0, 'ref_1': ref_1}
        self.assertEqual(stateDict, self.reflist.getStateDict())
