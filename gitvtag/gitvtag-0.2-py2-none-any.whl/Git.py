import re, subprocess
from os import path

VERSION_PATTERN= "v[0-9]*"

class Git:
  def __init__(self, repo=".", rel=None, show_commands= False):
    if rel:
      if not path.isdir(rel):
        rel= path.dirname(rel)
      repo= path.join(rel, repo)
    self._repo= path.abspath(repo)
    self._show_commands= show_commands

  def last_tag(self):
    status= self.tag_status()
    return status.last_tag

  def next_tag(self):
    return self.increment_tag(self.last_tag())

  def tag(self, tag_value, message=""):
    subprocess.check_call(self._show(["git", "tag",  "-a", tag_value, "--message=" + message]))

  def push_tags(self):
    subprocess.check_call(self._show(["git", "push",  "origin", "HEAD", "--tags"]))

  def _show(self, command):
    if self._show_commands:
      print("> " + " ".join(command))
    return command

  LAST_COMPONENT= re.compile("^(v.*[.]?)(\d+)(.*)$")

  def valid_tag(self, tag):
    return bool(Git.LAST_COMPONENT.match(tag))

  def increment_tag(self, tag):
    m= Git.LAST_COMPONENT.match(tag)
    if not m:
      raise ValueError("invalid tag format", {"value": tag})
    return m.group(1) + str(int(m.group(2)) + 1) + m.group(3)

  def has_uncommited_changes(self):
    return bool(subprocess.check_output(["git", "status", "--porcelain"]))

  class TagStatus:
    def __init__(self, report):
      if report:
        split= report.split("-")
        self.last_tag= split[0]
        self.untagged_commits= int(split[1])
        self.has_untagged_commits= self.untagged_commits > 0
        self.dirty= len(split) > 3
      else:
        self.last_tag= None
        self.dirty= None
        self.has_untagged_commits= True
        self.untagged_commits= -1

  def tag_status(self):
    # `git describe --match v[0-9]* --tags --long --dirty=-`
    try:
      report= subprocess.check_output(["git", "describe",  "--match", VERSION_PATTERN, "--tags", "--long", "--dirty=-"],
                                      stderr= subprocess.STDOUT)
      return Git.TagStatus(report)
    except subprocess.CalledProcessError:
      result= Git.TagStatus(None)
      result.dirty= self.has_uncommited_changes()
      return result

  def has_untagged_commits(self):
    # credit: http://stackoverflow.com/a/12083016/130228
    return bool(subprocess.check_output(["git", "log", "{0}..HEAD".format(self.last_tag()), "--oneline"]))

