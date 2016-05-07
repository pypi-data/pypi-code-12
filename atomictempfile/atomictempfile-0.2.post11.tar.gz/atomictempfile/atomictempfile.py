#! /usr/bin/env python

# http://stackoverflow.com/questions/12003805/threadsafe-and-fault-tolerant-file-writes

import logtool, os, tempfile

class AtomicTempFile (object): # pylint: disable=R0903
  """A temporary file object which will be atomically renamed to the
  specified path on exit.  This allows transactional behaviours with
  file writes.

  Args:

    final_path (string): path to the final file
    **kwargs (dict): Will be passed to :class:`tempfile.NamedTemporaryFile`.
      As the tempoaray file will be created in the same directory as the final
      file, the current process must have write access to that directory.
  """

  @logtool.log_call
  def __init__(self, final_path, **kwargs):
    self.final_path = str (final_path) # str cast for broken pathlib
    tmpfile_dir = kwargs.pop ('dir', None)
    if tmpfile_dir is None:
      tmpfile_dir = os.path.dirname (self.final_path)
    self.tmpfile = tempfile.NamedTemporaryFile (dir = tmpfile_dir,
                                                delete = False, **kwargs)

  @logtool.log_call
  def __getattr__ (self, attr):
    return getattr (self.tmpfile, attr)

  @logtool.log_call
  def __enter__ (self):
    self.tmpfile.__enter__ ()
    return self

  @logtool.log_call
  def __exit__ (self, exc_type, exc_val, exc_tb):
    if exc_type is None:
      self.tmpfile.delete = False
      self.tmpfile.__exit__ (exc_type, exc_val, exc_tb)
      os.rename (self.tmpfile.name, self.final_path)
