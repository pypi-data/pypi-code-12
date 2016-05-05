import github
import getpass
import json
import keyring
import subprocess
import requests

GITHUB_NEW_TOKEN_URI = 'https://github.com/settings/tokens/new'
fake_username = 'love tools'


def get_auth_token(token):

    if token is not None:
        return token

    token = keyring.get_password('github', fake_username)
    if token is not None:
        return token

    print("Please enter your github username and password. These are not "
           "stored, only used to get an oAuth token. You can revoke this at "
           "any time on Github.")
    user = input("Username: ")
    pw = getpass.getpass("Password: ")

    auth_request = {
      "scopes": [
        "public_repo",
      ],
      "note": "Love tools",
      "note_url": "https://github.com/Carreau/love",
    }
    response = requests.post('https://api.github.com/authorizations',
                            auth=(user, pw), data=json.dumps(auth_request))
    if response.status_code == 401 and response.headers.get('X-GitHub-OTP') == 'required; sms':
        print("Your login API resquest a SMS one time password")
        sms_pw = getpass.getpass("SMS password: ")
        response = requests.post('https://api.github.com/authorizations',
                            auth=(user, pw), 
                            data=json.dumps(auth_request),
                            headers={'X-GitHub-OTP':sms_pw})
    response.raise_for_status()
    token = json.loads(response.text)['token']
    keyring.set_password('github', fake_username, token)
    return token



def setup_github_credentials(log):
    token = get_auth_token(None)
    gh = github.Github(token)
    user = gh.get_user()
    log.info('Logged in on GitHub as %s ', user.name)
    return token, user



def setup_github_repository(user, proposal, log):
    from github import UnknownObjectException 
    try:
        repo = user.get_repo(proposal)
        log.info('It appears like %s repository already exists, using it as remote', repr(proposal))
    except UnknownObjectException:
        repo = user.create_repo(proposal)

    ssh_url = repo.ssh_url
    slug = repo.full_name
    log.info('Working with repository %s', slug)


    # Clone github repo locally, over SSH an chdir into it

    log.info("Cloning github repository locally")
    log.info("Calling subprocess : %s", ' '.join(['git', 'clone' , ssh_url]))
    subprocess.call(['git', 'clone' , ssh_url])
    return slug
