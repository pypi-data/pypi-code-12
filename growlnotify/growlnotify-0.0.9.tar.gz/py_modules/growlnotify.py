#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fullpath import fullpath
from isstring import isstring
import only
from subopen import subopen
from public import public


def _open():
    returncode, _, _ = subopen(["killall", "-s", "Growl"])
    if returncode != 0:
        returncode, _, stderr = subopen(["open", "-a", "Growl 2"])
        if returncode != 0:
            raise OSError(stderr)


def _run(args, stdin):
    # known errors:
    # We failed to notify after succesfully registering
    # fix Failed to register with
    # ----
    # 1) different versions produce diffrent errors
    # 2) pirate versions contains additional errors
    # repeat few until 0 exit status
    i = 0
    while i < 50:
        returncode, _, stderr = subopen(args, stdin=stdin)
        if returncode == 0:
            return
        if not (stderr.find("Failed to register with") >=
                0 or stderr.find("failed to notify") >= 0):
            return
        i += 1


@only.osx
@public
def growlnotify(title=None, message=None, app=None,
                sticky=False, icon=None, image=None, url=None):
    if title and not isstring(title):
        title = str(title)
    if not message:
        message = ""
    if message and not isstring(message):
        message = str(message)
    # if message and isstring(message):
        # message = message.encode("utf-8")
    if title and title[0] == "-":
        title = "\\" + title
    # if title and isstring(title):
        # title = title.encode("utf-8")
    if not message and not title:
        title = ""
    args = []
    if title:
        args += ["-t", title]
    if app:
        args += ["-a", app]
    if icon:
        args += ["--icon", icon]
    if image:
        args += ["--image", fullpath(image)]
    if sticky:
        args += ["-s"]
    if url:
        args += ["--url", url]
    stdin = message
    # need first growlnotify arg for correct app icon
    args = ["growlnotify"] + args
    _open()
    _run(args, stdin)
