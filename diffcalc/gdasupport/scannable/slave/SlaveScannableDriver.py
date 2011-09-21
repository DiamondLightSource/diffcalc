
class SlaveScannableDriver(object):

    def __init__(self, slaveScannable):
        self.slaveScannable = slaveScannable
        
    def isBusy(self):
        return self.slaveScannable.isBusy()
    
    def triggerAsynchronousMove(self, triggerPos):
        self.slaveScannable.asynchronousMoveTo(self.slaveFromTriggerPos(triggerPos))
        
    def slaveFromTriggerPos(self, triggerPos):
        raise RuntimeError("slaveFromTriggerPos should be overridden for your application")
    
