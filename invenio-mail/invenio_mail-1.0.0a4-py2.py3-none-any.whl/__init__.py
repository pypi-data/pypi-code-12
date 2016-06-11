# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio mail module.

The Invenio-Mail module is a tiny wrapper around Flask-Mail that provides
printing of emails to standard output when the configuration variable
``MAIL_SUPPRESS_SEND`` is true.

Invenio-Mail also takes care of initializing Flask-Mail if not already
initialized.


First, initialize the extension:

>>> from flask import Flask
>>> from invenio_mail import InvenioMail
>>> app = Flask('myapp')
>>> app.config.update(MAIL_SUPPRESS_SEND=True)
>>> InvenioMail(app)
<invenio_mail.ext.InvenioMail ...>


Next, let's send an email:

>>> from flask_mail import Message
>>> msg = Message("Hello", sender='from@example.org',
...    recipients=["to@example.com"], body='Hello, World!')
>>> with app.app_context():
...     app.extensions['mail'].send(msg)
Content-Type: text/plain; charset="utf-8"...


Writing extensions
------------------
By default you should just depend on Flask-Mail if you are writing an
extension which needs email sending functionality:

.. code-block:: python

   from flask import current_app
   from flask_mail import Message

   def mystuff():
       msg = Message("Hello", sender='from@example.org',
                     recipients=["to@example.com"], body='Hello, World!')
       current_app.extensions['mail'].send(msg)


Remember to add Flask-Mail to your ``setup.py`` file as well:

.. code-block:: python

   setup(
       # ...
       install_requires = ['Flask-Mail>=0.9.1',]
       #...
    )
"""

from __future__ import absolute_import, print_function

from .ext import InvenioMail
from .version import __version__

__all__ = ('__version__', 'InvenioMail')
