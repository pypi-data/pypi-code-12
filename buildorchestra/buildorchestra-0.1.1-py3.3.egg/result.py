import os
import shutil


class BuildResult:
  def __init__(self, artifacts):
    self.artifacts = artifacts

  def copy_to(self, destDir):
    os.makedirs(destDir, exist_ok=True)
    for artifact in self.artifacts:
      artifact.copy_to(destDir)


class StepResult:
  def __init__(self, artifacts):
    self.artifacts = artifacts

  def copy_to(self, destDir):
    os.makedirs(destDir, exist_ok=True)
    for artifact in self.artifacts:
      artifact.copy_to(destDir)


class Artifact:
  def __init__(self, name, location, target):
    self.name = name
    self.location = location
    self.target = target

  def __str__(self):
    return '"{}" at {}'.format(self.name, self.location)

  def copy_to(self, destDir):
    copyLocation = os.path.join(destDir, self.target)
    print('Copying artifact {} to {}'.format(self, copyLocation))
    shutil.copyfile(self.location, copyLocation)
