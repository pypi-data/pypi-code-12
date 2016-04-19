import textwrap
from score.cli.setup import append_to_bashrc, append_to_zshrc


def update_prompt():

    def test_exists(rcfile, content):
        return 'VIRTUAL_ENV_NAME' in content

    def gen_bash_prompt():
        return textwrap.dedent(r'''
            # This next line updates your shell prompt to include the name of
            # the current project.
            if [ -n "$VIRTUAL_ENV_NAME" ]; then
                export PS1="\[[0;33m\](${VIRTUAL_ENV_NAME})\[[0m\]$PS1"
            elif [ -n "$VIRTUAL_ENV" ]; then
                export PS1="\[[0;33m\](${VIRTUAL_ENV##*/})\[[0m\]$PS1"
            fi
        ''').strip()

    def gen_zsh_prompt():
        return textwrap.dedent(r'''
            # This next line updates your shell prompt to include the name of
            # the current project.
            if [ -n "$VIRTUAL_ENV_NAME" ]; then
                export PROMPT="%{[0;33m%}(${VIRTUAL_ENV_NAME})%{[0m%}$PROMPT"
            elif [ -n "$VIRTUAL_ENV" ]; then
                export PROMPT="%{[0;33m%}(${VIRTUAL_ENV##*/})%{[0m%}$PROMPT"
            fi
        ''').strip()

    append_to_bashrc('projects', test_exists, gen_bash_prompt)
    append_to_zshrc('projects', test_exists, gen_zsh_prompt)
