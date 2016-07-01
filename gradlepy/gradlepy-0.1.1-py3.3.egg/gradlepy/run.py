import os
import subprocess
from shutil import which


class Gradle(object):
  def __init__(self):
    self.useWrapper = True
    self.fallbackToInstalled = True

    self.targets = []
    self.properties = {}
    self.extraArgs = []

    self.settingsFile = None
    self.mavenLocalRepo = None

    self.offline = False

    self.debug = False
    self.stacktrace = False
    self.info = False
    self.quiet = False

    self.noNative = False

    self.env = {}

  def run_in_dir(self, cwd, *extraTargets, **extraProperties):
    self.run(cwd, None, *extraTargets, **extraProperties)

  def run_on_file(self, buildFile, *extraTargets, **extraProperties):
    self.run(None, buildFile, *extraTargets, **extraProperties)

  def run(self, cwd, buildFile, *extraTargets, **extraProperties):
    args = []

    if self.useWrapper:
      searchPath = cwd or os.getcwd()
      path = which('gradlew', path=searchPath) or which('gradlew')
      if not path and self.fallbackToInstalled:
        path = which('gradle')
    else:
      path = which('gradle')

    if path:
      args.append(path)
    else:
      raise RuntimeError("Cannot run Gradle, executable not found on the path")

    # Must occur before --data-file, for some reason. Gradle bug?
    if self.noNative:
      # Based on this: https://github.com/adammurdoch/native-platform/issues/6#issuecomment-41315984
      args.append('-Dorg.gradle.native=false')

    if buildFile:
      args.append('--data-file "{}"'.format(buildFile))

    if self.settingsFile:
      args.append('--settings-file "{}"'.format(self.settingsFile))
    if self.mavenLocalRepo:
      args.append('-Dmaven.repo.local={}'.format(self.mavenLocalRepo))

    if self.offline:
      args.append('--offline')

    if self.debug:
      args.append('--debug')
    if self.stacktrace:
      args.append('--stacktrace')
    if self.info:
      args.append('--info')
    if self.quiet:
      args.append('--quiet')

    allProperties = {}
    allProperties.update(self.properties)
    allProperties.update(extraProperties)
    for name, value in allProperties.items():
      args.append('-D{}={}'.format(name, value))

    allTargets = []
    allTargets.extend(self.targets)
    allTargets.extend(extraTargets)
    args.extend(allTargets)

    if self.extraArgs:
      args.extend(self.extraArgs)

    env = os.environ.copy()
    env.update(self.env)

    cmd = ' '.join(args)
    print(cmd)
    try:
      process = subprocess.Popen(cmd, cwd=cwd, env=env, shell=True)
      process.communicate()
      if process.returncode != 0:
        raise RuntimeError("Gradle run failed")
    except KeyboardInterrupt:
      raise RuntimeError("Gradle run interrupted")
