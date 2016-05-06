import os
import subprocess
import json
import underaid


def run_playbook(playbook, profile_name=None, extra_vars={}):

    if profile_name:
        underaid.set_aws_environment(profile_name)

    subprocess.check_call(
        [
            "ansible-playbook",
            "-v", playbook,
            "-i", "127.0.0.1,",
            "--extra-vars", json.dumps(extra_vars)
        ]
    )
