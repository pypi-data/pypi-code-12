# author: Manuel Gunther <siebenkopf@googlemail.com>
# date:  Wed May 25 10:55:42 MDT 2016
# license: BSD-3, see LICENSE file

def test_package():
  # This function tests that the example actually runs

  # As the test requires that buildout already ran, we do not run buildout again
  import subprocess
  import os, shutil
  import tempfile
  import bob.extension

  tmp = tempfile.mkdtemp(prefix="bobtest_")
  here = os.path.dirname(os.path.realpath(__file__))
  try:
    # find cmake executable
    cmake = bob.extension.find_executable("cmake")
    assert len(cmake)
    cmake = cmake[0]

    # run cmake in the temp directory
    assert subprocess.call([cmake, here], cwd=tmp) == 0
    assert subprocess.call(['make'], cwd=tmp) == 0

    # run the test executable
    assert os.path.exists(os.path.join(tmp, "my_test"))
    shutil.copy(os.path.join(here, "test.png"), tmp)
    assert subprocess.call(["./my_test"], cwd=tmp) == 0

    # assert that the test outout file actually was created
    assert os.path.exists(os.path.join(tmp, "test.hdf5"))

  finally:
    shutil.rmtree(tmp)
