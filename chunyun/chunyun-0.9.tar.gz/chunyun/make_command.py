import os
import random

from .command import Command


SQL_TPL = """
-- @up
---------------------------------------------------------------------
-- Migration SQL that makes the change goes here.

-- @down
---------------------------------------------------------------------
-- SQL to undo the change goes here.

"""


class MakeCommand(Command):

    def run(self):
        description = self.args.description
        files = os.listdir('migrations')
        files.sort()
        if len(files) == 0:
            filename = "001_{}.sql".format(description)
        else:
            file = files[-1]
            number, _ = file.split("_", 1)
            number = int(number)
            number += 1
            filename = "{:03d}_{:s}_{:d}.sql".format(number, description, random.randint(100000, 999999))

        with open(os.path.join('migrations', filename), "w") as handle:
            handle.write(SQL_TPL)

        print("{} is created.".format(filename))

