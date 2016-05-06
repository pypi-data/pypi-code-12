import os

def set_aws_environment(profile_name=None, env=None):
    if not env:
        env = os.environ

    if profile_name:
        env.pop('AWS_ACCESS_KEY_ID', None)
        env.pop('AWS_SECRET_ACCESS_KEY', None)
        env.pop('AWS_DEFAULT_PROFILE', None)
        env['AWS_PROFILE'] = profile_name

    return env