__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from uforgecli.utils.uforgecli_utils import *
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils.generics_utils import order_list_object_by
from ussclicore.utils import printer
from uforge.objects import uforge
from ussclicore.utils import generics_utils
from uforgecli.utils import uforgecli_utils
import pyxb
import datetime
import shlex

class Org_Golden_Cmd(Cmd, CoreGlobal):
        """Golden image operation (list|Create)"""

        cmd_name = "golden"

        def __init__(self):
                super(Org_Golden_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List golden images for a distribution")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--arch', dest='arch', type=str, required=True, help="Operating system architecture (i386, x86_64).")
                mandatory.add_argument('--version', dest='version', type=str, required=True, help="Operating system version (13, 5.6, ...)")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        org = org_utils.org_get(self.api, doArgs.org)
                        allDist = self.api.Orgs(org.dbId).Distributions.Getall()
                        allDist = allDist.distributions.distribution

                        goldenId = None
                        for distrib in allDist:
                                if distrib.name == doArgs.name and distrib.version == doArgs.version and distrib.arch == doArgs.arch:
                                        goldenId = distrib.dbId
                                        break

                        if goldenId is None:
                                printer.out("No distributions found with the arguments entered.")
                                return 2

                        allGoldens = self.api.Orgs(org.dbId).Distributions(goldenId).Goldens.Getall()
                        if allGoldens is None or len(allGoldens) == 0:
                                printer.out("No Golden Image found for this distribution.")
                                return 0
                        allGoldens = order_list_object_by(allGoldens.pkgs.pkg, "name")

                        if len(allGoldens) is 0:
                                printer.out("No golden image for ["+org.name+"]")
                                return 0

                        table = Texttable(200)
                        table.set_cols_align(["l", "l"])
                        table.header(["Name", "Date"])

                        for item in allGoldens:
                                table.add_row([item.name, item.pkgBuildDate.strftime("%Y-%m-%d %H:%M:%S")])

                        print table.draw() + "\n"

                        printer.out("Found "+str(len(allGoldens))+" golden images in organization ["+org.name+"].")
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_create(self):
                doParser = ArgumentParser(add_help = True, description="Create a golden for a distribution")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--arch', dest='arch', type=str, required=True, help="Operating system architecture (i386, x86_64).")
                mandatory.add_argument('--edition', dest='edition', type=str, required=True, help="The edition of the golden image (ex: Standard)")
                mandatory.add_argument('--goldenDate', dest='goldenDate', type=str, required=True, help="The date of the golden image (ex: 2014-04-28)")
                mandatory.add_argument('--goldenName', dest='goldenName', type=str, required=True, help="The file name of the golden image")
                mandatory.add_argument('--language', dest='language', type=str, required=True, help="The language of the golden image (ex: English, French)")
                mandatory.add_argument('--type', dest='type', type=str, required=True, help="The type of the golden image (ex: Core, Full)")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed.")
                mandatory.add_argument('--version', dest='version', type=str, required=True, help="Operating system version (13, 5.6, ...)")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_create(self, args):
                try:
                        doParser = self.arg_create()
                        doArgs = doParser.parse_args(shlex.split(args))

                        org = org_utils.org_get(self.api, doArgs.org)
                        allDist = self.api.Orgs(org.dbId).Distributions.Getall()
                        allDist = allDist.distributions.distribution

                        goldenId = None
                        for distrib in allDist:
                                if distrib.name == doArgs.name and distrib.version == doArgs.version and distrib.arch == doArgs.arch:
                                        goldenId = distrib.dbId

                        if goldenId is None:
                                printer.out("No distributions found with the arguments entered.")
                                return 0

                        result = self.api.Orgs(org.dbId).Distributions(goldenId).Goldens.Create(Language=doArgs.language, Edition=doArgs.edition, Type=doArgs.type, Goldendate=doArgs.goldenDate, Filename=doArgs.goldenName, body=None)
                        printer.out("Golden image [" + result.name + "] has been created", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_create()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_create(self):
                doParser = self.arg_create()
                doParser.print_help()