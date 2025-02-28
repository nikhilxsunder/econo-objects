import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'econo-objects'
author = 'Nikhil Sunder'
release = '0.4'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'