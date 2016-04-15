'''
    Utilities for parsing hyperparameter space configurations
'''

from hyperopt import hp

def parse_config(obj, obj_id='obj'):
    if isinstance(obj, dict):
        return parse_dict(obj, obj_id)

    if isinstance(obj, list):
        return parse_list(obj, obj_id)

    return obj

def parse_dict(obj, obj_id):
    hp_command = get_command(obj, '$')

    if hp_command is not None:
        return getattr(hp, hp_command)(
            obj_id,
            **parse_config(obj['$' + hp_command], obj_id + '.$' + hp_command)
        )

    at_command = get_command(obj, '@')

    if at_command is not None:

        return apply_at_command(
            obj_id,
            at_command,
            obj['@' + at_command]
        )

    return {
        key: parse_config(
            value,
            obj_id + '.' + str(key)
        )
        for (key, value) in obj.items()
    }

def parse_list(obj, obj_id):
    return [
        parse_config(
            item,
            obj_id + '.' + str(idx)
        )
        for (idx, item) in enumerate(obj)
    ]

def apply_at_command(obj_id, cmd, cmd_body):

    if cmd == 'repeat':
        options = [

            [
                parse_config(
                    cmd_body['body'],
                    obj_id + '.x' + str(num_times)
                )
            ] * num_times

            for num_times in range(
                cmd_body['times'][0],
                cmd_body['times'][1] + 1
            )
        ]
        return hp.choice(obj_id + '.@repeat', options)

    if cmd == 'merge':
        return sum(
           parse_config(cmd_body, obj_id + '.@merge'), []
        )

def get_command(obj, prefix='$'):
    '''
        { "$choice" : [] } => "choice"
    '''

    commands = [
        key for (key, val) in obj.items() if key.startswith(prefix)
    ]

    if not commands:
        return None

    return str(commands[0][1:])
