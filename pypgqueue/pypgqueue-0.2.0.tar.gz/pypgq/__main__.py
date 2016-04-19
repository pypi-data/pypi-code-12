"""This script handles command-line invocations of the package."""
import os
from argparse import ArgumentParser


def main():
  """Entry point for module being run as main."""
  args = parse_args()
  print(get_ddl(args.schema_name))


def parse_args():
  """Parses command line arguments."""
  apar = ArgumentParser(description="PyPGQ helper")
  apar.add_argument("schema_name",
                    default="public",
                    nargs="?",
                    help="The name of the schema to contain the job tables")
  return apar.parse_args()


def get_ddl(schema_name):
  """Prints the DDL to STDOUT.

  :schema_name: The schema to place the objects in
  """
  path = os.path.dirname(__file__)
  file = os.path.join(path, "ddl.sql")
  params = dict(SCHEMA_NAME=schema_name)
  with open(file, "r") as rf:
    sql_fmt = rf.read()

  return sql_fmt.format(**params)


if __name__ == "__main__":
  main()
