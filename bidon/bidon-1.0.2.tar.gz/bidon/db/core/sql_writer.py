"""The sql_writer module contains the SqlWriter class."""
import operator
import re


__all__ = ["SqlWriter"]


class SqlWriter(object):
  """This class writes SQL format strings, it can be customized for different driver conventions for
  placeholders and different typecaster conventions for databases.
  """
  def __init__(self, named_placeholder, unnamed_placeholder, typecaster, *, sort_columns=False):
    """Construct the instance.

    :named_placeholder: must be a format string accepting a single item.
    :unnamed_placeholder: must be a string.
    :typecaster: must be a format string accepting two items: a subject and a db type.
    """
    self.named_placeholder = named_placeholder
    self.unnamed_placeholder = unnamed_placeholder
    self.typecaster = typecaster
    self.sort_columns = sort_columns

  def typecast(self, subject, db_type):
    """Applys subject and db_type to the instance's typecaster format string."""
    return self.typecaster.format(subject, db_type)

  def to_placeholder(self, name=None, db_type=None):
    """Returns a placeholder for the specified name, by applying the instance's format strings.

    :name: if None an unamed placeholder is returned, otherwise a named placeholder is returned.
    :db_type: if not None the placeholder is typecast.
    """
    if name is None:
      placeholder = self.unnamed_placeholder
    else:
      placeholder = self.named_placeholder.format(name)

    if db_type:
      return self.typecast(placeholder, db_type)
    else:
      return placeholder

  def to_tuple(self, iterable, surround="()", joiner=", "):
    """Returns the iterable as a SQL tuple."""
    return "{0}{1}{2}".format(surround[0], joiner.join(iterable), surround[1])

  def to_expression(self, lhs, rhs, op):
    """Builds a binary sql expression.

    At its most basic, returns 'lhs op rhs' such as '5 + 3'. However, it also specially handles the
    'in' and 'between' operators. For each of these operators it is expected that rhs will be
    iterable.

    If the comparison operator is of the form 'not(op)' where op is the operator, it will result in
    not (lhs op rhs).

    This allows for doing the full range of null checks on composite types. For composite types,
    'is null' only returns true when all fields are null, and 'is not null' returns true only when
    all fields are not null. So, for a composite type with some null fields, 'is null' and
    'is not null' will both return false, making it difficult to get all rows that have composite
    columns with some value in them. The solution to this is to use not (composite is null) which
    is true when all composite fields, or only some composite fields are not null.
    """
    if op == "raw":
      # TODO: This is not documented
      return lhs
    elif op == "between":
      return "{0} between {1} and {2}".format(lhs, *rhs)
    elif op == "in":
      return "{0} in {1}".format(lhs, self.to_tuple(rhs))
    elif op.startswith("not(") and op.endswith(")"):
      return "not ({0} {1} {2})".format(lhs, op[4:-1].strip(), rhs)
    else:
      return "{0} {1} {2}".format(lhs, op.strip(), rhs)

  def transform_op(self, op, value):
    """For comparisons, if the value is None (null), the '=' operator must be replaced with ' is '
    and the '!=' operator must be replaced with ' is not '. This function handles that conversion.
    It's up to the caller to call this function only on comparisons and not on assignments.
    """
    if value is None:
      if _EQ_RE.match(op):
        return "is"
      elif _NEQ_RE.match(op):
        return "is not"

    return op

  def value_comparisons(self, values, comp="=", is_assignment=False):
    """Builds out a series of value comparisions.

    :values: can either be a dictionary, in which case the return will compare a name to a named
    placeholder, using the comp argument. I.E. values = {"first_name": "John", "last_name": "Smith"}
    will return ["first_name = %(first_name)s", "last_name = %(last_name)s"].

    Otherwise values will be assumed to be an iterable of 2- or 3-tuples in the form
    (column, value[, operator]). When operator is not specified, it will fallback to comp. So for
    instance values = [("first_name", "John"), ("id", (10, 100), "between")] will return
    ["first_name = %s", "id between %s and %s "].

    :is_assigment: if False, transform_op will be called on each operator.
    """
    if isinstance(values, dict):
      if self.sort_columns:
        keys = sorted(values.keys())
      else:
        keys = list(values.keys())

      params = zip(keys, [self.to_placeholder(k) for k in keys])
      return [
        self.to_expression(
          i[0],
          i[1],
          comp if is_assignment else self.transform_op(comp, values[i[0]]))
        for i in params]
    else:
      if self.sort_columns:
        values = sorted(values, key=operator.itemgetter(0))
      comps = []
      for val in values:
        lhs = val[0]
        op = val[2] if len(val) == 3 else comp
        if op == "raw":
          rhs = None
        elif op == "between":
          rhs = (self.to_placeholder(), self.to_placeholder())
        elif op == "in":
          rhs = [self.to_placeholder() for i in val[1]]
        else:
          rhs = self.to_placeholder()
          if not is_assignment:
            op = self.transform_op(op, val[1])

        comps.append(self.to_expression(lhs, rhs, op))
      return comps

  def join_comparisons(self, values, joiner, *, is_assignment=False, comp="="):
    """Generates comparisons with the value_comparisions method, and joins them with joiner.

    :is_assignment: if false, transform_op will be called on each comparison operator.
    """
    if isinstance(values, str):
      return values
    else:
      return joiner.join(self.value_comparisons(values, comp, is_assignment))

  def parse_constraints(self, constraints, joiner=" and ", *, is_assignment=False, comp="="):
    """Parses constraints into a (sql, params) tuple.

    :constraints: can either be a dict, an enumerable with a sql string and params, an enumerable of
    2- or 3-tuples, or just a string.

    If is_assignment is false, transform_op will be called on each comparison operator.
    """
    if constraints is None:
      return (None, None)
    elif isinstance(constraints, dict):
      return (
        self.join_comparisons(constraints, joiner, is_assignment=is_assignment, comp=comp),
        self.get_params(constraints))
    elif isinstance(constraints, (list, tuple)):
      if len(constraints) == 2 and isinstance(constraints[0], str):
        return (constraints[0], constraints[1])
      else:
        return (
          self.join_comparisons(constraints, joiner, is_assignment=is_assignment, comp=comp),
          self.get_params(constraints))
    elif isinstance(constraints, str):
      return (constraints, None)
    else:
      raise TypeError(
        "constraints must be None, str, dict, list or tuple. Is {0}".format(
          type(constraints).__name__))

  def get_params(self, values):
    """Gets params to be passed to execute from values.

    :values: can either be a dict, in which case it will be returned as is, or can be an enumerable
    of 2- or 3-tuples. This will return an enumerable of the 2nd values, and in the case of some
    operators such as 'in' and 'between' the values will be specially handled.
    """
    if values is None:
      return None
    elif isinstance(values, dict):
      return values
    elif isinstance(values, (list, tuple)):
      params = []
      for val in values:
        if len(val) == 2:
          params.append(val[1])
        else:
          if val[2] in ("in", "between"):
            params.extend(val[1])
          else:
            params.append(val[1])
      return params
    elif isinstance(values, str):
      return None
    else:
      raise TypeError(
        "values must be None, a dict, list or tuple, is {0}".format(type(values).__name__))

  def get_find_all_query(self, table_name, constraints=None, *, columns=None, order_by=None,
                         limiting=(None, None)):
    """Builds a find query.

    :limiting: if present must be a 2-tuple of (limit, offset) either of which can be None.
    """
    where, params = self.parse_constraints(constraints)

    if columns:
      if isinstance(columns, str):
        pass
      else:
        columns = ", ".join(columns)
    else:
      columns = "*"

    if order_by:
      order = " order by {0}".format(order_by)
    else:
      order = ""

    paging = ""
    if limiting is not None:
      limit, offset = limiting
      if limit is not None:
        paging += " limit {0}".format(limit)
      if offset is not None:
        paging += " offset {0}".format(offset)

    return ("select {0} from {1} where {2}{3}{4}".format(
      columns,
      table_name,
      where or "1 = 1",
      order,
      paging
    ), params)


_EQ_RE = re.compile(r"^\s*=\s*$")
_NEQ_RE = re.compile(r"^\s*!=\s*$")
