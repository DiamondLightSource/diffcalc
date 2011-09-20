from diffcalc.gdasupport.minigda.scannable.scannable import Scannable

class SingleFieldDummyScannable(Scannable):
    '''Dummy PD Class'''
    def __init__(self, name):
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(['%6.4f'])
        self.setLevel(3)
        self.currentposition=0.0

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self,new_position):
        self.currentposition = float(new_position)

    def getPosition(self):
        return self.currentposition

class DummyPD(SingleFieldDummyScannable):
    """For compatability with the gda's dummy_pd module"""
    pass
    
class MultiInputExtraFieldsDummyScannable(Scannable):
    '''Multi input Dummy PD Class supporting input and extra fields'''
    def __init__(self, name, inputNames, extraNames):
        self.setName(name)
        self.setInputNames(inputNames)
        self.setExtraNames(extraNames)
        self.setOutputFormat(['%6.4f']*(len(inputNames)+len(extraNames)))
        self.setLevel(3)
        self.currentposition=[0.0]*len(inputNames)
        
    def isBusy(self):
        return 0

    def asynchronousMoveTo(self,new_position):
        if type(new_position)==type(1) or type(new_position)==type(1.0):
            new_position=[new_position]
        assert len(new_position)==len(self.currentposition), "Wrong new_position size"
        for i in range(len(new_position)):
            if new_position[i] != None:
                self.currentposition[i] = float(new_position[i])

    def getPosition(self):
        extraValues = range(100,100+(len(self.getExtraNames())))
        return self.currentposition + map(float,extraValues)


class ZeroInputExtraFieldsDummyScannable(Scannable):
    '''Zero input/extra field dummy pd
    '''
    def __init__(self, name):
        self.setName(name)
        self.setInputNames([])
        self.setOutputFormat([])

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self,new_position):
        pass

    def getPosition(self):
        pass
