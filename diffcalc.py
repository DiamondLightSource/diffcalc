#!/usr/bin/python

import argparse
import subprocess
import os
import getpass

DIFFCALC_ROOT = os.path.split(os.path.realpath(__file__))[0]
MODULE_FOR_MANUALS = '_make_sixcircle_manual'

def main():
    parser = argparse.ArgumentParser(description='Diffcalc: A diffraction condition calculator of x-ray and neutron crystalography')
    parser.add_argument('--modules', dest='show_modules', action='store_true',
                        help='list available modules')
    parser.add_argument('--python', dest='use_python', action='store_true',
                        help='run within python rather than ipython')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='run in debug mode')
    parser.add_argument('--make-manuals', dest='make_manuals', action='store_true',
                        help='make .rst manual files by running template through sixcircle')
    parser.add_argument('module', type=str, nargs='?',
                        help='the module to startup with')
    args = parser.parse_args()
    
    # Create list of available modules
    module_names = []
    for module_path in os.listdir(os.path.join(DIFFCALC_ROOT, 'startup')):
        if not module_path.startswith('_') and module_path.endswith('.py'):
            module_names.append(module_path.split('.')[0])
    module_names.sort()
    
    if args.show_modules:
        print_available_modules(module_names)
        exit(1)      
    
    if not args.make_manuals and not args.module:   
        print "A module name should be provided. Choose one of:"
        print_available_modules(module_names)
        exit(1)
        
    if args.make_manuals:
        if args.module:
            print "When building the manuals no module should be given"
            exit(1)
        args.module = MODULE_FOR_MANUALS
        
    if not args.make_manuals and args.module not in module_names:
        print "The provided argument '%s' is not one of:" % args.module
        print_available_modules(module_names)
        exit(1)
    
    env = os.environ.copy()
    
    if 'PYTHONPATH' not in env:
        env['PYTHONPATH'] = ''
    env['PYTHONPATH'] = DIFFCALC_ROOT + ':' + env['PYTHONPATH']
    
    diffcmd_start_path = os.path.join(DIFFCALC_ROOT, 'diffcmd', 'start.py')
    
    exe = 'python' if args.use_python else 'ipython --no-banner --HistoryManager.hist_file=/tmp/ipython_hist_%s.sqlite' % getpass.getuser()
    cmd = "%s -i %s %s %s" % (exe, diffcmd_start_path, args.module, args.debug)
    print
    print 'Running: "%s"' % cmd
    subprocess.call(cmd, env=env, shell=True)
    
 
def print_available_modules(module_names):           
    lines = []
    for m in sorted(module_names):
        lines.append('   ' + m)
    print '\n'.join(lines)


if __name__ == '__main__':
    main()
# 
