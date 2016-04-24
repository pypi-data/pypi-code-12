import argparse
import logging
import six

from github import GithubObject

import prboard
from hub import DashBoard
# import prboard.filters as filters
# import prboard.settings as settings
# from prboard.utils import parse_pr_filters
import settings
import filters
from utils import parse_pr_filters, overload_settings_from_file

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger('')
logging.getLogger('sh').setLevel(logging.ERROR)

VERBOSITY_MAPPING = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}

overload_settings_from_file()

parser = argparse.ArgumentParser('')
parser.add_argument(
    "-b", "--baseurl",
    default=settings.PRBOARD_ORG,
    dest="baseurl",
    type=six.text_type,
    help="Github base url to be used."
)

parser.add_argument(
    "-o", "--org",
    default=settings.PRBOARD_ORG,
    dest="org",
    type=six.text_type,
    help="Organization name to be checked. This is applicable for enterprise users. "
         "For personal accounts user name is sufficient"
)

parser.add_argument(
    "-r", "--repo",
    default=settings.PRBOARD_REPO_FILTER,
    dest="repos",
    type=six.text_type,
    help="Repo names to be filtered. Provide comma separated multiple repos"
)

parser.add_argument(
    "-s", "--status",
    default=GithubObject.NotSet,
    dest="status",
    type=six.text_type,
    help="Status to be filtered. Allowed values are open, closed, all. Default is all"
)

parser.add_argument(
    "-u", "--user",
    default=settings.PRBOARD_GITHUB_USERNAME,
    dest="username",
    type=six.text_type,
    help="User name to login to Github. Default is picked from settings.DEFAULT_GITHUB_USER"
)

parser.add_argument(
    "-ru", "--repouser",
    default=settings.PRBOARD_GITHUB_USERNAME,
    dest="repouser",
    type=six.text_type,
    help="User name on Github for which the dashboard must be checked. "
         "Login user name is different from checking user name. For instance you may want to check PRs on your "
         "colleague's Github account, but login with yours. This parameter is to provide your colleague's user name"
)

parser.add_argument(
    "-p", "--password",
    default=settings.PRBOARD_GITHUB_PASSWORD,
    dest="password",
    type=six.text_type,
    help="Password to login to Github. Default is picked from settings.PRBOARD_GITHUB_PASSWORD"
)

parser.add_argument(
    "-pr", "--pull",
    default=settings.PRBOARD_REPO_FILTER,
    dest="pull",
    type=six.text_type,
    help="Filter Pull requests, with the following criteria"
         "By PR Number ---->  num:123"
         "By PR Labels ---->  labels:label1;label2;label3"
         "By PR Title  ---->  title:pr_title   (wilcard match)"
         "By PR Title  ---->  etitle:pr_title  (exact match)"
         "By PR All    ---->  num:123,labels:label1;label2;label3,title:pr_title"
)

parser.add_argument(
    "-d", "--detailed_mode",
    default=settings.PRBOARD_DETALED_MODE,
    dest="detailed_mode",
    type=bool,
    help="Option to control output mode. If Detailed mode is set each PR and it's comments is displayed"
)

parser.add_argument('-v', '--verbose',
                    action='count',
                    default=0,
                    help='Control verbosity level. Can be supplied multiple times to increase verbosity level', )

parser.add_argument('-V', '--version', action='version', version='%(prog)s v' + prboard.__version__,
                    help='To know prboard version number', )


def main():
    args = parser.parse_args()
    kwargs = {}
    if args.baseurl:
        kwargs['baseurl'] = args.baseurl
    if args.username:
        kwargs['user_or_token'] = args.username
    if args.repouser:
        kwargs['repouser'] = args.repouser
    if args.password:
        kwargs['password'] = args.password
    if args.repos:
        repo_filters = map(filters.RepoFilter, filter(lambda x: x != '', args.repos.split(",")))
        kwargs['repo_filter'] = repo_filters
    if args.pull:
        pr_filters = parse_pr_filters(args.pull)
        kwargs['pr_filter'] = pr_filters
    if args.detailed_mode:
        kwargs['detailed_mode'] = args.detailed_mode

    DashBoard(**kwargs).dash()

if __name__ == '__main__':
    main()
