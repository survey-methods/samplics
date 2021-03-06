# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

import samplics


sys.path.insert(0, os.path.abspath("../.."))


# -- Project information -----------------------------------------------------
project = "samplics"
copyright = "2019-2020, samplics"
author = "Mamadou S. Diallo"

# The master toctree document.
master_doc = "index"

version = samplics.__version__
release = version


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "nbsphinx",
    "recommonmark",
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

### Mardown parser
source_suffix = [
    ".rst",
    ".md",
    ".ipynb",
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "**.ipynb_checkpoints", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

import sphinx_bootstrap_theme


html_theme = "bootstrap"
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#

html_sidebars = {"sidebar": ["localtoc.html", "sourcelink.html", "searchbox.html"]}
# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = project + "docs"
html_show_sourcelink = False

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "samplics.tex", "samplics Documentation", "Mamadou S Diallo", "manual",)
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "samplics", "samplics Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "samplics",
        "samplics Documentation",
        author,
        "samplics",
        "One line description of project.",
        "Miscellaneous",
    )
]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]

# -- Extension configuration -------------------------------------------------
autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": True,
}
# (Optional) Logo. Should be small enough to fit the navbar (ideally 24x24).
# Path should be relative to the ``_static`` files directory.
# html_theme_options = {
#     "logo": "samplics_logo.png",
#     "logo_name": True,
#     "description": "Sample Analytics in Python",
#     "github_user": "survey-methods",
#     "github_repo": "samplics",
#     "github_banner": True,
#     "github_button": False,
#     "travis_button": False,
#     "codecov_button": False,
#     "analytics_id": False,
#     "font_family": "'Roboto', Georgia, sans",
#     "head_font_family": "'Roboto', Georgia, serif",
#     "code_font_family": "'Roboto Mono', 'Consolas', monospace",
#     "anchor": "#CCFFCC",
#     # "footnote_bg": "#CCE6FF",
#     # "pre_bg": "#433e56",
#     "page_width": "1024px",  # default is 940px
# }

# Theme options are theme-specific and customize the look and feel of a
# theme further.
# html_logo = "_static/samplics_logo3.png"
html_theme_options = {
    "navbar_title": "Sample Analytics",
    "navbar_links": [
        ("Getting started", "gettingstarted"),
        ("Tutorial", "tutorial/index"),
        ("Github", "https://github.com/survey-methods/samplics", True),
    ],
    "navbar_sidebarrel": False,
    "navbar_site_name": "Documentation",
    "navbar_pagenav": False,
    "navbar_pagenav_name": "Pages",
    "globaltoc_depth": 3,
    "globaltoc_includehidden": "true",
    "navbar_class": "navbar",
    "navbar_fixed_top": "true",
    "source_link_position": "nav",
    "bootswatch_theme": "paper",
    "bootstrap_version": "3",
}

# To add customized css
def setup(app):
    app.add_stylesheet("_source/samplics_style.css")
    app.add_stylesheet("samplics_style.css")
