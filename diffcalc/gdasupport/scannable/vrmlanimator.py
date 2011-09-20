from gda.device.scannable import DottedAccessScannableMotionBase
import time
import threading
import socket
PORT=4567

#import scannable.vrmlModelDriver
#reload(scannable.vrmlModelDriver);from scannable.vrmlModelDriver import VrmlModelDriver, LinearProfile, MoveThread;fc=VrmlModelDriver('fc',['alpha','delta','omega', 'chi','phi'], speed=30, host='diamrl5104')
#alpha = fc.alpha
#delta = fc.delta
#omega = fc.omega
#chi = fc.chi
#phi = fc.phi


def connect_to_socket(host, port):
    print "Connecting to %s on port %d" % (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sock.connect((host, port)) 
    print "Connected"
    socketfile = sock.makefile('rw', 0)
    return socketfile

    
class LinearProfile(object):
    
    def __init__(self, v, t_accel, startList, endList):
        assert len(startList) == len(endList)
        self.v = float(v)
        self.start = startList
        self.end = endList
        self.t_accel=t_accel
        
        distances = [e-s for e,s in zip(self.end, self.start)]
        max_distance = max([abs(d) for d in distances])
        if max_distance==0:
            self.delta_time=0
        else:
            self.delta_time = abs(max_distance/self.v)
            self.speeds = [d/self.delta_time for d in distances]
        self.start_time = time.time()
        
    def getPosition(self):
        if self.start_time == None:
            return self.start
        if not self.isMoving():
            return self.end
        t = abs(float(time.time()-self.start_time))
        if t > self.delta_time:
            # we are in the deceleration phase (i.e paused for now)
            return self.end
        return [s+v*t for s, v in zip(self.start, self.speeds)]
            
    def isMoving(self):
        return time.time() < self.start_time + self.delta_time + self.t_accel  
        

class MoveThread(threading.Thread):
    
    def __init__(self, profile, socketfile, axisNames):
        threading.Thread.__init__(self)
        self.profile = profile
        self.socketfile = socketfile
        self.axisNames = axisNames
    
    def run(self):
        while self.profile.isMoving():
            self.update()
            time.sleep(.1)   
        self.update()

    def update(self):
        pos = self.profile.getPosition()
        d = dict(zip(map(str,self.axisNames), pos))
        if self.socketfile:
            self.socketfile.write(`d`+'\n')


class VrmlModelDriver(DottedAccessScannableMotionBase):
    
    def __init__(self, name, axes_names, host=None, speed=60, t_accel=.1, format='%.3f'):
        self.name = name
        self.inputNames = list(axes_names)
        self.extraNames = []
        self.outputFormat = [format]*len(self.inputNames)
        self.completeInstantiation()
        self.__last_target= [0.] * len(self.inputNames)
        self.verbose = False
        self.move_thread = None
        self.speed = speed
        self.host = host
        self.t_accel = t_accel
        self.socketfile = None
        if self.host:
            try:
                self.connect()
            except socket.error:
                print "Failed to connect to %s:%s"%(self.host,`PORT`)
                print "Connect with: %s.connect()" % self.name
                
    def connect(self):
        self.socketfile = connect_to_socket(self.host, PORT)
        self.rawAsynchronousMoveTo(self.__last_target)
        
    def isBusy(self):
        if self.move_thread==None:
            return False
        return self.move_thread.profile.isMoving()
    
    def rawGetPosition(self):
        if self.move_thread==None:
            return self.__last_target
        else:
            return self.move_thread.profile.getPosition()
    
    def rawAsynchronousMoveTo(self, targetList):
        if self.isBusy():
            raise Exception(self.name + ' is already moving')
        if self.verbose:
            print self.name + ".rawAsynchronousMoveTo(%s)" % `targetList`
        
        for i, target in enumerate(targetList):
            if target == None:
                targetList[i] = self.__last_target[i]
        profile = LinearProfile(self.speed, self.t_accel, self.__last_target, targetList)
        self.move_thread = MoveThread(profile, self.socketfile, self.inputNames)
        self.move_thread.start()
        self.__last_target = targetList
        
    def getFieldPosition(self, index):
        return self.getPosition()[index]
    
    def __del__(self):
        self.socketfile.close()
        
#class TrapezoidProfile(object):
#    
#    def __init__(self, t_accel, v_max, delta_x):
#        self.t_a = t_accel
#        self.v_m = v_max
#        self.delta_x = delta_x
#        
#        self.t_c = (self.X - self.v_m*self.t_a) / self.v_m
#        
#    def x(self, t):
#        if self.t_c <=0:
#            return self.__xshort(t)
#        else:
#            return self.__xlong(t)
#        
#    def __xshort(self, t):
#        delta_t = 2 * sqrt(self.delta_x*self.t_a/self.v_m)
#        if t <= .5*delta_t:
#            return (.5*self.v_m/self.t_a) * t**2
#        else:
#            v_peak = (self.v_m/self.t_a) * .5*delta_t
#            return (t-.5*delta_t)*v_peak - (t-.5*delta_t)**2 ####HERE, bugged still
#            self.delta_x/2 