"""Contains classes and methods for writing data to a terminal."""
import sys
from datetime import datetime


__all__ = ["ProgressPrinter", "table_to_string"]


class ProgressPrinter(object):
  """A flexible command-line progress printer."""
  # pylint: disable=invalid-name

  def __init__(self, total, *, format="{} / {}", format_time_remaining=None):
    self._total = total
    self._format = format
    self._format_time_remaining = format_time_remaining
    self._current = 0
    self._started_at = None
    self._message = ""

  def __enter__(self):
    """Start the progress printer."""
    self.start()
    return self

  def __exit__(self, ex_type, ex_value, ex_traceback):
    """Stop the progress printer."""
    self.done()

  def start(self):
    """Sets several instance values to indicate when progress started."""
    self._started_at = datetime.now()
    self._current = 0

  def increment(self, amount=1, output=True):
    """Increment progress by a given amount (defaults to 1) and (optionally) output the progress
    status.
    """
    self._current += amount
    if output:
      # NOTE: This algorithm averages out the time it has taken to get to the current / total to
      #       determine how much time is left. So this is best used with jobs that have steps whose
      #       run time is roughly the same.

      now = datetime.now()
      elapsed_time = now - self._started_at
      expected_finish = self._started_at + elapsed_time * (1 / (self._current / self._total))
      remaining_time = expected_finish - now

      if self._format_time_remaining:
        remaining_time_str = self._format_time_remaining(remaining_time)
      else:
        remaining_time_str = str(remaining_time)

      tab_count = self._message.count("\t")
      sys.stdout.write("\r" + "\t" * tab_count + " " * (len(self._message) - tab_count))

      if isinstance(self._format, str):
        self._message = self._format.format(self._current, self._total, remaining_time_str)
      else:
        self._message = self._format(self._current, self._total, remaining_time_str)

      sys.stdout.write("\r" + self._message)
      sys.stdout.flush()

  def done(self):
    """Clean up after progress printing is done."""
    print()

  @staticmethod
  def ratio(current, total, time_remaining):
    """Returns the progress ratio."""
    return "{} / {}".format(current, total)

  @staticmethod
  def percentage(current, total, time_remaining):
    """Returns the progress percentage."""
    return "{}% completed".format(int(current / total * 100))

  @staticmethod
  def time_remaining(current, total, time_remaining):
    """Returns the time remaining."""
    return "~{} remaining".format(time_remaining)

  @staticmethod
  def ratio_and_percentage(current, total, time_remaining):
    """Returns the progress ratio and percentage."""
    return "{} / {} ({}% completed)".format(current, total, int(current / total * 100))

  @staticmethod
  def ratio_with_time_remaining(current, total, time_remaining):
    """Returns the progress ratio and time remaining."""
    return "{} / {} (~{} remaining)".format(current, total, time_remaining)

  @staticmethod
  def percentage_with_time_remaining(current, total, time_remaining):
    """Returns the progress percentage and time remaining."""
    return "{}% (~{} remaining)".format(int(current / total * 100), time_remaining)

  @staticmethod
  def ratio_and_percentage_with_time_remaining(current, total, time_remaining):
    """Returns the progress ratio, percentage and time remaining."""
    return "{} / {} ({}% completed) (~{} remaining)".format(
      current,
      total,
      int(current / total * 100),
      time_remaining)

  @staticmethod
  def time_remaining_whole_seconds(time_remaining):
    """Strips off the microsecond portion of time remaining."""
    return str(time_remaining).split(".")[0]


def table_to_string(headers, table, align="", *, lines=("-", "-+-", " | ")):
  """Write a list of headers and a table of rows to the terminal in a nice format.

  Parameters:
  - headers: a list of strings that are the headers of the table
  - table: a list of lists, the actual data to be printed.
  - align: a string whose elements are in the set {'<', '^', '>'}. These define how the values
           printed in the cells will align. '<': left, '^': center, '>': right. This argument is
           optional and all unspecified columns will align as if '<' were passed for them.
  - lines: a tuple of line characters to print for the table: (row_sep, row_intersection, col_sep)
  """
  header_separator, header_junction, row_separator = lines
  align = ("{0:<<" + str(len(headers)) + "}").format(align or "")
  all_lens = [tuple(len(c) for c in r) for r in table]

  if headers:
    all_lens.append(tuple(len(h) for h in headers))

  max_lens = [max(r[i] for r in all_lens) for i in range(len(headers))]
  col_outs = ["{{{0}: {1}{2}}}".format(i, align[i], w) for i, w in enumerate(max_lens)]
  fmt_str = row_separator.join(col_outs)
  if headers:
    yield fmt_str.format(*headers)
    yield header_junction.join((header_separator * ml for ml in max_lens))
  for row in table:
    yield fmt_str.format(*row)
