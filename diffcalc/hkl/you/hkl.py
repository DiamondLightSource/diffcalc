###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

from __future__ import absolute_import

from diffcalc.hkl.common import getNameFromScannableOrString
from diffcalc.util import command
from diffcalc.hkl.you.calc import YouHklCalculator
from diffcalc import settings



import diffcalc.ub.ub
from diffcalc.hkl.you.constraints import YouConstraintManager

__all__ = ['allhkl', 'con', 'uncon', 'hklcalc', 'constraint_manager']


_fixed_constraints = settings.geometry.fixed_constraints  # @UndefinedVariable

constraint_manager = YouConstraintManager(_fixed_constraints)

hklcalc = YouHklCalculator(diffcalc.ub.ub.ubcalc, constraint_manager)


def __str__(self):
    return hklcalc.__str__()

@command
def con(*args):
    """
    con -- list available constraints and values
    con <name> {val} -- constrains and optionally sets one constraint
    con <name> {val} <name> {val} <name> {val} -- clears and then fully constrains

    Select three constraints using 'con' and 'uncon'. Choose up to one
    from each of the sample and detector columns and up to three from
    the sample column.

    Not all constraint combinations are currently available:

        1 x samp:              all

        2 x samp and 1 x ref:  chi & phi
                               chi & eta
                               chi & mu
                               mu & eta

        2 x samp and 1 x det:  chi & phi
                               mu & eta
                               mu & phi
                               eta & phi
                               bisect & mu
                               bisect & eta
                               bisect & omega

        3 x samp:              eta, chi & phi

    See also 'uncon'
    """
    args = list(args)
    msg = _handle_con(args)
    if (hklcalc.constraints.is_fully_constrained() and 
        not hklcalc.constraints.is_current_mode_implemented()):
        msg += ("\n\nWARNING: The selected constraint combination "
            "is not implemented.\n\nType 'help con' to see implemented combinations")
    if msg:
        print msg

    diffcalc.ub.ub.ubcalc.save()


def _handle_con(args):
    if not args:
        return hklcalc.constraints.__str__()
    
    if len(args) > 6:
        raise TypeError("Unexpected args: " + str(args))
    
    cons_value_pairs = []
    while args:
        scn_or_str = args.pop(0)
        ext_name = getNameFromScannableOrString(scn_or_str)
        if args and isinstance(args[0], (int, long, float)):
            ext_value = args.pop(0)
        else:
            try:
                ext_value = settings.hardware.get_position_by_name(ext_name)
            except ValueError:
                ext_value = None
        cons_name, cons_value = settings.geometry.map_to_internal_position(ext_name, ext_value)
        cons_value_pairs.append((cons_name, cons_value))
    
    if len(cons_value_pairs) == 1:
        pass
    elif len(cons_value_pairs) == 3:
        hklcalc.constraints.clear_constraints()
    else:
        raise TypeError("Either one or three constraints must be specified")
    for name, value in cons_value_pairs:
        hklcalc.constraints.constrain(name)
        if value is not None:
            hklcalc.constraints.set_constraint(name, value)
    return '\n'.join(hklcalc.constraints.report_constraints_lines())


@command
def uncon(scn_or_string):
    """uncon <name> -- remove constraint

    See also 'con'
    """
    ext_name = getNameFromScannableOrString(scn_or_string)
    cons_name = settings.geometry.map_to_internal_name(ext_name)
    hklcalc.constraints.unconstrain(cons_name)
    print '\n'.join(hklcalc.constraints.report_constraints_lines())

    diffcalc.ub.ub.ubcalc.save()


@command 
def allhkl(hkl, wavelength=None):
    """allhkl [h k l] -- print all hkl solutions ignoring limits

    """
    _hardware = settings.hardware
    _geometry = settings.geometry
    if wavelength is None:
        wavelength = _hardware.get_wavelength()
    h, k, l = hkl
    pos_virtual_angles_pairs = hklcalc.hkl_to_all_angles(
                                    h, k, l, wavelength)
    cells = []
    msg_lines = ['_' * 300]
    idx_err = 0
    # virtual_angle_names = list(pos_virtual_angles_pairs[0][1].keys())
    # virtual_angle_names.sort()
    if settings.include_reference:
        virtual_angle_names = ['qaz', 'psi', 'naz', 'tau', 'theta', 'ttheta', 'alpha', 'beta', 'betain', 'betaout']
    else:
        virtual_angle_names = ['qaz', 'theta', 'ttheta', 'betain', 'betaout']
    header_cell_names = [''] + list(_hardware.get_axes_names()) + [' '] + virtual_angle_names
    cells.append(['%9s' % s for s in header_cell_names])

    for pos, virtual_angles in pos_virtual_angles_pairs:
        row_cells = []

        angle_tuple = _geometry.internal_position_to_physical_angles(pos)
        angle_tuple = _hardware.cut_angles(angle_tuple)
        try:
            err_msg = _hardware.diffhw.checkPositionValid(angle_tuple)
        except Exception:
            err_msg = "Cannot read limit violation message."
        if err_msg:
            idx_err += 1
            idx_str =  str(idx_err) + '.'
            row_cells.append(idx_str)
            msg_lines.append(idx_str + '  ' + err_msg)
        else:
            row_cells.append('*')
        for val in angle_tuple:
            row_cells.append('%9.4f' % val)
        row_cells.append('|')
        for name in virtual_angle_names:
            row_cells.append('%9.4f' %  virtual_angles[name])
        cells.append(row_cells)

    column_widths = []
    for col in range(len(cells[0])):
        widths = []
        for row in range(len(cells)):
            cell = cells[row][col]
            width = len(cell.strip())
            widths.append(width)
        column_widths.append(max(widths))
    total_width = sum(column_widths) + 2 * (len(column_widths) - 1)

    lines = []
    for row_cells in cells:
        trimmed_row_cells = []
        for cell, width in zip(row_cells, column_widths):
            trimmed_cell = cell.strip().rjust(width)
            trimmed_row_cells.append(trimmed_cell)
        lines.append('  '.join(trimmed_row_cells))
    lines.append('')
    for msg in msg_lines:
        lines.append(msg[:total_width])
    print '\n'.join(lines)


commands_for_help = ['Constraints',
                     con,
                     uncon,
                     'Hkl',
                     allhkl
                     ]
