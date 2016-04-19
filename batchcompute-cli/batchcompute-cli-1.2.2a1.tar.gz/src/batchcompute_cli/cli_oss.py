
from .externals.command import Command
from .action import oss_pwd,oss_upload,oss_download,oss_ls,oss_delete,oss_cat
from . import i18n_util
from .const import *


MSG=i18n_util.msg()


def init(cmd_oss):

    # pwd
    cmd_oss_pwd = Command('pwd',
                             description=MSG['oss']['pwd']['description'],
                             func=oss_pwd.pwd)
    cmd_oss.action(cmd_oss_pwd)


     # ls
    cmd_oss_ls = Command('ls',
                         arguments=['osspath'],
                             description=MSG['oss']['ls']['description'],
                         usage="""Usage: %s oss|o ls [osspath] [option]

  Examples:
      1. %s o ls                    # list <current_osspath>, current_osspath is set by "bcs config -o <current_osspath>"
      2. %s o ls oss://bucket/abc/
      3. %s o ls ca/                # list <current_osspath>/ca/
                         """,
                             func=oss_ls.ls)
    cmd_oss_ls.option('-t, --top [num]', MSG['oss']['ls']['option']['top'])
    cmd_oss_ls.option('-n, --name [name]', MSG['oss']['ls']['option']['name'])
    cmd_oss.action(cmd_oss_ls)


     # cat
    cmd_oss_cat = Command('cat', visible=False,
                             arguments=['osspath'],
                             description=MSG['oss']['cat']['description'],
                             func=oss_cat.cat)
    cmd_oss.action(cmd_oss_cat)


    # upload
    cmd_oss_upload = Command('upload', alias=['up'],
                             arguments=['localpath','osspath'],
                             description=MSG['oss']['upload']['description'],
                             usage='''Usage: %s oss|o upload|up <filename> <osspath> [option]

  Examples:
      1. %s o upload ./worker.tar.gz  oss://my-bucket/abc/worker.tar.gz # upload file
      3. %s o upload ./abc/  oss://my-bucket/abc/                       # upload folder''' % (
                             COMMAND,CMD,CMD),
                             func=oss_upload.upload)
    cmd_oss.action(cmd_oss_upload)


    # download
    cmd_oss_download = Command('download',alias=['down'],
                             arguments=['osspath','localpath'],
                             description=MSG['oss']['download']['description'],
                             usage='''Usage: %s oss|o download|down <osspath> <filename> [option]

  Examples:
      1. %s o download oss://my-bucket/abc/worker.tar.gz # download to ./
      2. %s o download oss://my-bucket/abc/  ./abc/      # download to ./abc/''' % (
                             COMMAND,CMD,CMD),
                             func=oss_download.download)
    cmd_oss.action(cmd_oss_download)


     # remove
    cmd_oss_delete = Command('delete',alias=['del'],
                             arguments=['osspath'],
                             description=MSG['oss']['delete']['description'],
                             usage='''Usage: %s oss|o delete|del <osspath> [option]

  Examples:
      1. %s o del oss://my-bucket/abc/worker.tar.gz
      2. %s o del oss://my-bucket/abc/               # delete folder''' % (
                             COMMAND,CMD,CMD),
                             func=oss_delete.delete)
    cmd_oss_delete.option('-y, --yes', MSG['oss']['delete']['option']['yes'])
    cmd_oss.action(cmd_oss_delete)
