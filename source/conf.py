# -- Project information -----------------------------------------------------
project = 'Client Notes'
author = 'Cody Vantienen'
release = '1.0'
master_doc = 'client_notes'
# -- General configuration ---------------------------------------------------
extensions = [
    'recommonmark',  # Enable recommonmark for markdown support
    'sphinx_rtd_theme',  # Optional, for Read the Docs theme
]

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Optional theme for better styling
html_static_path = ['_static']

# -- Options for source file processing ------------------------------------
source_suffix = {
    '.rst': 'restructuredtext',  # Default
    '.md': 'markdown',  # Enable Markdown support
}
