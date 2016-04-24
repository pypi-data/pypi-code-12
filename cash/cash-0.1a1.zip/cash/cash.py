# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from os import remove
from os.path import dirname, exists, expanduser, isdir, isfile, join
from sys import argv, exit

from configobj import ConfigObj

from cash.accessory import create_directory, get_date_time
from cash.converter import csv2df
from cash.graph import create_bar_chart

module_location = dirname(__file__)
config_cash_abs_path = join(module_location, "config/cash.ini")
config = ConfigObj(config_cash_abs_path)

argparse = {} # Strings for -h --help
messages = {} # Strings for output


def create_dictionaries():
    """Create "argparse" and "messages" dictionaries"""

    config_argparse_rel_path = config["config_argparse_rel_path"]
    config_argparse_abs_path = join(module_location, config_argparse_rel_path)
    config_messages_rel_path = config["config_messages_rel_path"]
    config_messages_abs_path = join(module_location, config_messages_rel_path)
    with open(config_argparse_abs_path, 'r') as f:
        argparse_list = f.read().splitlines()
    for i in range(0, len(argparse_list), 2):
        argparse[argparse_list[i]] = argparse_list[i+1]
    with open(config_messages_abs_path, 'r') as f:
        messages_list = f.read().splitlines()
    for i in range(0, len(messages_list), 2):
        messages[messages_list[i]] = messages_list[i+1]

def img(args):
    """Create bar chart img"""

    def check_labels(labels):
        """Check 'labels' var"""

        years = []

        label_min = min(labels)
        label_max = max(labels)
        for label in labels:
            year = label[:4]
            if year not in years:
                years.append(year)
        for year in years:
            for i in range(1,13):
                month = str(i)
                if len(month) == 1:
                    month = '0' + month
                label = year + month
                if ((label > label_min) and (label < label_max) and
                        (label not in labels)):
                    labels.append(label)
        labels.sort()
        return labels

    data={}

    # Read CSV file into DataFrame
    df = csv2df(config)
    # Sort by the values along either axis
    df.sort_values(by="date", axis=0, ascending=True, inplace=True,
                   na_position='last')
    # Get data to 'data' dict var
    for index, date in enumerate(df["date"]):
        label = date[:7].replace('-',"")
        if label not in data:
            data[label] = df["amount"][index] / df["exchange_rate"][index]
        else:
            data[label] += (df["amount"][index] / df["exchange_rate"][index])
    # Get labels to 'labels' list var
    labels = list(data.keys())
    labels = check_labels(labels)
    # Get heights to 'heights' list var
    heights = []
    for label in labels:
        if label in data:
            heights.append(data[label])
        else:
            heights.append(0.00)
    # Improve labels look
    for index, label in enumerate(labels):
        labels[index] = label[4:] + "\n" + label[:4]
    # Create bar chart img
    create_bar_chart(labels, heights, config=config)

def init(args):
    """Init the cash utility"""

    def init_csv(csv_abs_path):
        """Init CSV file"""

        date = get_date_time()[:10]
        header = "\"date\",\"amount\",\"exchange_rate\"\n"
        empty_data = "\"%s\",0.00,1\n" % date
        with open(csv_abs_path, 'w') as f:
            f.write(header)
            f.write(empty_data)

    csv_abs_path = expanduser(config["csv_abs_path"])
    dir_abs_path = dirname(csv_abs_path)
    if exists(csv_abs_path) and isfile(csv_abs_path):
        print(messages["_delete_csv"] % csv_abs_path)
        try:
            answer = raw_input()
        except NameError:
            answer = input()
        answer_lower = answer.lower()
        if ((answer_lower == 'y') or (answer_lower == 'yes') or
            (answer_lower == 'yep')):
            if exists(dir_abs_path) and isdir(dir_abs_path):
                pass
            elif exists(dir_abs_path) and isfile(dir_abs_path):
                remove(dir_abs_path)
                create_directory(dir_abs_path, messages=messages)
            else:
                create_directory(dir_abs_path, messages=messages)
            init_csv(csv_abs_path)
    else:
        if exists(dir_abs_path) and isdir(dir_abs_path):
            pass
        elif exists(dir_abs_path) and isfile(dir_abs_path):
            remove(dir_abs_path)
            create_directory(dir_abs_path, messages=messages)
        else:
            create_directory(dir_abs_path, messages=messages)
        init_csv(csv_abs_path)

def main():
    """Main function"""

    create_dictionaries()
    args = parse_command_line_args()
    args.function_name(args)

def parse_command_line_args():
    """Parse command line arguments"""

    # Create top parser
    parser = ArgumentParser(prog="cash", description=argparse["_parser"],
                            add_help=True)
    parser.add_argument("-v", "--version", action="version",
                        version="cash 0.1a1")
    # Create subparsers for the top parser
    subparsers = parser.add_subparsers(title=argparse["_subparsers"])
    # Create the parser for the "img" subcommand
    parser_img = subparsers.add_parser(
            "img", description=argparse["_parser_img"],
            help=argparse["_parser_img"])
    parser_img.set_defaults(function_name=img)
    # Create the parser for the "init" subcommand
    parser_init = subparsers.add_parser(
            "init", description=argparse["_parser_init"],
            help=argparse["_parser_init"])
    parser_init.set_defaults(function_name=init)
    if len(argv) == 1:
        parser.print_help()
        exit(0) # Clean exit without any errors/problems
    return parser.parse_args()
