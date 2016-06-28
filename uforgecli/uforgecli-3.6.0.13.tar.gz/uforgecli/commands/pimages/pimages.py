
__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils import *
from hurry.filesize import size
from uforgecli.utils.extract_id_utils import extractId
from uforgecli.utils.compare_utils import compare
import shlex


class Pimages_Cmd(Cmd, CoreGlobal):
        """Administer published images for a user"""

        cmd_name = "pimages"

        def __init__(self):
                super(Pimages_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help=True, description="List all the published images created by a user")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="Name of the user.")
                optional.add_argument('--os', dest='os', nargs='+', required=False, help="Only display templates that have been built from the operating system(s). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--name', dest='name', nargs='+', required=False, help="Only display published images that have the name matching this name. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--cloud', dest='cloud', nargs='+', required=False, help="Only display published images that have been published to the following cloud environment(s). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        printer.out("Getting published images ...")
                        allPimages = self.api.Users(doArgs.account).Pimages.Get()
                        allPimages = allPimages.publishImages.publishImage

                        userAppliances = self.api.Users(doArgs.account).Appliances.Getall()
                        userAppliances = userAppliances.appliances.appliance

                        if allPimages is None or len(allPimages) == 0:
                                printer.out("No publish images for user [" + doArgs.account + "].")
                                return 0

                        if doArgs.name:
                                allPimages = compare(allPimages, doArgs.name, "name")

                        if doArgs.os is not None:
                                allPimages = compare(list=allPimages, values=doArgs.os, attrName='distributionName', subattrName=None, otherList=userAppliances, linkProperties=['applianceUri', 'uri'])

                        if doArgs.cloud is not None:
                                allPimages = compare(list=allPimages, values=doArgs.cloud, attrName='format', subattrName=None, otherList=userAppliances, linkProperties=['applianceUri', 'uri'])

                        table = Texttable(200)
                        table.set_cols_align(["l", "l", "l", "l", "l", "l", "l", "l", "l"])
                        table.header(["Id", "Name", "Version", "Rev", "OS", "Cloud", "Published", "Size", "Status"])
                        for item in allPimages:
                                if item.status.error:
                                        status = "Error"
                                elif item.status.cancelled:
                                        status = "Cancelled"
                                elif item.status.complete:
                                        status = "Done"
                                else:
                                        status = "Publishing"
                                for item2 in userAppliances:
                                        if item.applianceUri == item2.uri:
                                                os = item2.distributionName + " " + item2.archName
                                table.add_row([item.dbId, item.name, item.version, item.revision, os, item.targetFormat.name, item.created.strftime("%Y-%m-%d %H:%M:%S"), size(item.size), status])
                        print table.draw() + "\n"
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_info(self):
                doParser = ArgumentParser(add_help=True, description="Retrieve detailed information of a published image")

                mandatory = doParser.add_argument_group("mandatory arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="Name of the user.")
                mandatory.add_argument('--id', dest='id', required=True, help="The unique identifier of the published image to retrieve.")

                return doParser

        def do_info(self, args):
                try:
                        doParser = self.arg_info()
                        doArgs = doParser.parse_args(shlex.split(args))

                        allPimages = self.api.Users(doArgs.account).Pimages.Get()
                        userAppliances = self.api.Users(doArgs.account).Appliances.Getall()

                        printer.out("Getting published image with id [" + doArgs.id + "] ...")

                        Exist = False
                        for item in allPimages.publishImages.publishImage:
                                if str(item.dbId) == str(doArgs.id):
                                        printer.out("Published image informations :")
                                        for item2 in userAppliances.appliances.appliance:
                                                if item.applianceUri == item2.uri:
                                                        os = item2.distributionName + " " + item2.archName
                                        if item.status.published:
                                                published = "Yes"
                                        else:
                                                published = "No"
                                        Exist = True
                                        table = Texttable(200)
                                        table.set_cols_align(["l", "l"])
                                        table.add_row(["Name", item.name])
                                        table.add_row(["ID", item.dbId])
                                        table.add_row(["Cloud", item.format])
                                        table.add_row(["Version", item.version])
                                        table.add_row(["Revision", item.revision])
                                        table.add_row(["Uri", item.uri])
                                        table.add_row(["OS", os])
                                        table.add_row(["Template ID", extractId(item.uri)])
                                        table.add_row(["Generated Image Id", extractId(item.imageUri)])
                                        table.add_row(["Created", item.created.strftime("%Y-%m-%d %H:%M:%S")])
                                        table.add_row(["Size", size(item.size)])
                                        table.add_row(["Description", item.description])
                                        table.add_row(["Published", published])
                                        table.add_row(["Published Cloud Id", item.cloudId])
                                        print table.draw() + "\n"
                        if not Exist:
                                printer.out("Published image with ID [" + doArgs.id + "] was not found.")

                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_info()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_info(self):
                doParser = self.arg_info()
                doParser.print_help()
