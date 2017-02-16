

from StringIO import StringIO
from IPython import get_ipython
import sys


TEST_INPUT="""
Diffcalc's Scannables
=====================

Please see :ref:`moving-in-hkl-space` and :ref:`scanning-in-hkl-space` for some relevant examples.

To list and show the current positions of your beamline's scannables
use ``pos`` with no arguments::
     
   >>> pos wl
   
should do nought, but this should be replaced::

   ==> pos wl 2  
   
should do the thing

   ==> abcd
"""



def echorun(magic_cmd):
    print "\n>>> " + str(magic_cmd)
     

    
def make_manual(input_file_path, output_file_path=None):
    
    # Read input file (should be .rst file)
    if input_file_path:
        with open(input_file_path, 'r') as f:
            input_string = f.read()
    else:
        input_string = TEST_INPUT
    
    output_lines = []
    for lineno, line in enumerate(input_string.split('\n')):
        if '==> STOP' in line:
            print "'==> STOP' found on line", lineno
            return
        output_lines = parse_line(line, lineno)
       
        print '\n'.join(output_lines)
    
#     try:
#         if output_file_path:
#             orig_stdout = sys.stdout
#             f = file(output_file_path, 'w')
#             sys.stdout = f
#         
#         
#     
#     finally:
#         if output_file_path:
#             sys.stdout = orig_stdout
#             f.close()

 
def parse_line(linein, lineno):
    output_lines = []
    if '==>' in linein:
        pre, cmd = linein.split('==>')
        _check_spaces_only(pre, lineno)
        cmd = cmd.strip()  # strip whitespace
        output_lines.append(pre + ">>> " + cmd)
        result_lines = _capture_magic_command_output(cmd, lineno)

        
        # append to output    
        for line in result_lines:
            output_lines.append(pre + line)
    else:
        output_lines.append(linein)
    return output_lines

    
def _check_spaces_only(s, lineno):
    for c in s:
        if c != ' ':
            raise Exception('Error on line %i: text preceeding --> must be '
                            'spaces only' % lineno)
            
def _capture_magic_command_output(magic_cmd, lineno):
    orig_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    
    def log_error(lineno, magic_cmd):
        msg = "Error on line %i evaluating '%s'" % (lineno, magic_cmd)
        sys.stderr.write('\n' + '=' * 79 + '\n' + msg + '\n' +'v' * 79 + '\n')
        return msg
    try:
        line_magics = get_ipython().magics_manager.magics['line']
        magic = magic_cmd.split(' ')[0]
        if magic not in line_magics:
            msg = log_error(lineno, magic_cmd)
            raise Exception(msg + " ('%s' is not a magic command)" % magic)
            
        get_ipython().magic(magic_cmd)
    except:
        log_error(lineno, magic_cmd)
        raise
    finally:
        sys.stdout = orig_stdout

    result_lines = result.getvalue().split('\n')
        
    # trim trailing lines which are whitespace only
    while result_lines and (result_lines[-1].isspace() or not result_lines[-1]):
        result_lines.pop()
        
    
    return result_lines
    

    