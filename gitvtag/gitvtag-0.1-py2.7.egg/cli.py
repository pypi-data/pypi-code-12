from __future__ import print_function

import optparse, subprocess, sys
import Git

class SyntaxError(Exception):
  pass

class CLI:
  def __init__(self):
    parser = optparse.OptionParser(usage="""
    git vtag get|set|status [<args>] [options]

    set [<version>]  -- tag the latest commit with <version>,
                        if <version> was not specified, tag with the next version
    get last | next  -- find and print last or next version. 'last' is default
    status           -- print the version status of the current directory
    """)
    parser.set_defaults(check_clean= True, allow_duplicate= False)
    parser.add_option("-c", "--check-clean",
                      action="store_true", dest="check_clean",
                      help="check if there are uncommitted changes")
    parser.add_option("-d", "--dont-check-clean",
                      action="store_false", dest="check_clean",
                      help="don't check for uncommitted changes")
    parser.add_option("-u", "--allow-duplicate",
                      action="store_true", dest="allow_duplicate",
                      help="allow duplicate version tags for the same commit")
    parser.add_option("-n", "--dont-allow-duplicate",
                      action="store_false", dest="allow_duplicate",
                      help="uNique. do not allow duplicate version tags")
    self._parser= parser
    self._git= Git.Git()

  def run(self):
    try:
      (options, args) = self._parser.parse_args()
      if len(args)==0:
        raise SyntaxError("no arguments specified")
      command= args[0]
      if command=="get":
        print(self._get(args[1] if len(args)>1 else "last"))
      elif command=="set":
        return self._set(args[1] if len(args)>1 else None, options)
      elif command=="status":
        self._status()
      else:
        raise SyntaxError("unknown argument", {"arg": command})
      return 0
    except SyntaxError as err:
      print("Syntax error: " + str(err) + "\n", file=sys.stderr)
      self._parser.print_usage(file=sys.stderr)
      return -1
    except subprocess.CalledProcessError as err:
      print(err, file=sys.stderr)

  def _get(self, sub):
    if sub=="last":
      return self._git.last_tag()
    elif sub=="next":
      return self._git.next_tag()
    else:
      raise SyntaxError("unknown argument", {"arg": sub})

  def _set(self, tag, options):
    status= self._git.tag_status()
    if options.check_clean and status.dirty:
      print("The repository has uncommitted changes. Please commit first",
            file=sys.stderr)
      return 1
    if (not options.allow_duplicate) and (not status.has_untagged_commits):
      print("The repository already has tag: " + status.last_tag, file=sys.stderr)
      return 1
    if tag:
      if not self._git.valid_tag(tag):
        raise SyntaxError('tag should be in format: vNNN.NNN..', {"actual": tag })
      self._git.tag(tag)
    else:
      next= self._git.next_tag()
      print(next, file=sys.stdout)
      self._git.tag(next)
    return 0

  def _status(self):
    status= self._git.tag_status()
    print("dirty:", status.dirty)
    print("last_tag:", status.last_tag)
    print("has_untagged_commits:", status.has_untagged_commits)
    if status.has_untagged_commits and status.untagged_commits > 0:
      print("number_of_untagged_commits:", status.untagged_commits)

def cli():
  CLI().run()

if __name__=="__main__":
  cli()

