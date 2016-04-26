# -*- coding: utf-8 -*-
#
# mercurial_bitbucketize: create and update bitbucket repos from cmdline
#
# Copyright (c) 2015 Marcin Kasperski <Marcin.Kasperski@mekk.waw.pl>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# See README.txt for more details.

"""Create and administer BitBucket repositories without using web interface.

See README.txt (web copy: https://bitbucket.org/Mekk/mercurial-bitbucketize )
for details.
"""

# pylint: disable=invalid-name,star-args,broad-except,too-many-arguments,line-too-long

from mercurial import commands, util
from mercurial.i18n import _

import re
import os
import sys
import textwrap
import pprint


def import_meu():
    """Importing mercurial_extension_utils so it can be found also outside
    Python PATH (support for TortoiseHG/Win and similar setups)"""
    try:
        import mercurial_extension_utils
    except ImportError:
        my_dir = os.path.dirname(__file__)
        sys.path.extend([
            # In the same dir (manual or site-packages after pip)
            my_dir,
            # Developer clone
            os.path.join(os.path.dirname(my_dir), "extension_utils"),
            # Side clone
            os.path.join(os.path.dirname(my_dir), "mercurial-extension_utils"),
        ])
        try:
            import mercurial_extension_utils
        except ImportError:
            raise util.Abort(_("""Can not import mercurial_extension_utils.
Please install this module in Python path.
See Installation chapter in https://bitbucket.org/Mekk/mercurial-dynamic_username/ for details
(and for info about TortoiseHG on Windows, or other bundled Python)."""))
    return mercurial_extension_utils

meu = import_meu()


def import_pybitbucket(submodule):
    """demandimport-resistant import of pybitbucket.bitbucket
    Returns imported module"""
    module_name = 'pybitbucket.' + submodule
    return meu.direct_import(module_name, [
        'ssl', 'urllib3'])


# Disabling notorious ssl warnings which require upgrade to python 2.7.9,
# and are often not possible for the user in charge. As Mercurial itself
# is less picky, we may shut up too.
# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
# https://urllib3.readthedocs.org/en/latest/security.html#snimissingwarning
if sys.version_info < (2, 7, 9):
    try:
        import urllib3
        urllib3.disable_warnings()
    except:
        pass
 

############################################################
# BitBucket-API related utility functions
############################################################

CONFIG_SECTION = 'bitbucketize'

# Regexp for bitbucket paths. We allow the following forms:
#    mercurial-bitbucketize
#    Mekk/mercurial-bitbucketize
#    bitbucket.org/Mekk/mercurial-bitbucketize
#    https://bitbucket.org/Mekk/mercurial-bitbucketize
# and a few similar variations
re_path = re.compile(r'''
^
    # http prefix and host
    (?:
        (?: https?:// )?
        (?:www\.)? bitbucket\.org /
    )?
    # Username
    (?:
        (?P<user> [^/]+ )  /
    )?
    # name
    (?P<name> [^/]+ )
$
''', re.VERBOSE)


def calculate_bb_name(ui, repo, name):
    """Calculates BitBucket username and repository name,
    according to configuration, current repo and params.

    Returns USER, NAME, ALIAS"""
    user = ui.config(CONFIG_SECTION, 'user')
    if not user:
        raise util.Abort(
            _('BitBucket username not set. '
              + 'Please, set user option in [bitbucketize] section'))

    alias = None
    if not name:
        # User did not specify bitbucket name on the command line
        if not repo:
            raise util.Abort(_("""BitBucket path not specified
(it is required when command is executed outside any repository"""))
        alias = ui.config(CONFIG_SECTION, 'path_alias')
        if not alias:
            raise util.Abort(_("""BitBucket path not specified
(specify it or configure path_alias in [bitbucketize] section"""))
        # name = ui.expandpath(alias)  # No, we don't want default or alias
        name = ui.config('paths', alias)
        if not name:
            raise util.Abort(_("""Alias %s can not be resolved
(either specify BitBucket path as parameter, or define %s path)""") % (
                alias, alias))

    match = re_path.search(name)
    if not match:
        raise util.Abort(_("""Invalid BitBucket path: %(name)s
Expected one of the following:
    https://bitbucket.org/%(user)s/repo-name
    bitbucket.org/%(user)s/repo-name
    %(user)s/repo-name
    repo-name
""") % {'name': name, 'user': user})

    match_user, match_name = match.group('user'), match.group('name')
    if match_user:
        if match_user != user:
            raise util.Abort(_("""Username inconsistency.
You configured your Bitbucket username (user in [bitbucketize]) as %s,
but given path %s belongs to %s""") % (user, name, match_user))

    return user, match_name, alias


def bb_connect(ui, user, repo_name):
    """Setup Bb connection and return client object"""

    bitbucket = import_pybitbucket('bitbucket')
    auth = import_pybitbucket('auth')
    from mercurial.url import passwordmgr

    pwmgr = passwordmgr(ui)
    # This should utilize mercurial_keyring, if present
    http_user, http_pwd = pwmgr.find_user_password(
        "BitBucket.org",
        "https://%(user)s@bitbucket.org/%(user)s/%(name)s"
        % {'user': user, 'name': repo_name})

    email = ''
    return bitbucket.Client(
        auth.BasicAuthenticator(http_user, http_pwd, email)
    )


def bb_load_details(ui, bb_client, bb_user, bb_name):
    """Load and returns details of given repo.
    If it is not found, or can't be loaded, prints appropriate
    warnings and returns None"""
    BitbucketRepository = import_pybitbucket('repository').Repository
    try:
        bb_repo = BitbucketRepository.find_repository_by_name_and_owner(
            owner=bb_user, repository_name=bb_name, client=bb_client)
        if isinstance(bb_repo, type({})):
            # Raw dictionary returned. pybitbucket so far works this way,
            # I am not sure why but let's fix it up
            data = bb_repo
            bb_repo = BitbucketRepository(data=data, client=bb_client)
        return bb_repo
    except Exception as e:
        e_tn = type(e).__name__
        if (e_tn == 'HTTPError'
            and hasattr(e, 'response')
            and hasattr(e.response, 'status_code')
            and e.response.status_code == 404):
            ui.warn(_("\nRepository %s/%s does not exist on BitBucket\n") % (
                bb_user, bb_name))
        else:
            ui.traceback()   # Print traceback if --traceback given
            ui.warn(_("\nFailed to load repository data: %s: %s\n") % (
                e_tn, str(e)))


# At the moment repository.put is supported only on 1.0 API.
# I leave the code for 2.0 to enable it if it happens.
API_V2_SUPPORTS_MODIFY = False


def bb_modify(ui, bb_repo,
              has_wiki=None, has_issues=None, is_private=None,
              fork_policy=None, description=None, language=None):
    """Applies given modifications to the repo.
    Returns reply (whatever it is)  if succeeded, None on failure (after logging the error)"""

    # Some docs:
    # https://confluence.atlassian.com/bitbucket/repositories-endpoint-1-0-296092719.html
    # https://confluence.atlassian.com/bitbucket/repository-resource-1-0-296095202.html#repositoryResource1.0-PUTarepositoryupdate

    def setstr(payload, name, value):
        if value is not None:
            payload[name] = value

    if API_V2_SUPPORTS_MODIFY:
        def setbool(payload, name, value):
            if value is not None:
                payload[name] = value
    else:
        def setbool(payload, name, value):
            if value is not None:
                payload[name] = "true" if value else "false"

    # pybitbucket doesn't have make_payload for repository, so ...
    payload = {}
    setbool(payload, "has_wiki", has_wiki)
    setbool(payload, "has_issues", has_issues)
    setbool(payload, "is_private", is_private)
    setstr(payload, "description", description)
    setstr(payload, "language", language)
    if fork_policy is not None:
        if API_V2_SUPPORTS_MODIFY:
            payload["fork_policy"] = fork_policy
        else:
            if fork_policy == 'allow_forks':
                payload['no_public_forks'] = "false"
                payload['no_forks'] = "false"
            elif fork_policy == 'no_public_forks':
                payload['no_public_forks'] = "true"
                payload['no_forks'] = "false"
            elif fork_policy == 'no_forks':
                payload['no_public_forks'] = "true"
                payload['no_forks'] = "true"

    if API_V2_SUPPORTS_MODIFY:
        ui.status(_("Applying BitBucket metadata changes (API v2)\n"))
    else:
        ui.status(_("Applying BitBucket metadata changes (API v1)\n"))
        payload['accountname'] = bb_repo.owner.username
        payload['repo_slug'] = bb_repo.name
        posted_url = bb_repo.links['self']['href']\
                            .replace('2.0', 'api/1.0')\
                            .replace('api.bitbucket.org', 'bitbucket.org')
        bb_repo.links['self']['href'] = posted_url
        ui.debug(_("PUT-ting %s\nPayload:\n%s\n") % (
            posted_url, pprint.pformat(payload)))

    try:
        reply = bb_repo.put(payload)
    except Exception as err:
        detail = bb_unpack_error_details(ui, err)
        ui.warn(_("\nFailed to modify BitBucket repository: %s\n") % detail)
        return None

    ui.debug(_("put results: %s\n") % pprint.pformat(reply))
    return reply


def bb_print_status(ui, bb_repo, raw=False):
    """Prints repository information

    :param bb_repo: repo data dictionary, as returned by load_bb_details
    """
    if raw:
        ui.status(pprint.pformat(bb_repo.__dict__) + "\n")
    else:
        paths = u"\n".join([
            "    %-9s  %s" % ('(' + lnk['name'] + ')', lnk['href'])
            for lnk in bb_repo.links['clone']])
        if bb_repo.description:
            message = u"\n\n".join(
                textwrap.fill(
                    txt, width=65,
                    replace_whitespace=True, drop_whitespace=True,
                    initial_indent='    ', subsequent_indent='    ')
                for txt
                in bb_repo.description.replace('\r\n', '\n').split("\n\n"))
            descr = _('Description:\n') + message
        else:
            descr = _('No description')
        ui.status(_(u"""
Repository: {repo.full_name}  (scm: {repo.scm}, size: {size})
Access: {access}   (owner: {repo.owner.username})
Issues: {issues}, wiki: {wiki}, forks: {forks}, language: {repo.language}
Paths:
{paths}
{descr}
""".encode("utf-8")).format(
    repo=bb_repo,
    access=bb_repo.is_private and "private" or "public",
    wiki=bb_repo.has_wiki and "yes" or "no",
    issues=bb_repo.has_issues and "yes" or "no",
    size="%0.1f kB" % (1.0 * bb_repo.size/1024),
    forks=forks_api2opt(bb_repo.fork_policy),
    paths=paths, descr=descr))
        # (bb_repo['created_on'], bb_repo['updated_on'])


def enable_requests_debugging():
    """This enables console logging of final HTTP traffic"""
    import httplib
    import logging
    httplib.HTTPConnection.debuglevel = 2
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def bb_unpack_error_details(ui, err):
    """Tries to extract error details from exception.
    Returns best description it can find"""
    bitbucket = import_pybitbucket('bitbucket')

    # BitbucketError is common base for BadRequestError and ServerError
    if isinstance(err, bitbucket.BitbucketError):
        if isinstance(err, bitbucket.BadRequestError):
            # Those are usually readable texts worth showing as-is
            prefix = ''
        else:
            # ServerError and similar
            prefix = type(err).__name__ + ': '
        # Some exceptions have json payload. pybitbucket parses it
        # and returns where possible. Let's try... The payload is like
        # {"error": {"message": "Repository already exists."}}
        try:
            return prefix + err.error['message']
        except:  # pylint: disable=bare-except
            pass
        # If not, mayhaps we have 1.0 horror like
        # <ul class="errorlist"><li>__all__<ul class="errorlist"><li>Public repositories must allow public forks.</li></ul></li></ul>
        if hasattr(err, 'text'):
            errtxt = err.text
            match = re.search(
                r'^<ul class="errorlist">.*?<li>([^<>]+)</li></ul>',
                errtxt)
            if match:
                return prefix + match.group(1)
            else:
                return errtxt
    # Fallback
    ui.traceback()   # Print traceback if --traceback given
    return "%s: %s" % (type(err).__name__, str(err))


############################################################
# Option validators/support
############################################################

# Mapping between --forks values and bb-api values
_BB_FORKS = [
    ('public', 'allow_forks'),           # unrestricted forking
    ('private', 'no_public_forks'),      # only private forks
    ('no', 'no_forks'),                  # deny all forking
]
_BB_FORKS_ALLOWED = ", ".join([v[0] for v in _BB_FORKS])


def forks_opt2api(given_value, default=None):
    """Parses --forks value returning value for use in BB API.
    If default is given, fallbacks to it if value is missing, elsewhere fails"""
    if not given_value:
        if default:
            return default
    for mbval, apival in _BB_FORKS:
        if mbval == given_value:
            return apival
    raise util.Abort(_('Bad value of --forks: %s (expected one of: %s)') % (
        given_value, _BB_FORKS_ALLOWED))


def forks_api2opt(api_value):
    """Converts BB API forks value into more readable one"""
    for mbval, apival in _BB_FORKS:
        if apival == api_value:
            return mbval
    return api_value  # fallback


############################################################
# Other utilities
############################################################


def open_browser(ui, url):
    """
    Spawns web browser on given url. Uses
        [browser]
    config section if present. There the browser itself can
    be specified either by sth like
        type = firefox
    where value is one of documented at
    https://docs.python.org/2/library/webbrowser.html
    (firefox, chrome, opera, safari, konqueror…) or just
    by:
        command = /usr/bin/firefox
    (the former is slightly preferable, if working, as it
    can autoraise window etc).

    If [browser] section is absent, falls back to system
    defaults (clickable settings, BROWSER variable etc).
    """
    ui.status(_("Opening web browser on %s\n") % url)
    import webbrowser
    cmd = ui.config('browser', 'command')
    if cmd:
        browser_type = 'hg-browser'
        webbrowser.register(browser_type, None, webbrowser.GenericBrowser(cmd))
    else:
        browser_type = ui.config('browser', 'type')
    try:
        browser_controller = webbrowser.get(browser_type)
    except webbrowser.Error:
        ui.traceback()   # Print traceback if --traceback given
        ui.warn(_("Can not locate browser type %(type)s (bad type=%(type)s in [browser] section). Using default.\n") % {'type': browser_type})
        browser_controller = webbrowser.get()
    browser_controller.open(url, autoraise=True)


############################################################
# Commands
############################################################

cmdtable = {}
command = meu.command(cmdtable)

BB_REPO_FEATURE_OPTS = [
    # Third param is default, but also designates type
    ('w', 'wiki', False, _('enable wiki')),
    ('x', 'no-wiki', False, _('disable wiki')),
    ('i', 'issues', False, _('enable issue tracker')),
    ('j', 'no-issues', False, _('disable issues')),
    ('p', 'public', False, _('make public')),
    ('r', 'private', False, _('make private')),
    ('f', 'forks', '', _('forks approach: %s') % _BB_FORKS_ALLOWED),
    ('m', 'descr', '', _('repository description'), _('DESCRIPTION')),
    ('l', 'language', '', _('programming language')),
]

@command("bitbucket_create|bb_create",
         [
             item for item in BB_REPO_FEATURE_OPTS
             if item[1] not in ['no-wiki', 'no-issues', 'private']
         ],
         _("[NAME] [--public] [--issues] [--wiki] [--descr='...'] [--lang=LANG]"),
         optionalrepo=True)
def cmd_bb_create(ui, repo, name=None, **opts):
    """create BitBucket clone of current repo

    Does not push, just creates properly named repository
    """
    BitbucketRepository = import_pybitbucket('repository').Repository

    bb_user, bb_name, bb_alias = calculate_bb_name(ui, repo, name)
    ui.status(_("Creating BitBucket repo %(user)s/%(name)s\n") % {
        'user': bb_user, 'name': bb_name})
    bb_client = bb_connect(ui, bb_user, bb_name)

    try:
        is_public = bool(opts.get('public'))
        args = dict(
            owner=bb_user,
            scm='hg',
            repository_name=bb_name,
            # name=bb_name,         # TODO: fit to local path?
            fork_policy=forks_opt2api(
                opts['forks'],
                default='allow_forks' if is_public else 'no_public_forks'),
            is_private=not is_public,
            description=opts.get('descr', ''),
            language=opts.get('language'),
            has_issues=opts.get('issues'),
            has_wiki=opts.get('wiki'),
        )
        bb_repo = BitbucketRepository.create(
            client=bb_client, **args)
        ui.status(_("Repository created\n"))
        ui.debug(_("Creation reply: %s") % pprint.pformat(bb_repo))
        # create_repository returns seriously truncated and incompatible
        # repository details. So we can't really use it straight away,
        # instead let's check details
        bb_repo = bb_load_details(ui, bb_client, bb_user, bb_name)
        bb_print_status(ui, bb_repo, raw=opts.get('raw'))
        bb_url = bb_repo.links['html']['href']
        ui.status(_("""
Now `hg push %s` to push the code
Visit %s to review details
""") % (
            bb_alias or bb_url, bb_url))
    except Exception as e:
        detail = bb_unpack_error_details(ui, e)
        ui.warn(_("\nFailed to create BitBucket repository: %s\n") % detail)
        return True


@command("bitbucket_modify|bb_modify",
         BB_REPO_FEATURE_OPTS,
         _("[NAME] [--public|--private] [--issues|--no-issues] [--wiki|--no-wiki] [--descr=DESCR] [--lang=LANG]"),
         optionalrepo=True)
def cmd_bb_modify(ui, repo, name=None, **opts):   # pylint: disable=too-many-branches,too-many-statements
    """update BitBucket clone metadata"""
    bb_user, bb_name, __ = calculate_bb_name(ui, repo, name)
    bb_client = bb_connect(ui, bb_user, bb_name)
    bb_repo = bb_load_details(ui, bb_client, bb_user, bb_name)
    if not bb_repo:
        return True

    args = {}
    if opts.get('wiki'):
        args['has_wiki'] = True
    elif opts.get('no_wiki'):
        args['has_wiki'] = False
    if opts.get('issues'):
        args['has_issues'] = True
    elif opts.get('no_issues'):
        args['has_issues'] = False
    if opts.get('private'):
        args['is_private'] = True
    elif opts.get('public'):
        args['is_private'] = False
    if opts.get('forks'):
        args['fork_policy'] = forks_opt2api(opts['forks'])
    else:
        # BitBucket fails with 'public repositories must allow public forks'
        # if forks model is not public. So let's accomodate that as user
        # hasn't decided otherwise. For symmetry switch back when going priv
        if opts.get('public'):
            args['fork_policy'] = 'allow_forks'
        if opts.get('private'):
            args['fork_policy'] = 'no_public_forks'
    if opts.get('descr'):
        args['description'] = opts['descr']
    if opts.get('language'):
        args['language'] = opts['language']

    if not args:
        ui.warn(_("Nothing to change\n"))
        return False

    if not bb_modify(ui, bb_repo, **args):
        return True
    ui.status(_("Changes saved\n"))

    bb_repo = bb_load_details(ui, bb_client, bb_user, bb_name)
    if not bb_repo:
        return True
    bb_print_status(ui, bb_repo)


@command("bitbucket_status|bb_status",
         [
             ('r', 'raw', False, _('dumb raw technical data')),
         ],
         _("[NAME] [--raw]"),
         optionalrepo=True)
def cmd_bb_status(ui, repo, name=None, **opts):
    """checks and prints BitBucket clone status"""
    bb_user, bb_name, __ = calculate_bb_name(ui, repo, name)
    ui.status(_("Checking status of BitBucket repo %s belonging to %s\n") % (
        bb_name, bb_user))
    bb_client = bb_connect(ui, bb_user, bb_name)
    bb_repo = bb_load_details(ui, bb_client, bb_user, bb_name)
    if bb_repo:
        bb_print_status(ui, bb_repo, raw=opts.get('raw'))
    else:
        return True


@command("bitbucket_delete|bb_delete",
         [
             ('', 'force', False, _('do not prompt, delete repository straight away')),
         ],
         _("[NAME]"),
         optionalrepo=True)
def cmd_bb_delete(ui, repo, name=None, **opts):
    """delete BitBucket clone"""
    bb_user, bb_name, __ = calculate_bb_name(ui, repo, name)
    bb_client = bb_connect(ui, bb_user, bb_name)
    bb_repo = bb_load_details(ui, bb_client, bb_user, bb_name)
    if not bb_repo:
        return True
    bb_print_status(ui, bb_repo)
    if not opts.get('force'):
        val = ui.promptchoice(
            _('are you sure to delete this repository (Y/N)?'
              '$$ &Yes $$ &No'),
            default=1)
    else:
        val = 0
    if val == 0:
        ui.status(_("Deleting BitBucket clone %s\n") % (bb_repo.full_name))
        bb_repo.delete()
        ui.status(_("BitBucket clone deleted\n"))
    else:
        ui.status(_("OK, not deleting\n"))

# List of bitbucket web pages inside repo. Used to construct
# and interpret bb_goto params. Every item has, in order:
# - short option
# - long option
# - url snippet
# - description
BB_SUB_PAGES = [
    ('', 'overview', 'overview', _('goto overview')),
    ('s', 'source', 'src', _('goto source')),
    ('l', 'log', 'commits', _('goto commits (history)')),
    ('b', 'branches', 'branches', _('goto branches')),
    ('p', 'pulls', 'pull-requests', _('goto pull-requests')),
    ('d', 'downloads', 'downloads', _('goto downloads')),
    ('a', 'admin', 'admin', _('goto admin')),
    ('i', 'issues', 'issues?status=new&status=open', _('goto issues')),
]

@command("bitbucket_goto|bb_goto",
         [
             (bb_short, bb_long, False, bb_descr)
             for bb_short, bb_long, __, bb_descr in BB_SUB_PAGES
         ],
         _("[NAME] [" + "|".join(["--" + bb_p[1] for bb_p in BB_SUB_PAGES]) + "]"),
         optionalrepo=True)
def cmd_bb_goto(ui, repo, name=None, **opts):
    """open web browser on BitBucket repository page"""
    bb_user, bb_name, __ = calculate_bb_name(ui, repo, name)

    # Pick the page
    page_sfx = BB_SUB_PAGES[0][2]   # default
    for __, option, sfx, __ in BB_SUB_PAGES:
        if opts.get(option):
            page_sfx = sfx

    url = 'https://bitbucket.org/%s/%s/%s' % (
        bb_user, bb_name, page_sfx)

    open_browser(ui, url)


############################################################
# Extension setup
############################################################

# testedwith = '3.0 3.1.2 3.3'
buglink = 'https://bitbucket.org/Mekk/mercurial-bitbucketize/issues'
