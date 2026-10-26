# Configuration file for the Sphinx documentation builder.
#
# For the full list of options see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = "CI course"
copyright = "2026, Oxford Research Software Engineering"
author = "Oxford Research Software Engineering"

# -- General configuration ---------------------------------------------------

# autodoc pulls the docstrings out of the installed package, and napoleon
# teaches it to read the numpydoc style those docstrings are written in.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "alabaster"
