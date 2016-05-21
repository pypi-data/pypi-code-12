"""
::Magic::

https://github.com/mardix/flask-magic

app_{project_name}.py

This is the entry point of the application.

--------------------------------------------------------------------------------

** To serve the local development app

> magic serve {project_name}

#---------

** To deploy with Propel ( https://github.com/mardix/propel )

> propel -w

#---------

** To deploy with Gunicorn

> gunicorn app_{project_name}:app

"""

from flask_magic import MagicWand

# Import the project's views
import application.{project_name}.views

# 'app' variable name is required if you intend to use 'Magic' the cli tool
app = MagicWand(__name__, project="{project_name}")

