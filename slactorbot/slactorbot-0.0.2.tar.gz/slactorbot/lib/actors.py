from thespian.actors import *


def create_actor(actor_system, plugin_class):
    return actor_system.createActor(plugin_class)


def delete_actor(actor_system, actor):
    return actor_system.ask(actor, ActorExitRequest())