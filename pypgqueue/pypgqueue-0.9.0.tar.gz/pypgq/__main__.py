"""This script handles command-line invocations of the package."""
import argparse
import logging
import os
import signal
import sys
from importlib.machinery import SourceFileLoader

from bidon.db.access import ModelAccess
from bidon.db.core import get_pg_core

from pypgq.queue import Cooperative, Queue, StopMode


STOP_SIGNALS = {
  signal.SIGHUP: StopMode.when_all_done,
  signal.SIGINT: StopMode.when_current_done,
  signal.SIGTERM: StopMode.now
}


def main():
  """Entry point for module being run as main."""
  args = parse_args()

  if args is None:
    return

  if args.action == "schema":
    print(get_ddl(args.schema_name, args.is_95))
  elif args.action == "start":
    coop = parse_cooperative(args.coop_mode, args.coop_arg)
    is_parent = True
    children = []
    qcount = args.queues

    if coop.mode == Cooperative.none and qcount > 1:
      raise Exception("You must provide a cooperative mode if launching "
                      "multiple queue processes")

    while qcount > 1:
      pid = os.fork()
      if pid == 0:
        is_parent = False
        break
      else:
        children.append(pid)
      qcount -= 1

    start_queue(args.connection_string,
                args.job_filepath,
                args.schema_name,
                args.workers,
                args.pid_filepath if is_parent else None,
                coop,
                args.job_args,
                children if is_parent else None)

  elif args.action == "stop":
    stop_queue(args.pid_filepath, args.stop_mode)
  elif args.action == "status":
    query_queue(args.pid_filepath)
  else:
    raise Exception("Unhandled subcommand: {}".format(args.action))


def parse_args():
  """Parses command line arguments."""
  fcls = argparse.ArgumentDefaultsHelpFormatter
  apar = argparse.ArgumentParser(prog="python3 -m pypgq", description="PyPGQ", formatter_class=fcls)
  spar = apar.add_subparsers()

  schema_cmd = spar.add_parser("schema", help="Write the PyPGQ DDL to STDOUT", formatter_class=fcls)
  schema_cmd.add_argument("schema_name",
                          default="public",
                          nargs="?",
                          help="The name of the schema to contain the job tables")
  schema_cmd.add_argument("--is-95",
                          default=False,
                          action="store_true",
                          help="If the Postgres version is 9.5+ pass this flag to enable some "
                               "features")
  schema_cmd.set_defaults(action="schema")

  start_cmd = spar.add_parser("start",
                              help="Run a job queue with jobs handlers assigned and logging "
                                   "configured in the file at --jobfile-path",
                              formatter_class=fcls)
  start_cmd.add_argument("-c",
                         "--connection-string",
                         required=True,
                         help="A postgres connection string for the database holding the job "
                              "tables")
  start_cmd.add_argument("-f",
                         "--job-filepath",
                         required=True,
                         help="The path to a python script that will assign handlers to the queue. "
                              "If the path is a directory, then the directory's parent will be "
                              "added to sys.path, and path/__init__.py will be loaded")
  start_cmd.add_argument("-a",
                         "--job-args",
                         help="A string argument to pass as the second parameter to the setup_jobs "
                              "function defined in job_filepath")
  start_cmd.add_argument("-s",
                         "--schema-name",
                         default="public",
                         help="The name of the schema that holds the job tables")
  start_cmd.add_argument("-q",
                         "--queues",
                         default=1,
                         type=int,
                         help="The number of queue processes to launch. Each queue beyond the "
                              "first will be launched in a child process")
  start_cmd.add_argument("-w",
                         "--workers",
                         default=10,
                         type=int,
                         help="The number of workers to spawn for each queue. So if this value is "
                              "5 and you have 1 queue, there will be 5 workers total. If 2 queues "
                              "then 10 workers total, etc")
  start_cmd.add_argument("-p",
                         "--pid-filepath",
                         default=None,
                         help="The file to write the PID of the main queue. This is needed if you "
                              "want to daemonize the queue and use the stop cmd")
  start_cmd.add_argument("--coop-mode",
                         default=None,
                         choices={"none", "advisory_lock", "row_lock"},
                         help="The cooperative mode to run the queues in")
  start_cmd.add_argument("--coop-arg",
                         default=None,
                         help="The arg for the cooperative mode. If the coop mode is advisory_lock "
                              "you need to provide either a big int, or a pair of integers "
                              "separated by a comma for the advisory lock key")
  start_cmd.set_defaults(action="start")

  stop_cmd = spar.add_parser("stop",
                             help="Stop a job queue whose pid is listed in pid-filepath",
                             formatter_class=fcls)
  stop_cmd.add_argument("-p", "--pid-filepath", required=True)
  stop_cmd.add_argument("-m",
                        "--stop-mode",
                        default="current",
                        choices={"all", "current", "now"})
  stop_cmd.set_defaults(action="stop")

  status_cmd = spar.add_parser("status",
                               help="Write the queue status to STDERR of the terminal that the "
                                    "queue is attached to",
                               formatter_class=fcls)
  status_cmd.add_argument("-p", "--pid-filepath", required=True)
  status_cmd.set_defaults(action="status")


  args = apar.parse_args()

  if not hasattr(args, "action"):
    apar.print_usage()
    return None
  return args


def get_ddl(schema_name, skip_locked=True):
  """Prints the DDL to STDOUT.

  :schema_name: The schema to place the objects in
  """
  path = os.path.dirname(__file__)
  file = os.path.join(path, "ddl.sql")

  params = dict(SCHEMA_NAME=schema_name, SKIP_LOCKED=" skip locked" if skip_locked else "")
  with open(file, "r") as rf:
    sql_fmt = rf.read()

  return sql_fmt.format(**params)


def start_queue(connection_string, job_filepath, schema_name="public", workers=10,
                pid_filepath=None, cooperative=None, job_args=None, children=None):
  """Creates, configures and runs a job queue.

  :param connection_string: a Postgres connection string
  :param job_filepath: the path to a python script that can configure the queue
  :param schema_name: the name of the schema that contains the queue tables
  :param workers: the number of concurrent workers to run
  """
  model_access = ModelAccess(get_pg_core(connection_string),
                             search_path=schema_name)
  model_access.open(autocommit=True)
  queue = Queue(model_access,
                worker_count=workers,
                cooperative=cooperative)
  job_module = load_module(job_filepath, None)
  job_module.setup_jobs(queue, job_args)

  def stop(sig, _):
    """Stops the queue in the manner specified by the signal.

    :param sig: the signal receieved
    """
    queue.stop(stop_mode=STOP_SIGNALS[sig])
    if children:
      for pid in children:
        os.kill(pid, sig)
        try:
          os.waitpid(pid, 0)
        except ChildProcessError:
          # Child already shut down before we started waiting on it.
          pass

  for sig in STOP_SIGNALS:
    signal.signal(sig, stop)
  signal.signal(signal.SIGINFO, lambda n, f: print(queue.status(), file=sys.stderr))

  log_queue_info(job_filepath, workers)

  if pid_filepath:
    write_pidfile(pid_filepath)

  queue.start()


def parse_cooperative(coop_mode, coop_arg):
  """Parses the coop command line args into a Cooperative class instance.

  :param coop_mode: a string matchng one of the coop mode types
  :param coop_arg: a string that can be parsed into a coop arg
  """
  if coop_mode is None or coop_mode == "none":
    mode = Cooperative.none
  elif coop_mode == "advisory_lock":
    mode = Cooperative.advisory_lock
  elif coop_mode == "row_lock":
    mode = Cooperative.row_lock
  else:
    mode = Cooperative.none

  if coop_arg is None:
    arg = None
  else:
    if coop_arg.find(",") >= 0:
      key0, key1 = coop_arg.split(",", 1)
      arg = (int(key0.strip()), int(key1.strip()))
    else:
      arg = int(coop_arg)

  return Cooperative(mode, arg)


def stop_queue(pid_filepath, mode=None):
  """Sends a kill signal to the queue running under the pid found written in the
  pid file.

  :param pid_filepath: the path to the pid file
  :param mode: the stop mode. one of: "now", "all", "current"
  """
  pid = read_pidfile(pid_filepath)

  if mode == "now":
    sig = signal.SIGTERM
  elif mode == "all":
    sig = signal.SIGHUP
  else:
    sig = signal.SIGINT

  os.kill(pid, sig)
  os.remove(pid_filepath)


def query_queue(pid_filepath):
  """Sends the SIGINFO signal to the queue running under the pid found written
  in the pid file.

  :param pid_filepath: the path to the pid file
  """
  pid = read_pidfile(pid_filepath)

  os.kill(pid, signal.SIGINFO)


def log_queue_info(job_filepath, workers):
  """Writes startup info about the queue to the queue log."""
  pid = os.getpid()
  log("Queue config:\n"
      "  pid: {pid}\n"
      "  job_file: {job_file}\n"
      "  workers: {workers}".format(
        pid=pid,
        job_file=job_filepath,
        workers=workers))
  log("To stop or query the queue, send a signal:\n"
      "  kill -HUP {pid} #stop the queue when there are no more waiting jobs\n"
      "  kill -INT {pid} #stop the queue when the currently running jobs are done\n"
      "  kill -TERM {pid} #cancel all running jobs and stop the queue asap\n"
      "  kill -INFO {pid} #print the current queue status to the queue process' STDERR".format(
        pid=pid))


def write_pidfile(filepath):
  """Writes the process pid to the filepath. If the file exists an error is
  raised.

  :param filepath: the path to write the pid
  """
  if os.path.exists(filepath):
    raise Exception("Unable to write pid file. It already exists")

  with open(filepath, "w") as wf:
    wf.write(str(os.getpid()))


def read_pidfile(filepath):
  """Reads the pid from the contents of the file at filepath.

  :param filepath: the path to the file
  """
  with open(filepath, "r") as rf:
    return int(rf.read().strip())


def load_module(path, name):
  """Returns a loaded module from path. If path is a direectory, then the parent directory is added
  to the path, and name/__init__.py is loaded and that module returned.

  :param path: the path to the directory containing the init file or to a python file
  :param name: the name to assign the module
  """
  if os.path.isdir(path):
    mod_root, mod_name = os.path.split(path)
    filename = os.path.join(path, "__init__.py")
    sys.path.insert(0, mod_root)
    return SourceFileLoader(name or mod_name, filename).load_module()
  else:
    return SourceFileLoader(name or "__loaded_module__", path).load_module()


def log(msg):
  """Writes a message to the queue log."""
  logging.getLogger("pypgq").info(msg)


if __name__ == "__main__":
  main()
