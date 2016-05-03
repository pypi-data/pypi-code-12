"""
---------------------------------- JUICY -----------------------------------

A command line tool to manage your app

To run, Magic already has a hook that you can directly use in the command line

Run:

    magic

It will show the list of actions available

To run an action:

    magic $action


By default it will use the DEV environment. On production, change the env

    env="production" magic $action


If you are using Propel, the example below will run the setup in the production
environment

    scripts:

      # Run before all
      before_all:
        -
          command: "$PYTHON_ENV magic.py setup"
          environment: env="production"

-----

Examples:

@cli.command()
def hello():
    ''' Hello Description '''
    print(":Hello")
    print("Hello From the Other Side!")

@cli.command()
@click.option("id")
def user(id):
    ''' This is the user's description '''
    print("User ID: %s" % id)


- The hello() can be called

    magic hello

- The user() can be called:

    magic user id 1

--------------------------------------------------------------------------------

"""

from flask_magic import MagicWand, get_env_config, abort
import flask_magic.utils as utils
from application import config, model
from flask_magic.plugins import user, publisher
from flask_magic.ext import mail
from flask_magic.cli import cli, click

# init Magic without registering the views
MagicWand(__name__, exclude_views=True)

# Load the config
conf = get_env_config(config)

# ------------------------------------------------------------------------------

def setup_db():
    """
    Setup models from model.py
    """
    model.db.create_all()

def setup_admin_user_publisher():
    """
    Setup Magic User and Publisher Admin
    :return:
    """

    # ==== Setup User Admin === #

    admin_email = conf.APPLICATION_ADMIN_EMAIL
    if not admin_email:
        print("ERROR: APPLICATION_ADMIN_EMAIL is empty")
        exit()

    password = utils.generate_random_string()
    if user.setup(model.User,
                  admin_email=admin_email,
                  password=password):

        if mail.validated:
            body = "Admin Password: %s" % password
            mail.send(to=admin_email, subject="Admin Password", body=body)

        print("---- Setup SUPER ADMIN User ----")
        print("- Admin Email: %s" % admin_email)
        print("- Admin Password: %s" % password)
        print("-" * 40)
        print("")

    # ==== Setup Publisher === #

    # admin user
    admin_user = model.User.User.get_by_email(admin_email)

    # Set default categories and post types
    post_categories = ["Uncategorized"]
    post_types = ["Page", "Blog", "Document", "Other"]

    if admin_user and admin_user.role.name.lower() == "superadmin":
        print("---- Setup PUBLISHER ----")
        if publisher.setup(model.Publisher,
                           admin_user_id=admin_user.id,
                           post_types=post_types,
                           post_categories=post_categories):
            print("Completed")
        print("-" * 40)
        print("")

# ------------------------------------------------------------------------------


@cli.command()
def setup():

    """ Setup """
    print("::Setup")
    setup_db()

    setup_admin_user_publisher()

    print("Done!")


# ------------------------------------------------------------------------------

#
if __name__ == "__main__":
    cli()







