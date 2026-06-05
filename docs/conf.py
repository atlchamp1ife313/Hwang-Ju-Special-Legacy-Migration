"""
Sphinx Documentation Configuration for LGM-35A Sentinel Framework
Auto-generates technical API layouts from engine docstrings.
"""

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'LGM-35A Sentinel AaC Framework'
copyright = '2026, Hwang-Ju'
author = 'Hwang-Ju'
release = '1.0.0'

# Core extensions for parsing Google/NumPy style python docstrings
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Clear, readable documentation theme
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
