from django.db import connections
from django.db.models.signals import post_init
from django.db.migrations.state import AppConfigStub

def meta_equal(m1, m2):
    return (m1.app_config.name == m2.app_config.name and
            m1.model_name == m2.model_name)

# TODO: Handle inheritance
def is_model_instance(instance, model):
    # Don't trigger on half-migrated objects
    if isinstance(instance._meta.app_config, AppConfigStub):
        return False

    return (isinstance(instance, model) or meta_equal(instance._meta,
                                                      model._meta))


class MigrationHandler(object):
    # TODO: Figure out how to handle multiple dbs
    def __init__(self):
        self.migration_handler_plans = {}
        post_init.connect(self.migration_handler_pre_post)

    def migration_handler_pre_post(self, sender, **kwargs):
        from django.db.migrations.recorder import MigrationRecorder
        from django.db.migrations.executor import MigrationExecutor

        self.migration_class = MigrationRecorder.Migration
        self.executors = {}
        self.plans = {}
        self.sender_plans = {}

        for db in connections:
            connection = connections[db]
            executor = MigrationExecutor(connection)
            self.executors[db] = executor
            targets = executor.loader.graph.leaf_nodes()
            self.plans[db] = executor.migration_plan(targets)

        post_init.connect(self.migration_handler_post)
        post_init.disconnect(self.migration_handler_pre_post)

        self.migration_handler_post(sender, **kwargs)

    # TODO: Multiple migration updaters at once, this is problematic because if
    # you depend on the update migration, then getting the old app expects the
    # old fields (not yet removed) to be there.
    # TODO: Provide a means of blanket or selective clearing of the plan cache
    def migration_handler_post(self, sender, instance, **kwargs):
        if sender == self.migration_class:
            return

        plan = self.migration_handler_plans.get(sender)

        if plan is not None:
            for handler, apps in plan:
                handler(instance, apps)
        else:
            plan = []
            for migration, backwards in self.plans['default']:
                model_handlers = getattr(migration, 'model_handlers', [])
                for model, handler in model_handlers:
                    if is_model_instance(instance, model):
                        executor = self.executors['default']
                        migration_state = [(migration.app_label,
                                            migration.name)]
                        apps = executor.loader.project_state(migration_state).apps
                        handler(instance, apps)
                        plan.append((handler, apps))

            self.migration_handler_plans[sender] = plan

handler = MigrationHandler()
