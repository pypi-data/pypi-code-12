'''
Copyright 2016 define().

This file is part of dsgnutils.

dsgnutils is free software: you can redistribute it and/or modify it under the
terms of the Lesser GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

dsgnutils is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the Lesser GNU General Public License for more
details.

You should have received a copy of the Lesser GNU General Public License along
with dsgnutils.  If not, see <http://www.gnu.org/licenses/>.
'''

#=======MAIN IMPORT===========================================================
import flask

#=======UBIQUITOUS============================================================
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

#=======EXTENSIONS============================================================
import flask_classy
import flask_login
from flask_login import current_user
import flask_wtf
import wtforms
