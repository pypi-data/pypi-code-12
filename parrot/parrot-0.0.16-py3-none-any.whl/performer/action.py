"""
Действие - метод Performer, который принимает аргументом только самого себя.
Например:
ConsolePerformer.clear(self)
"""


def register_action(**kwargs):
    """
    Помечает метод класса Performer как действие

    Примеры:
    @register_action(label='Обновить', private=True)
    def update_items(self):
        pass

    @register_action
    def parse_items(self):
        pass

    :param kwargs: дополнительные атрибуты метода
                   (например, можно передать label)
    :return:
    """
    def decorator(method):
        kwargs['is_action'] = True
        for name, value in kwargs.items():
            setattr(method, name, value)
        return method
    return decorator


def unregister_action(*pargs):
    def decorator(method):
        for name in pargs + ('is_action', ):
            if hasattr(method, name):
                delattr(method, name)
        return method
    return decorator


def is_action(performer_attr):
    return hasattr(performer_attr, 'is_action') and performer_attr.is_action


def get_actions(performer_cls):
    """
    :param performer_cls:
    :return: список методов класса, которые являются действиями
    """
    actions = []
    for attr_name in dir(performer_cls):
        attr = getattr(performer_cls, attr_name)
        if is_action(attr):
            actions.append(attr)
    return actions
