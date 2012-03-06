import unittest

try:
    from gdascripts.pd.dummy_pds import DummyPD  # @UnusedImport
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import DummyPD

from diffcalc.gdasupport.scannable.mock import MockMotor
from diffcalc.gdasupport.minigda.scannable import \
    SingleFieldDummyScannable
from diffcalc.gdasupport.minigda.scannable import Scannable
from diffcalc.gdasupport.scannable.base import ScannableGroup


class TestScannable(unittest.TestCase):

    def setUp(self):
        self.scannable = Scannable()

    def testSomethingUnrelated(self):
        a = SingleFieldDummyScannable('a')
        print isinstance(a, Scannable)


def createDummyAxes(names):
    result = []
    for name in names:
        result.append(DummyPD(name))
    return result


class TestScannableGroup(unittest.TestCase):

    def setUp(self):
        self.a = MockMotor('a')
        self.b = MockMotor('bbb')
        self.c = MockMotor('c')
        self.sg = ScannableGroup('abc', (self.a, self.b, self.c))

    def testInit(self):
        self.assertEqual(list(self.sg.getInputNames()), ['a', 'bbb', 'c'])
        self.assertEqual(self.sg.getPosition(), [0.0, 0.0, 0.0])

    def testAsynchronousMoveTo(self):
        self.sg.asynchronousMoveTo([1, 2.0, 3])
        self.assertEqual(self.sg.getPosition(), [1.0, 2.0, 3.0])

    def testAsynchronousMoveToWithNones(self):
        self.sg.asynchronousMoveTo([1.0, 2.0, 3.0])
        self.sg.asynchronousMoveTo([None, None, 3.2])
        self.assertEqual(self.sg.getPosition(), [1.0, 2.0, 3.2])

    def testGetPosition(self):
        # implicitely tested above
        pass

    def testIsBusy(self):
        self.assertEqual(self.sg.isBusy(), False)
        self.sg.asynchronousMoveTo([1.0, 2.0, 3.0])
        self.assertEqual(self.sg.isBusy(), True)
        self.b.makeNotBusy()
        self.assertEqual(self.sg.isBusy(), True)
        self.a.makeNotBusy()
        self.c.makeNotBusy()
        self.assertEqual(self.sg.isBusy(), False)
