'''
Created on 6 May 2016

@author: walton
'''
from diffcalc import settings
from diffcalc.gdasupport.scannable.sim import sim
import textwrap
from diffcalc.util import bold


class ExternalCommand(object):
    """Instances found in a command_list by format_command_help will
    result in documentation for a command without there actually being one.
    """
    def __init__(self, docstring):
        """Set the docstring that will be pulled off by format_command_help.
        """
        self.__doc__ = docstring
        self.__name__ = ''


WIDTH = 27
INDENT = 3


def format_command_help(command_list):

    row_list = _command_list_to_table_cells(command_list)
    lines = []
    for row_cells in row_list:
        if len(row_cells) == 1:
            heading = row_cells[0]
            lines.append('')
            lines.append(bold(heading))
            lines.append('')
        elif len(row_cells) == 2:
            cell1, cell2 = row_cells
    
            cell1_lines = textwrap.wrap(cell1, WIDTH, subsequent_indent='    ')
            cell2_lines = textwrap.wrap(cell2, 79 - INDENT - 3 - WIDTH)
            
            first_line = True
            while cell1_lines or cell2_lines:
                line = ' ' * INDENT
                if cell1_lines:
                    line += cell1_lines.pop(0).ljust(WIDTH)
                else:
                    line += ' ' * (WIDTH)
                line += ' : ' if first_line else '   '
                if cell2_lines:
                    line += cell2_lines.pop(0)
                lines.append(line)
                first_line = False

    return '\n'.join(lines)

        
def format_commands_for_rst_table(title, command_list):
    W1 = WIDTH  # internal width
    W2 = 79 - W1 - 3  # internal width
    HORIZ_LINE = '+-' + '-' * W1 + '-+-' + '-' * W2 + '-+'
    
    row_list = _command_list_to_table_cells(command_list)
    
    lines = []
  
    lines.append(HORIZ_LINE)  # Top line
    for row_cells in row_list:
        if len(row_cells) == 1:
            lines.append('| ' + ('**' + row_cells[0] + '**').ljust(W1 + W2 + 3) + ' |')
        
        elif len(row_cells) == 2:
            cmd_and_args = row_cells[0].split(' ', 1)
            cmd = cmd_and_args[0]
            args = cmd_and_args[1] if len(cmd_and_args) == 2 else ''
            cell1 = '**-- %s** %s' % (cmd, args)
            cell1_lines = textwrap.wrap(cell1, W1)  #, subsequent_indent='    ')
            cell2_lines = textwrap.wrap(row_cells[1], W2)
            
            while cell1_lines or cell2_lines:
                line = '| '
                line += (cell1_lines.pop(0) if cell1_lines else '').ljust(W1)
                line += ' | '
                line += (cell2_lines.pop(0) if cell2_lines else '').ljust(W2)
                line += ' |'
                lines.append(line)
        
        else:
            assert False
        
        lines.append(HORIZ_LINE)
    return lines

    
    
    
                
def _command_list_to_table_cells(command_list):
    row_list = []
    for obj in command_list:

        if isinstance(obj, basestring):  # group heading
            row_list.append([obj.upper()])

        else:  # individual command
            doc_before_empty_line = obj.__doc__.split('\n\n')[0]
            doc_lines = [s.strip() for s in doc_before_empty_line.split('\n')]
            for doc_line in doc_lines:
                if doc_line == '':
                    continue
                if obj.__name__ in ('ub', 'hkl'):
                    continue
                name, args, desc = _split_doc_line(doc_line)
                desc = desc.strip()
                args = args.strip()
                if desc and desc[-1] == '.':
                    desc = desc[:-1]
                
                row_list.append([name + (' ' if args else '') + args, desc])
    
    return row_list
    

def _split_doc_line(docLine):
    name, _, right = docLine.partition(' ')
    args, _, desc = right.partition('-- ')
    return name, args, desc


def compile_extra_motion_commands_for_help():
    
    _hwname = settings.hardware.name  # @UndefinedVariable
    _angles = ', '.join(settings.hardware.get_axes_names())  # @UndefinedVariable
    
    commands = []
        
    commands.append('Motion')
    commands.append(sim)
    commands.append(ExternalCommand(
        '%(_hwname)s -- show Eularian position' % vars()))
    commands.append(ExternalCommand(
        'pos %(_hwname)s [%(_angles)s]  -- move to Eularian position'
        '(None holds an axis still)' % vars()))
    commands.append(ExternalCommand(
        'sim %(_hwname)s [%(_angles)s] -- simulate move to Eulerian position'
        '%(_hwname)s' % vars()))
    
    commands.append(ExternalCommand(
        'hkl -- show hkl position'))
    commands.append(ExternalCommand(
        'pos hkl [h k l] -- move to hkl position'))
    commands.append(ExternalCommand(
        'pos {h | k | l} val -- move h, k or l to val'))
    commands.append(ExternalCommand(
        'sim hkl [h k l] -- simulate move to hkl position'))
    
#     if engine_name != 'vlieg':
#         pass
#         # TODO: remove sigtau command and 'Surface' string
    return commands