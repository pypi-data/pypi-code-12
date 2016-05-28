# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class DotNet45(Dependency):
    name = "dotnet45"
    depends = "wic",
    url = "http://cuckoo.sh/vmcloak/NDP452-KB2901907-x86-x64-AllOS-ENU.exe"
    sha1 = "89f86f9522dc7a8a965facce839abb790a285a63"

    def run(self):
        # TODO Does not work on Windows XP at the moment.
        self.upload_dependency("C:\\dotnet45.exe")
        self.a.execute("C:\\dotnet45.exe /passive /norestart")
        self.a.remove("C:\\dotnet45.exe")
