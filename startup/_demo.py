'''
Created on 19 Feb 2017

@author: zrb13439
'''

try:
    import diffcmd.ipython
    __IPYTHON__  # @UndefinedVariable
    IPYTHON = True
except (ImportError, NameError):
    IPYTHON = False
    

GEOMETRIES = ['sixc', 'fivec', 'fourc', 'i16', 'i21']


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
        
        pos_cmd_001 = {
            'sixc': 'pos sixc [0 60 0 30 90 0]', # mu, delta, gam, eta, chi, phi
            'i16': 'pos sixc [0 90 30 0 60 0]', #  phi, chi, eta, mu, delta, gam
            'i21': 'pos fourc [60 30 0 0]',
            'fivec': 'pos fivec [60 0 30 90 0]',
            'fourc': 'pos fourc [60 30 90 0]'
            }[self.geometry]
 
        pos_cmd_011 = {
            'sixc': 'pos sixc [0 90 0 45 45 90]', # mu, delta, gam, eta, chi, phi
            'i16': 'pos sixc [90 45 45 0 90 0]', #  phi, chi, eta, mu, delta, gam
            'i21': 'pos fourc [90 90 0 0]',
            'fivec': 'pos fivec [90 0 45 45 90]',
            'fourc': 'pos fourc [90 45 45 90]'
            }[self.geometry]
                   
        self.echorun_magiccmd_list([
            'help ub',
            'pos wl 1',
            "newub 'test'",
            "setlat 'cubic' 1 1 1 90 90 90",
            'ub',
            'c2th [0 0 1]',
            pos_cmd_001,
            'addref [0 0 1]',
            'c2th [0 1 1]',
            pos_cmd_011,
            'addref [0 1 1]',
            'ub',
            'checkub'])
        
    def constrain(self):
        print_heading('Constraint demo')
        con_qaz_cmd = '' if self.geometry in ('fourc', 'i21') else 'con qaz 90'
        con_mu_cmd = 'con mu 0' if self.geometry in ('sixc', 'i16') else ''
        setmin_chi = 'setmin chi -180' if self.geometry == 'i21' else 'setmin chi 0'
        setmin_phi = 'setmin phi -180' if self.geometry == 'i21' else ''
        setmax_phi = 'setmax phi 180' if self.geometry == 'i21' else ''
        self.echorun_magiccmd_list([
            'help hkl',
            con_qaz_cmd,
            'con a_eq_b',
            con_mu_cmd,
            'con',
            'setmin delta 0',
            setmin_chi,
            setmin_phi,
            setmax_phi])
            
    def scan(self):
        print_heading('Scanning demo')
        if self.geometry == 'i16':
            diff_name = 'sixc'
        elif self.geometry == 'i21':
            diff_name = 'fourc'
        else:
            diff_name = self.geometry
        self.echorun_magiccmd_list([
            'setnphi [0 0 1]' if self.geometry == 'i21' else '',
            'pos hkl [0 0 1]' if self.geometry == 'i21' else 'pos hkl [1 0 0]',
            'scan delta 40 90 10 hkl ct 1',
            'pos hkl [0 1 0]',
            'scan h 0 1 .2 k l %s ct 1' % diff_name,
            'con psi',
            'scan psi 0 90 10 hkl [1 0 1] eta chi phi ct .1'])
 
    def echorun_magiccmd_list(self, magic_cmd_list):
        for cmd in magic_cmd_list:
            self.echorun_magiccmd(cmd)
            
    def remove_test_ubcalc(self):
        try:
            eval("rmub('test')", self.namespace)
        except (OSError, KeyError):
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
            if not tokens:
                return
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
