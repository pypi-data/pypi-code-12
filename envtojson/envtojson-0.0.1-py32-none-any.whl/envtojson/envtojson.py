#!/usr/bin/env python3
import argparse
import json
import os
import pprint


class Envtojson:
    def __init__(self, filename, var_names=[], quiet=False):
        self.validate(filename)
        self.var_names = var_names if var_names else []
        self.filepath = os.path.join(os.getcwd(), filename)
        self.quiet = quiet

    def validate(self, filename):
        if not filename:
            raise Exception('need to specify filename to write to')

    def createOrLoadDict(self):
        # if JSON file already exists then decorate the JSON in it
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as out:
                self.envs_dict = json.load(out)
        else:
            self.envs_dict = {}

    def writeVarsToDict(self):
        for var_name in self.var_names:
            try:
                self.envs_dict[var_name] = os.environ[var_name]
            except Exception:
                print('missing env var: %s' % var_name)
            finally:
                pass

    def writeVarsToFile(self):
        with open(self.filepath, 'w') as out:
            json.dump(self.envs_dict, out)

    def printResult(self):
        if self.quiet is not True:
            print('')
            print('Env vars written to: %s:\n' % self.filepath)
            pprint.pprint(self.envs_dict)
            print('')

    def run(self):
        self.createOrLoadDict()
        self.writeVarsToDict()
        self.writeVarsToFile()
        self.printResult()


def main():
    parser = argparse.ArgumentParser(
        description='Write shell environment variables to a file in JSON.'
    )
    parser.add_argument('filename', type=str, help='file to write to')
    parser.add_argument('vars', nargs='+', type=str)
    parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    envtojson = Envtojson(args.filename, args.vars, args.quiet)
    envtojson.run()

if __name__ == '__main__':
    main()
