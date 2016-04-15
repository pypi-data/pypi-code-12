# -*- coding: utf-8 -*-
#
# Setuptools documentation build configuration file, created by
# sphinx-quickstart on Fri Jul 17 14:22:37 2009.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# Allow Sphinx to find the setup command that is imported below, as referenced above.
import sys, os
sys.path.append(os.path.abspath('..'))

import setup as setup_script

# -- General configuration -----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['rst.linker']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.txt'

# The encoding of source files.
#source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Setuptools'
copyright = '2009-2014, The fellowship of the packaging'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = setup_script.setup_params['version']
# The full version, including alpha/beta/rc tags.
release = setup_script.setup_params['version']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = []

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
html_theme = 'nature'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ['_theme']

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "Setuptools documentation"

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = "Setuptools"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
html_sidebars = {'index': 'indexsidebar.html'}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
html_use_modindex = False

# If false, no index is generated.
html_use_index = False

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'Setuptoolsdoc'


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
#latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'Setuptools.tex', 'Setuptools Documentation',
   'The fellowship of the packaging', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True

link_files = {
	'CHANGES.rst': dict(
		using=dict(
			BB='https://bitbucket.org',
			GH='https://github.com',
		),
		replace=[
			dict(
				pattern=r"(Issue )?#(?P<issue>\d+)",
				url='{GH}/pypa/setuptools/issues/{issue}',
			),
			dict(
				pattern=r"BB Pull Request ?#(?P<bb_pull_request>\d+)",
				url='{BB}/pypa/setuptools/pull-request/{bb_pull_request}',
			),
			dict(
				pattern=r"Distribute #(?P<distribute>\d+)",
				url='{BB}/tarek/distribute/issue/{distribute}',
			),
			dict(
				pattern=r"Buildout #(?P<buildout>\d+)",
				url='{GH}/buildout/buildout/issues/{buildout}',
			),
			dict(
				pattern=r"Old Setuptools #(?P<old_setuptools>\d+)",
				url='http://bugs.python.org/setuptools/issue{old_setuptools}',
			),
			dict(
				pattern=r"Jython #(?P<jython>\d+)",
				url='http://bugs.jython.org/issue{jython}',
			),
			dict(
				pattern=r"Python #(?P<python>\d+)",
				url='http://bugs.python.org/issue{python}',
			),
			dict(
				pattern=r"Interop #(?P<interop>\d+)",
				url='{GH}/pypa/interoperability-peps/issues/{interop}',
			),
			dict(
				pattern=r"Pip #(?P<pip>\d+)",
				url='{GH}/pypa/pip/issues/{pip}',
			),
			dict(
				pattern=r"Packaging #(?P<packaging>\d+)",
				url='{GH}/pypa/packaging/issues/{packaging}',
			),
			dict(
				pattern=r"[Pp]ackaging (?P<packaging_ver>\d+(\.\d+)+)",
				url='{GH}/pypa/packaging/blob/{packaging_ver}/CHANGELOG.rst',
			),
			dict(
				pattern=r"PEP[- ](?P<pep_number>\d+)",
				url='https://www.python.org/dev/peps/pep-{pep_number:0>4}/',
			),
			dict(
				pattern=r"^(?m)((?P<scm_version>v?\d+(\.\d+){1,2}))\n[-=]+\n",
				with_scm="{text}\n{rev[timestamp]:%d %b %Y}\n",
			),
		],
	),
}
