#!/usr/bin/env python

import os
import re
import signal
import subprocess
import sys
import urwid

def get_value(output, n = 0):
    match = re.match("[^\d]*(\d+).*", output)
    if (match):
        # TODO: what if n is bad?
        return int(match.group(n+1))
    return None

def call(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True)
        return output.rstrip()
    except OSError:
        print("Couldn't execute command: " + " ".join(cmd))
        sys.exit(1)

def test_command(cmd):
    output = call(cmd)
    value = get_value(output)
    if (value == None):
        print("Couldn't find data in command's output.")
        sys.exit(1)

def usage():
    print("vander - live graphing of a command's output")
    print("vander [-t ...] [-c ...] <command>")
    print(" -t <n> : wait <n> seconds between each command. eg. 0.5, 3")
    print(" -c <color> : use <color> for the graph. eg. dark red, white")

def add_data_point(data_points, data_point):
    data_points.pop(0)
    data_points.append((data_point, ))

def get_data_ceiling(data_points):
    maximum = 0
    for (i, ) in data_points:
        if (maximum < i):
            maximum = i
    return maximum

def get_unique_points(data_points):
    uniques = []
    for (i, ) in data_points:
        if i not in uniques and (i != 0):
            uniques.append(i)
    return sorted(uniques)[:-1]

def update_y_axis(maximum, data_points):
    if maximum == 0:
        return

    uniques = get_unique_points(data_points)

    graph_height = settings["screen height"] - state["title rows"]

    if len(uniques) > 5:
        new_uniques = []
        factor = len(uniques) / 5
        i = 0
        while (i < len(uniques)):
            new_uniques.append(uniques[i])
            i += factor
        uniques = new_uniques

    placements = []
    for unique in uniques:
        placement = graph_height - int((float(unique) / maximum) * graph_height)
        if (placement > graph_height):
            placement = graph_height
        placements.append((placement, unique))

    final = ["\n"] * (graph_height)
    final[0] = str(maximum) + "\n"
    final[-1] = "0" + "\n"
    for (placement, unique) in placements:
        if (placement > 0) and (placement < (graph_height-1)):
            final[placement] = str(unique) + "\n"

    new_text = "".join(final)
    state["y axis text"].set_text(new_text)

def update_graph():
    data_point = get_value(call(state["command"]))
    add_data_point(state["data points"], data_point)
    maximum = get_data_ceiling(state["data points"])
    state["graph"].set_data(state["data points"], maximum)
    update_y_axis(maximum, state["data points"])

def handle_input(key):
    if key == 'Q' or key == 'q':
        raise urwid.ExitMainLoop()

def quit_after_sigint(_, __):
    raise urwid.ExitMainLoop()

def periodic(main_loop, user_data):
    update_graph()
    main_loop.set_alarm_in(settings["update period"], periodic)

def update_screen_dimensions(settings):
    screen_height, screen_width = os.popen('stty size', 'r').read().split()
    settings["screen height"] = int(screen_height)
    settings["screen width"] = int(screen_width)

def read_arguments_and_get_command(settings):
    settings["update period"] = 1
    settings["graph color"] = "white"

    # Build the command, and possibly read some flags.
    command = list()
    read_all_flags = False
    i = 1
    while i != len(sys.argv):
        if not read_all_flags:
            if sys.argv[i] == "-t":
                settings["update period"] = float(sys.argv[i+1])
                i += 1
            elif sys.argv[i] == "-c":
                settings["graph color"] = sys.argv[i+1]
                i += 1
            elif sys.argv[i] == "-h":
                usage()
                sys.exit(0)
        else:
            read_all_flags = True
        command.append(sys.argv[i])
        i += 1

    if len(command) == 0:
        print("ERROR: No command specified.")
        usage()
        sys.exit(1)

    return command

def create_ui(settings, command, state):
    state["command"] = command

    palette = [
        ("titlebar", "white", "black"),
        ("background", "white", "black"),
        ("graph_top", settings["graph color"], settings["graph color"]),
        ("line", "white", "white"),
        ("graph_fill", "white", "black")
        ]

    title_text = "Q quits. Graphing command: '" + " ".join(command) + "'"
    header_text = urwid.Text(title_text)
    header = urwid.AttrMap(header_text, "titlebar")

    state["title rows"] = header_text.rows((settings["screen width"], ))
    graph_attrs = [("background", " "), ("graph_top", "#"), ("graph_fill", "&")]
    state["graph"] = urwid.BarGraph(graph_attrs)

    y_axis_size = 10

    state["y axis text"] = urwid.Text("MAXIMUM", align="right")

    y_axis = urwid.AttrMap(state["y axis text"], "titlebar")
    columns = urwid.Columns([(y_axis_size, y_axis), ("weight", 1, urwid.LineBox(urwid.BoxAdapter(state["graph"], settings["screen height"] - (2 + state["title rows"]))))])

    layout = urwid.Frame(header=header, body=urwid.Filler(columns))

    max_data_points = settings["screen width"] - y_axis_size - 2
    state["data points"] = list()
    # Put in fake data points at the start, so the graphing comes
    # in from the right...
    for i in xrange(0, max_data_points):
        state["data points"].append((0, ))

    main_loop = urwid.MainLoop(layout, palette, unhandled_input=handle_input)
    periodic(main_loop, None)

    return main_loop

settings = dict()
state = dict()
def main():
    update_screen_dimensions(settings)
    command = read_arguments_and_get_command(settings)

    # Make sure the command actually returns an integer value somewhere.
    test_command(command)

    signal.signal(signal.SIGINT, quit_after_sigint)
    main_loop = create_ui(settings, command, state)
    main_loop.run()
