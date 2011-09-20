from numbers import *
from math import *
import copy
md=[[[1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,0,-1]],
    [[1,0,0,0],[0,-1,0,0],[0,0,1,0],[0,0,0,-1]],
    [[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]]]
class quat:
    #builder
    def __init__(self,a=0,b=0,c=0,d=0):
        self.q=[float(a),float(b),float(c),float(d)]
    # quaternion as string or for printing
    def __str__(self):
        a=''
        lab=['i','j','k']
        a=str(self.q[0])
        if self.q[1]>=0:
            a=a+'+'
        for i in range(1,3):
                if self.q[i+1]<0:
                    a=a+str(self.q[i])+lab[i-1]
                elif self.q[i+1]>=0:
                    a=a+str(self.q[i])+lab[i-1]+'+'
 
        a=a+str(self.q[3])+lab[2]
        return a
    # addition of quaternions
    def __add__(self,ob2):
        s=quat()
        for i in range(4):
            s.q[i]=self.q[i]+ob2.q[i]
        return s    
    # subtraction of quaternions
    def __sub__(self,ob2):
                s=quat()
                for i in range(4):
                        s.q[i]=self.q[i]-ob2.q[i]
                return s
    # quaternion product (in R3 cross product)
    def __mul__(self,ob2):
        s=quat(0,0,0,0)
        #matrices and vector used in quaternion product (not math just for the index of the quaternion
        or1=[0,1,2,3]
        or2=[1,0,3,2]
 
        v=[[1,-1,-1,-1],[1,1,1,-1],[1,-1,1,1],[1,1,-1,1]]
        m=[or1,or2,[i for i in reversed(or2)],[i for i in reversed(or1)]]
        for k in range(4):
            a=0
            for i in range(4):
#    just for debugging         print self.q[m[0][i]]
#                    print ob2.q[m[k][i]]
                    a=a+(self.q[m[0][i]])*(float(v[k][i])*ob2.q[m[k][i]])
            s.q[k]=a    
        return s
    # product by scalar
    def __rmul__(self,ob):
        s=quat()
        for i in range(4):
            s.q[i]=self.q[i]*ob
        return s
    # division of quaternions, quat/quat 
    def __div__(self,ob):
        s=quat()
        b=copy.deepcopy(ob)
        ob.C()
        c=(b*ob).q[0]
        s=(self*ob)
        a=(1/c)*s
        ob.C()
        return a
    # norm of a quaternion returns an scalar
    def norm(self):
        s=0
        for i in range(4):
            s=s+self.q[i]**2
        return float(s**(0.5))
    # conjugates a quaternion a: a.C() -> a=a+bi+cj+dk --> a.C()=a-bi-cj-dk
    def C(self):
        s=self
        for i in range(1,4):
            s.q[i]=s.q[i]*(-1)
        return s
    # method used to create a rotation quaternion to rotate any vector defined as a quaternion 
    # with respect to the vector vect theta 'radians' 
    def rotQuat(self,theta,vect):
        self.q=[cos(theta/2.0),vect[0]*sin(theta/2.0),vect[1]*sin(theta/2.0),vect[2]*sin(theta/2.0)]
# rotates a vector or a vector defined as a quaternion 0+xi+yj+zk with respect to a quaternion
def rotate(vect,quatern):
    if "list" in str(type(vect)):
        a=quat()
        for i in range(3):
            a.q[i+1]=vect[i]
        vect=a
    rotq=(quatern*vect)/quatern
    return rotq
 
# rotates a vector v_to_rotate theta 'radians' with respect to v_about, both are vectors
# but it uses quaternions
def rotateH(v_to_rotate,theta,v_about):
    a=quat(0,v_to_rotate[0],v_to_rotate[1],v_to_rotate[2])
    b=quat(cos(theta/2),v_about[0]*sin(theta/2),v_about[1]*sin(theta/2),v_about[2]*sin(theta/2))
    v_rotated=[0,0,0]
    vq=rotate(a,b)
    for i in range(4):
        if i<3:
            v_rotated[i]=vq.q[i+1]
    return v_rotated
 
#metric tensor defaul basis [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
#fe. for Minkowski use [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,-1]]
# q1T[basis]q2
# for R3 MT(A,B,[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,0]])
 
def MT(q1,q2,basis=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]):
    a=[0,0,0,0]
    s=0  
    for i in range(4):
        for j in range(4):
            a[i]=a[i]+q2.q[j]*basis[i][j]
    for i in range(4):
        s=s+q1.q[i]*a[i]    
    return s
 
def quat_to_rotMat(q):
    rm=[[0,0,0],[0,0,0],[0,0,0]]
    for i in range(3):
        rm[i][i]=MT(q,q,md[i])
    rm[0][1]=2*(q.q[1]*q.q[2]-q.q[0]*q.q[3])
    rm[0][2]=2*(q.q[1]*q.q[3]+q.q[0]*q.q[2])
    rm[1][0]=2*(q.q[1]*q.q[2]+q.q[0]*q.q[3])
    rm[1][2]=2*(q.q[2]*q.q[3]-q.q[0]*q.q[1])
    rm[2][0]=2*(q.q[1]*q.q[3]-q.q[0]*q.q[2])
    rm[2][1]=2*(q.q[3]*q.q[2]+q.q[0]*q.q[1])    
    return rm

def quatrot(theta, vect):
    q=quat()
    q.rotQuat(theta, vect)
    return q
    
# You geometry
    
def calcphi(phi):
    return quatrot(-phi,[0,0,-1])

def calcchi(chi):
    return quatrot(chi,[0,1,0])

def calceta(eta):
    return quatrot(eta,[1,0,0])

def calcmu(mu):
    return quatrot(mu,[1,0,0])


