from collections import deque
from copy import deepcopy

from toposort import toposort_flatten

from buildorchestra.result import BuildResult
from buildorchestra.steps import BuildStep, TargetStep


class Builder(object):
  def __init__(self, copyOptions=True, dependencyAnalysis=True):
    self.copyOptions = copyOptions
    self.dependencyAnalysis = dependencyAnalysis
    self.steps = {}
    self.deps = {}

  def add_build_step(self, identifier, depIds, method):
    if identifier in self.steps:
      raise RuntimeError('Step or target with identifier {} already exists'.format(identifier))
    self.steps[identifier] = BuildStep(identifier, method)
    if identifier in self.deps:
      self.deps[identifier].update(depIds)
    else:
      self.deps[identifier] = set(depIds)
    return identifier

  def add_target(self, identifier, depIds):
    if identifier in self.steps:
      raise RuntimeError('Step or target with identifier {} already exists'.format(identifier))
    self.steps[identifier] = TargetStep(identifier)
    if identifier in self.deps:
      self.deps[identifier].update(depIds)
    else:
      self.deps[identifier] = set(depIds)
    return identifier

  def build(self, *targets, **options):
    if not targets: return

    stepIdsToExecute = set()
    if self.dependencyAnalysis:
      for target in targets:
        if target not in self.steps:
          raise RuntimeError('Target {} does not exist'.format(target))
        transClosureIds = self.__get_transitive_closure_ids(target)
        stepIdsToExecute.update(transClosureIds)
      stepIdsDepGraph = {stepId: self.__get_dep_ids(stepId) for stepId in stepIdsToExecute}
    else:
      stepIdsToExecute.update(targets)
      stepIdsDepGraph = {stepId: {depId for depId in self.__get_dep_ids(stepId) if depId in targets} for stepId in
                         stepIdsToExecute}

    stepIdsBuildOrder = toposort_flatten(stepIdsDepGraph)
    stepsBuildOrder = [self.__resolve_step(stepId) for stepId in stepIdsBuildOrder]

    print('Executing build steps: {}'.format(', '.join(stepIdsBuildOrder)))

    artifacts = []
    for step in stepsBuildOrder:
      if step.shouldExecute:
        if self.copyOptions:
          stepOptions = deepcopy(options)
        else:
          stepOptions = options
        print('Executing build step {}'.format(step))
        result = step.execute(**stepOptions)
        print('Executing build step {} completed'.format(step))
        if result:
          for artifact in result.artifacts:
            print('  Produced artifact {}'.format(artifact))
            artifacts.append(artifact)
    print('All done!')

    if artifacts:
      print('Produced artifacts:')
      for artifact in artifacts:
        print('Artifact {}'.format(artifact))

    return BuildResult(artifacts)

  @property
  def all_steps(self):
    return self.steps.keys()

  @property
  def all_steps_ordered(self):
    graph = {stepId: self.__get_dep_ids(stepId) for stepId in self.all_steps}
    ordered = toposort_flatten(graph)
    return ordered

  def __get_transitive_closure_ids(self, startId):
    transClosure = set()
    queue = deque()
    queue.append(startId)
    while queue:
      identifier = queue.popleft()
      transClosure.add(identifier)
      depIds = self.__get_dep_ids(identifier)
      for depId in depIds:
        if depId not in transClosure:
          queue.append(depId)
    return transClosure

  def __get_dep_ids(self, stepId):
    depIds = set()
    if stepId not in self.deps:
      return depIds
    return self.deps[stepId]

  def __resolve_step(self, stepId):
    if stepId not in self.steps:
      raise RuntimeError('Step {} does not exist'.format(stepId))
    return self.steps[stepId]
