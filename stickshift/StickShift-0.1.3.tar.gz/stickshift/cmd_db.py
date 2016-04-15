import click

try:
    from stickshift.shell import pass_context
    from stickshift.cli_strings import CLIStrings
except ImportError:
    from shell import pass_context
    from cli_strings import CLIStrings


DB_OPERATIONS = [
    "provision",
    "deprovision",
    "version",
    "procedures",
    "tables",
    "migrate",
    "reset",
    "upgrade",
    "downgrade",
]


@click.command('db', short_help='Run specific commands against a specific database')
@click.argument('operation', required=True, type=click.Choice(DB_OPERATIONS), metavar='<operation>')
@click.argument('environment', required=True, type=click.STRING, metavar='<environment>')
@pass_context
def cli(ctx, operation, environment):

    if ctx.repository().is_repository_setup():
        database_manager = ctx.database_manager(environment=environment)
        if operation == "provision":
            provision_database(ctx=ctx, database_manager=database_manager)
        elif operation == "deprovision":
            deprovision_database(ctx=ctx, database_manager=database_manager)
        elif operation == "version":
            print_database_version(ctx=ctx, database_manager=database_manager)
        elif operation == "procedures":
            print_list_items_with_title(title="PROCEDURES", list_items=database_manager.list_procedures())
        elif operation == "tables":
            print_list_items_with_title(title="TABLES", list_items=database_manager.list_tables())
        elif operation == "upgrade":
            database_manager.upgrade()
        elif operation == "downgrade":
            database_manager.downgrade()
        elif operation == "migrate":
            database_manager.migrate()
        elif operation == "reset":
            database_manager.reset()
    else:
        ctx.log(CLIStrings.DB_MIGRATION_REPOSITORY_MUST_BE_SETUP)


def provision_database(ctx, database_manager):
    if database_manager.provision_database():
        ctx.log(CLIStrings.DB_DATABASE_PROVISIONED_SUCCESSFULLY)
    else:
        ctx.log(CLIStrings.DB_DATABASE_IS_ALREADY_PROVISIONED)


def deprovision_database(ctx, database_manager):
    if database_manager.deprovision_database():
        ctx.log(CLIStrings.DB_DATABASE_DEPROVISIONED_SUCCESSFULLY)
    else:
        ctx.log(CLIStrings.DB_DATABASE_IS_NOT_PROVISIONED)


def print_database_version(ctx, database_manager):
    version = database_manager.current_database_migration_version()
    if version is not None:
        ctx.log("{0}: {1}".format(CLIStrings.DB_DATABASE_VERSION, version))
    else:
        ctx.log(CLIStrings.DB_DATABASE_NOT_MIGRATED_YET)


def print_list_items_with_title(title, list_items):
    print("\n{0}".format(title))
    print("--------")
    for item in list_items:
        print(item)
    print("--------")
