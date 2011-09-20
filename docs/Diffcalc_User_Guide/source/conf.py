# -*- coding: utf-8 -*-

# get standard configurations settings
import os.path
conf_common_path = os.path.abspath('../../../../builders.dawn/documentation/source/conf_common.py')
if not os.path.isfile(conf_common_path):
    raise Exception, 'File %s not found' % (conf_common_path,)
execfile(conf_common_path)

# General information about the project.
project = u'Diffcalc User Guide'
copyright = copyright_diamond

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.0'
# The full version, including alpha/beta/rc tags.
release = '1.0'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = html_theme_options_gda

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = None

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('contents', 'Diffcalc_User_Guide.tex', u'Diffcalc User Guide',
   _author_diamond, 'manual'),
]
