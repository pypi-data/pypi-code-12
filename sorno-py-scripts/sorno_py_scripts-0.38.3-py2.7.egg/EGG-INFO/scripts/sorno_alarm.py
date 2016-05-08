#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""
sorno_alarm.py


   Copyright 2014 Heung Ming Tai

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

import argparse
import time

from Tkinter import *
import tkFont

class Alarm(object):
    def __init__(self, use_pop_up=False):
        """
        use_pop_up -- By default, the alarm uses the system bell. This option
            changes it to use a UI pop-up instead.
        """
        self.use_pop_up = use_pop_up

    def countdown(self, seconds):
        print("Current time is %s" % time.asctime())
        print("Sleep for %s seconds" % seconds)
        time.sleep(seconds)
        print("Alarm goes off!")

        if self.use_pop_up:
            root = Tk()
            custom_font = tkFont.Font(family="Helvetica", size=30)
            root.tkraise()
            w = Label(
                root,
                text="Alarm goes off!"
                ,
                font=custom_font,
                fg="red",
            )
            w.pack()
            root.mainloop()
        else:
            # System bell
            print("\a")
            raw_input("Press enter to continue...")

class AlarmApp(object):
    def __init__(self, alarm):
        self.alarm = alarm

    def continuous_alarm(self, seconds):
        while True:
            self.alarm.countdown(seconds)


def _main():
    description = """
A console alarm which uses the system bell as the alarm bell by default. You set how
many seconds before the alarm goes off, not an absolute time in the future.
After you respond to the bell (e.g. please "Enter" in the console after the
system bell rings), it restarts the alarm and will ring again after your
specified time. Use control-c to exit the alarm completely.

Synopsis:
sorno_alarm.py <number of seconds before the alarm rings it bell>
    """

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("seconds", type=int)
    parser.add_argument(
        "--use-pop-up",
        action="store_true",
        help="By default, the alarm uses the system bell."
        " This option changes it to use a UI pop-up instead.",
    )

    args = parser.parse_args()

    alarm = Alarm(use_pop_up=args.use_pop_up)

    app = AlarmApp(alarm)
    app.continuous_alarm(args.seconds)

if __name__ == '__main__':
    _main()
