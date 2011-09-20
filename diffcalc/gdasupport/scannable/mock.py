class MockMotor:
    def __init__(self, name = 'mock'):
        self.pos = 0.0
        self.busy = False
        self.name = name
        
    def getName(self):
        return self.name
        
    def asynchronousMoveTo(self,pos):
        self.busy = True
        self.pos = float(pos)
        
    def getPosition(self):
        return self.pos
    
    def isBusy(self):
        return self.busy
    
    def makeNotBusy(self):
        self.busy = False
        
    def getOutputFormat(self):
        return ['%f']