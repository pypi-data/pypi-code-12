from django_autoshard.models import ShardedModel, ShardRelatedModel


class ShardRouter:
    def db_for_write(self, model, **hints):
        if not issubclass(model, ShardedModel) and not issubclass(model, ShardRelatedModel):
            return 'default'
