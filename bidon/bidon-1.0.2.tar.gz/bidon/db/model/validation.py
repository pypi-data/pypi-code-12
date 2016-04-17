"""The validation module contains the Validation and Validator classes."""
import bidon.util as util


__all__ = ["Validation", "Validator"]


class Validation(object):
  """A simple validation mechanism, designed for use by bidon.db.model.ModelBase."""
  def __init__(self, callback, property_name=None, message=None, *, is_simple=True,
               is_property_specific=True):
    """
    Initializes the Validation instance.

    :is_simple: when True the validation requires no outside information to process, if False,
    outside information (such as a database connection) is required.
    :is_property_specific: when True, the value of the property under question is passed to the
    validation callback, when false the entire model is passed.
    """
    self.property_name = property_name
    self.callback = callback
    self.message = message
    self.is_simple = is_simple
    self.filters = []
    self.pretty_property_name = None
    self.is_property_specific = is_property_specific

  def add_filter(self, filter_):
    """Filters are methods that accept a model and return True if the model should be validated or
    False if it should not. This makes it possible to exempt models from validations when
    necessary.
    """
    self.filters.append(filter_)
    return self

  def set_pretty_property_name(self, ppn):
    """Set the pretty property name for the validation and return the validation instance."""
    self.pretty_property_name = ppn
    return self

  def is_valid(self, model, validator=None):
    """Returns true if the model passes the validation, and false if not. Validator must be
    present_optional if validation is not 'simple'.
    """
    if self.property_name and self.is_property_specific:
      arg0 = getattr(model, self.property_name)
    else:
      arg0 = model

    if self.is_simple:
      is_valid = self.callback(arg0)
    else:
      is_valid = self.callback(arg0, validator)

    return (is_valid, None if is_valid else (self.message or "is invalid"))

  def validate(self, model, validator=None):
    """Checks the model against all filters, and if it shoud be validated, runs the validation. if
    the model is invalid, an error is added to the model. Then the validity value is returned.
    """
    for filter_ in self.filters:
      if not filter_(model):
        return True

    is_valid, message = self.is_valid(model, validator)
    if not is_valid:
      model.add_error(self.pretty_property_name or self.property_name, message)
    return is_valid

  @staticmethod
  def _is_present(val):
    """Returns True if the value is not None, and if it is either not a string, or a string with
    length > 0.
    """
    if val is None:
      return False
    if isinstance(val, str):
      return len(val) > 0
    return True

  @staticmethod
  def is_present(property_name):
    """Returns a Validation that returns false when the property is None or an empty string."""
    return Validation(Validation._is_present, property_name, "cannot be blank")

  @staticmethod
  def is_length(property_name, *, min_length=1, max_length=None, present_optional=False):
    """Returns a Validation that checks the length of a string."""
    def check(val):
      """Checks that a value matches a scope-enclosed set of length parameters."""
      if not val:
        return present_optional
      else:
        if len(val) >= min_length:
          if max_length is None:
            return True
          else:
            return len(val) <= max_length
        else:
          return False

    if max_length:
      message = "must be at least {0} characters long".format(min_length)
    else:
      message = "must be between {0} and {1} characters long".format(min_length, max_length)

    return Validation(check, property_name, message)

  @staticmethod
  def matches(property_name, regex, *, present_optional=False, message=None):
    """Returns a Validation that checks a property against a regex."""
    def check(val):
      """Checks that a value matches a scope-enclosed regex."""
      if not val:
        return present_optional
      else:
        return True if regex.search(val) else False

    return Validation(check, property_name, message)

  @staticmethod
  def is_numeric(property_name, *, numtype="float", min=None, max=None,
                 present_optional=False, message=None):
    """Returns a Validation that checks a property as a number, with optional range constraints."""
    if numtype == "int":
      cast = util.try_parse_int
    elif numtype == "decimal":
      cast = util.try_parse_decimal
    elif numtype == "float":
      cast = util.try_parse_float
    else:
      raise ValueError("numtype argument must be one of: int, decimal, float")

    def check(val):
      """Checks that a value can be parsed as a number."""
      if val is None:
        return present_optional
      else:
        is_num, new_val = cast(val)
        if not is_num:
          return False
        else:
          if min is not None and new_val < min:
            return False
          if max is not None and new_val > max:
            return False
          return True

    if not message:
      msg = ["must be a"]
      if numtype == "int":
        msg.append("whole number")
      else:
        msg.append("number")
      if min is not None and max is not None:
        msg.append("between {0} and {1}".format(min, max))
      elif min is not None:
        msg.append("greater than or equal to {0}".format(min))
      elif max is not None:
        msg.append("less than or equal to {0}".format(max))
      message = " ".join(msg)

    return Validation(check, property_name, message)

  @staticmethod
  def is_date(property_name, *, format=None, present_optional=False, message=None):
    """Returns a Validation that checks a value as a date."""
    # NOTE: Not currently using format param
    def check(val):
      """Checks that a value can be parsed as a date."""
      if val is None:
        return present_optional
      else:
        is_date, _ = util.try_parse_date(val)
        return is_date

    return Validation(check, property_name, message)

  @staticmethod
  def is_datetime(property_name, *, format=None, present_optional=False, message=None):
    """Returns a Validation that checks a value as a datetime."""
    # NOTE: Not currently using format param
    def check(val):
      """Checks that a value can be parsed as a datetime."""
      if val is None:
        return present_optional
      else:
        is_date, _ = util.try_parse_datetime(val)
        return is_date

    return Validation(check, property_name, message)

  @staticmethod
  def is_in(property_name, set_values, *, present_optional=False, message=None):
    """Returns a Validation that checks that a value is contained within a given set."""
    def check(val):
      """Checks that a value is contained within a scope-enclosed set."""
      if val is None:
        return present_optional
      else:
        return val in set_values

    return Validation(check, property_name, message)

  @staticmethod
  def is_unique(keys, *, scope=None, comparison_operators=None, present_optional=False,
                message=None):
    """Returns a Validation that makes sure the given value is unique for a table and optionally a
    scope.
    """
    def check(pname, validator):
      """Checks that a value is unique in its column, with an optional scope."""
      # pylint: disable=too-many-branches
      model = validator.model
      data_access = validator.data_access
      pkname = model.primary_key_name
      pkey = model.primary_key

      if isinstance(keys, str):
        key = getattr(model, keys)

        if present_optional and key is None:
          return True

        if comparison_operators:
          if isinstance(comparison_operators, str):
            op = comparison_operators
          else:
            op = comparison_operators[0]
        else:
          op = " = "

        constraints = [(keys, key, op)]
      else:
        if comparison_operators:
          ops = comparison_operators
        else:
          ops = [" = "] * len(keys)

        constraints = list(zip(keys, [getattr(model, key) for key in keys], ops))

      if scope:
        if comparison_operators:
          ops = comparison_operators[len(constraints):]
        else:
          ops = [" = "] * len(scope)

        constraints.extend(zip(scope, [getattr(model, col) for col in scope], ops))

      dupe = data_access.find(model.table_name, constraints, columns=pkname)

      if dupe is None:
        return True
      if isinstance(pkname, str):
        return dupe[0] == pkey
      else:
        return tuple(dupe) == tuple(pkey)

    return Validation(check, keys, message or "is already taken", is_simple=False)


class Validator(object):
  """The Validator class holds a collection of validations and methods to work with them."""
  def __init__(self, validations=None, *, fail_fast=False):
    """Initializes the Validator instance."""
    self.validations = validations or []
    self.model = None
    self.data_access = None
    self.fail_fast = fail_fast

  def add(self, validation):
    """Adds a Validation to the collection."""
    self.validations.append(validation)

  def validate(self, model, data_access=None, *, fail_fast=None):
    """Validates a model against the collection of Validations.

    Returns True if all Validations pass, or False if one or more do not.
    """
    if fail_fast is None:
      fail_fast = self.fail_fast

    self.model = model
    self.data_access = data_access
    is_valid = True
    for validation in self.validations:
      if not validation.validate(model, self):
        is_valid = False
        if fail_fast:
          break
    return is_valid
