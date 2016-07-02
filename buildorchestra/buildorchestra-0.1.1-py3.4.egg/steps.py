from abc import ABCMeta, abstractmethod


class Step(metaclass=ABCMeta):
  @property
  @abstractmethod
  def identifier(self): pass

  @property
  @abstractmethod
  def shouldExecute(self): True

  @abstractmethod
  def execute(self, **options): pass

  def __eq__(self, other): return self.identifier == other.identifier

  def __lt__(self, other): return self.identifier < other.identifier

  def __hash__(self): return hash(self.identifier)

  def __repr__(self): return self.identifier


class BuildStep(Step):
  def __init__(self, identifier, method):
    self._identifier = identifier
    self._method = method

  @property
  def identifier(self): return self._identifier

  @property
  def shouldExecute(self): return True

  def execute(self, **options):
    return self._method(**options)


class TargetStep(Step):
  def __init__(self, identifier):
    self._identifier = identifier

  @property
  def identifier(self): return self._identifier

  @property
  def shouldExecute(self): return False

  def execute(self, **options): pass
