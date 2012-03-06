from diffcalc.gdasupport.diffcalc_factory import create_objects
from nose.tools import eq_

a = None

expected_objects = ['delref', 'en', 'uncon', 'showref', 'cons', 'l',
                    'hardware', 'checkub', 'listub', 'mu_par', 'saveubas',
                    'eta_par', 'ct', 'setmin', 'ub', 'setcut', 'chi', 'setlat',
                    'qaz', 'addref', 'swapref', 'newub', 'naz', 'sixc', 'nu',
                    'sim', 'diffcalcdemo', 'phi', 'psi', 'sigtau', 'wl',
                    'setmax', 'dc', 'loadub', 'beta', 'hkl', 'delta', 'alpha',
                    'nu_par', 'trialub', 'delta_par', 'h', 'k', 'phi_par',
                    'mu', 'setu', 'eta', 'editref', 'con', 'setub', 'c2th',
                    'calcub', 'chi_par', 'hklverbose']

# Placeholders for names to be added to globals for benefit of IDE
delref = en = uncon = showref = cons = l = hardware = checkub = listub = None
mu_par = saveubas = eta_par = ct = setmin = ub = setcut = chi = setlat = None
qaz = addref = swapref = newub = naz = sixc = nu = sim = diffcalcdemo = None
phi = psi = sigtau = wl = setmax = dc = loadub = beta = hkl = delta = None
alpha = nu_par = trialub = delta_par = h = k = phi_par = mu = setu = eta = None
editref = con = setub = c2th = calcub = chi_par = hklverbose = None


class TestDiffcalcFactorySixc():

    def setup(self):
        axis_names = ('mu', 'delta', 'nu', 'eta', 'chi', 'phi')
        virtual_angles = ('theta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta')
        self.objects = create_objects(
            engine_name='you',
            geometry='sixc',
            dummy_axis_names=axis_names,
            dummy_energy_name='en',
            hklverbose_virtual_angles_to_report=virtual_angles,
            simulated_crystal_counter_name='ct'
            )
        globals().update(self.objects)
        print self.objects.keys()

    def test_created_objects(self):
        eq_(set(self.objects.keys()), set(expected_objects))

    def test_scratch(self):
        help(ub)
