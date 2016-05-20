# flake8: noqa

# Generic tasks
from .basics import dump, glob, log, noop, sync, walk, write
from .io import external_command
from .filters import exclude, match
from .paths import directory, relative_to, rename_replace, strip_dirs
from .text import concat, contents_replace, footer, header, regex
from .templating import jinja2

# Specific tasks
from .angular import ng_annotate, ng_min, ng_template_cache
from .css import autoprefixer, cleancss, lessc
from .gzip import gzip
from .html import minify_html
from .javascript import coffee, traceur, uglify
from .markdown import markdown
from .png import optipng, pngquant
from .textile import textile
from .web import cachebust
