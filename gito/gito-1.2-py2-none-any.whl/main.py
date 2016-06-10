import argparse
import todo
import validation
import config


def execute():
    parser = argparse.ArgumentParser(
        description="Gito - Command Line Utility to Print "
                    "TODO`s in source files & upload to wunderlist")
    parser.add_argument('--wsync', help='Sync the TODO`s to wunderlist',
                        action="store_true")
    parser.add_argument('--display', help='Display all the TODO`s',
                        action="store_true")
    parser.add_argument('--initconfig',
                        help='Init Gito Configuration file under home',
                        action="store_true")
    parser.add_argument('--version',
                        help='Prints version',
                        action="store_true")
    args = parser.parse_args()

    if args.wsync:
        # Running validations
        validation.wunderlist_validation()

        # Starting wunderlist upload
        print 'Uploading tasks to Wunderlist:'
        todo_ob = todo.GiTo()
        todo_ob.upload_todos()

    elif args.display:
        todo_ob = todo.GiTo()
        todo_ob.print_todo()
    elif args.initconfig:
        config.init_config()
    elif args.version:
        print "1.2"
    else:
        parser.print_help()


if __name__ == "__main__":
    execute()
