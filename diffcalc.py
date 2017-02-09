#!/usr/bin/python

import argparse
import subprocess
import os


DIFFCALC_ROOT = os.path.split(os.path.realpath(__file__))[0]


def main():
    parser = argparse.ArgumentParser(description='Start Diffcalc')
    parser.add_argument('module', metavar='MODULE', type=str, nargs='?',
                        help='the module to startup with')
    args = parser.parse_args()
    
    # Create list of available modules
    module_files = os.listdir(os.path.join(DIFFCALC_ROOT, 'startup'))
    module_names = set([s.split('.')[0] for s in module_files])
    
    
    if not args.module:   
        print "A module name should be provided. Choose one of:"
        print_available_modules(module_names)
        exit(1)
        
    if args.module not in module_names:
        print "The provided argument '%s' is not one of:" % args.module
        print_available_modules(module_names)
        exit(1)
    module_path = os.path.join(DIFFCALC_ROOT, 'startup', args.module) + '.py'
    cmd = "ipython -i %s" % module_path
    print "Running command: '%s'" % cmd
    subprocess.call(cmd, env=create_environent_dict(), shell=True)
    
 
def print_available_modules(module_names):           
    lines = []
    for m in sorted(module_names):
        lines.append('   ' + m)
    print '\n'.join(lines)


def create_environent_dict(): 
    my_env = os.environ.copy()
    if "PYTHONPATH" not in my_env:
        my_env["PYTHONPATH"] = ''
    my_env["PYTHONPATH"] = DIFFCALC_ROOT + ':' + my_env["PYTHONPATH"]
    return my_env


if __name__ == '__main__':
    main()
# 