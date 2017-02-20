'''
Created on 19 Feb 2017

@author: zrb13439
'''

import diffcmd.ipython
from gevent.ares import result

try:
    __IPYTHON__  # @UndefinedVariable
    IPYTHON = True
except NameError:
    IPYTHON = False
    

GEOMETRIES = ['sixc', 'fivec', 'fourc']


def echo(cmd):
    print "\n>>> " + str(cmd)

    
def print_heading(s):
    print '\n' + '=' * len(s) + '\n' + s + '\n' + '=' * len(s)


class Demo(object):
    
    def __init__(self, namespace, geometry):
        self.namespace = namespace
        assert geometry in GEOMETRIES
        self.geometry = geometry

    def all(self):
        self.orient()
        self.constrain()
        self.scan()
                 
    def orient(self):
        print_heading('Orientation demo')
        self.remove_test_ubcalc()
        
        pos_cmd = {
            'sixc': 'pos sixc [0 60 0 30 0 0]',
            'fivec': 'pos fivec [60 0 30 0 0]',
            'fourc': 'pos fourc [60 30 0 0]'
            }[self.geometry]
        
        self.echorun_magiccmd_list([
            'help ub',
            'pos wl 1',
            "newub 'test'",
            "setlat 'cubic' 1 1 1 90 90 90",
            'ub',
            'c2th [1 0 0]',
            pos_cmd,
            'addref [1 0 0]',
            'c2th [0 1 0]',
            'pos phi 90',
            'addref [0 1 0]',
            'ub',
            'checkub'])
        
    def constrain(self):
        print_heading('Constraint demo')
        self.echorun_magiccmd_list([
            'help hkl',
            'con qaz 90',
            'con a_eq_b',
            'con mu 0',
            'con',
            'setmin delta 0',
            'setmin chi 0'])
            
    def scan(self):
        print_heading('Scanning demo')
        self.echorun_magiccmd_list([
            'pos hkl [1 0 0]',
            'scan delta 40 80 10 hkl ct 1',
            'pos hkl [0 1 0]',
            'scan h 0 1 .2 k l %s ct 1' % self.geometry,
            'con psi',
            'scan psi 0 90 10 hkl [1 0 1] eta chi phi ct .1'])
 
    def echorun_magiccmd_list(self, magic_cmd_list):
        for cmd in magic_cmd_list:
            self.echorun_magiccmd(cmd)
            
    def remove_test_ubcalc(self):
        try:
            eval("rmub('test')", self.namespace)
        except OSError:
            pass
 
    def echorun_magiccmd(self, magic_cmd):
        if IPYTHON:
            from IPython import get_ipython
            echo(magic_cmd)
            get_ipython().magic(magic_cmd) 
        else:  # Python
            # python's help is interactive. Handle specially 
            if magic_cmd == 'help ub':
                
                echo("help ub")
                exec("print ub.__doc__", self.namespace)
                return
            if magic_cmd == 'help hkl':
                echo("help(hkl)")
                exec("print hkl.__doc__", self.namespace)
                return  
            
            # Echo the Python version of the magic command   
            tokens = diffcmd.ipython.tokenify(magic_cmd)
            python_cmd = tokens.pop(0) + '(' + ', '.join(tokens) + ')'
            python_cmd = python_cmd.replace('[, ', '[')
            python_cmd = python_cmd.replace(',]', ']')
            python_cmd = python_cmd.replace(', ]', ']')
            echo(python_cmd)
            
            # Run the Python version of the magic command
            elements = diffcmd.ipython.parse(magic_cmd, self.namespace)
            func = elements.pop(0)
            result = func(*elements)
            if result:
                print result
