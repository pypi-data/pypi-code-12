# encoding: UTF-8

import os, re, json, yaml, textwrap
import config

class Comfortable(object):

  def mktemp(self, filename, content = None):
    # touch filename
    if content is None:
      open(filename, 'w').close()
      return
    open(filename, 'w').write(content).close()

  def rmtemp(self, temp):
    os.remove(temp)

  def prepare(self, testcase):
    data = ''
    with open(testcase, 'r') as f:
      data = f.read()
    m = re.match(r"\/\+\s(.+)\+\/\s(.+)", data, re.DOTALL)
    if not m:
      raise Exception('testcase format does not correct.')
    dedented = textwrap.dedent(m.groups()[0].strip())
    invoke = yaml.load(dedented).get('invoke')
    playbook = config.from_data(dedented, invoke)
    expected = m.groups()[1].strip()
    return (playbook, expected)

  def get_testcases(self, dirname):
    basedir = os.path.join(os.path.dirname(__file__), dirname)
    return [os.path.join(basedir, filename) \
      for filename in os.listdir(basedir) if re.match(r"^test", filename)]

  def to_json(self, stacks):
    return json.dumps(stacks, default = lambda x: x.__dict__, sort_keys=True, indent=2)

  def info(self, actual, expect):
    print("- actual")
    print(actual)
    print("- expect")
    print(expect)
