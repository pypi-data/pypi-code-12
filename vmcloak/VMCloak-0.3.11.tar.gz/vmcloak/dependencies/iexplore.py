# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class InternetExplorer10(Dependency):
    name = "iexplore10"
    exes = [
        {
            "target": "win7x86",
            "sha1": "e6552da75de95f6b1f7937c2bdb5fe14443dea2a",
            "url": "http://cuckoo.sh/vmcloak/IE10-Windows6.1-x86-en-us.exe",
        },
        {
            "target": "win7x64",
            "sha1": "17d1eaca123e453269b12b20863fd5ce96727888",
            "url": "http://cuckoo.sh/vmcloak/IE10-Windows6.1-x64-en-us.exe",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\iexplore10.exe")
        self.a.execute("C:\\iexplore10.exe /passive /update-no")
        self.wait_process_exit("TrustedInstaller.exe")
        self.a.remove("C:\\iexplore10.exe")
