"""
Magic

model.py

You may place your models here.
"""

from active_alchemy import ActiveAlchemy
import config
from flask_magic import init_app, get_env_config
from flask_magic.plugins import user, publisher

# The config
conf = get_env_config(config)

# Connect the DB
db = ActiveAlchemy(conf.SQL_URI)

# Attach the ActiveAlchemy
init_app(db.init_app)

# ------------------------------------------------------------------------------

# User Model
User = user.model(db)

# Post Model
Publisher = publisher.model(User.User)

"""
# A Table schema example. The table name will automatically be 'my_note'
# To change the table, set the property: __tablename__
class MyNote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.User.id))
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    user = db.relationship(User.User, backref="notes")
"""
