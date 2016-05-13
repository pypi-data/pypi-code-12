import os
import json

def parse(env_name):
    json_data = os.environ.get(env_name, None)
    if json_data is None:
        return {}
    return json.loads(json_data)

