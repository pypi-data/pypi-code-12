try:
    from flask import has_app_context
    from celery import Celery as BaseCelery

    class Celery(BaseCelery):
        app = None

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.patch_task()

            if 'application' in kwargs:
                self.init_app(kwargs['application'])

        def patch_task(self):
            base_task = self.Task
            _celery = self

            class ContextTask(base_task):
                abstract = True

                def __call__(self, *args, **kwargs):
                    if has_app_context():
                        return base_task.__call__(self, *args, **kwargs)

                    with _celery.app.app_context():
                        return base_task.__call__(self, *args, **kwargs)

            setattr(self, 'Task', ContextTask)

        def init_app(self, app):
            self.app = app
            self.config_from_object(app.config)
except:
    class Celery:
        pass
