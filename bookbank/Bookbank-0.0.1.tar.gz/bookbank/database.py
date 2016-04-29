
from bookbank.core import app
import flask.ext.sqlalchemy

# db and config
db = flask.ext.sqlalchemy.SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'