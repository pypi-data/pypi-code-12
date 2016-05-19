#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_faz
----------------------------------

Tests for `faz` module.
"""
import os
import glob
import time
import unittest

from faz import main, parser
from faz.task import Task, TaskFailedException
from faz.graph import CircularDependencyException


FILE = """file=file999
# Using bash as the interpreter
# file21, file22, $file <-
touch file21 file22
echo "Output from the first task"
echo $file
touch $file

# file3, file4 <- file2*, $file :force
touch file3 file4
echo "Output from the last task"
"""

FILE1 = """
# Using bash as the interpreter
# file1, file2 <-
touch file1 file2

# file3, file4 <- file1, file2
echo "Hellow world! 1" > file3
echo "Hellow world! 1" > file4

# file5, file6 <- file3, file4
echo "Hellow world! 2" > file5
echo "Hellow world! 2" > file6

# file7, file8 <- file5, file6
echo "Hellow world! 3" > file7
echo "Hellow world! 3" > file8

# Now using python as the interpreter
# file9, file10, file11 <- file5, file3 :python, force
import sys

a = [[range(3)], [range(4, 7)], [range(7, 10)]]
f = open("file11", "w")
for line in a:
    f.write(" ".join([str(i) for i in line]))
f.close()
open("file9", "w").write("Hello from python\\n")
open("file10", "w").write("Hello from python\\n")

# file22, file33 <- file1, file11 :ruby
File.open("file22", 'w') { |file| file.write("Hi Ruby22!") }
File.open("file33", 'w') { |file| file.write("Hi Ruby33!") }
"""


FILE2 = """
# Using bash as the interpreter
# file1, file2 <-
touch file3 file4
touch file1 file2

# file3, file4 <- file1, file2
echo "Hellow world! 1" > file3
echo "Hellow world! 1" > file4

# file5, file6 <- file3, file4
echo "Hellow world! 2" > file5
echo "Hellow world! 2" > file6

# file7, file8 <- file5, file6
echo "Hellow world! 3" > file7
echo "Hellow world! 3" > file8
"""

FILE3 = """
# Using bash as the interpreter
# file1, file2 <-
touch file3 file4
"""

FILE4 = """
# Using bash as the interpreter
# file3, file4 <- file1, file2
touch file3 file4
"""


FILE5 = """
# Using bash as the interpreter
# file1, file2 <-
touch file5
touch file1 file2

# file3, file4 <- file1, file2
touch file3 file4

# file5 <- file3, file4
touch file5
"""


FILE6 = """
# Using bash as the interpreter
# file21, file22 <-
touch file21 file22

# file3, file4 <- file2*
touch file3 file4
"""


FILE7 = """
test = 1
a = 2
b = 3
"""


FILE8 = """
file=asdf
# Using bash as the interpreter
# file21, file22, $file <-
touch file21 file22
touch $file

# file3, file4 <- file2*, $file
touch file3 file4

# file5, file6 <- file3, file4
touch $[OUTPUT1]
touch $[OUTPUT2]
"""


FILE9 = """
# Using bash as the interpreter
# file21, file22 <- file3
touch file21 file22

# file3, file4 <- file22, file21
touch file3 file4
"""


class TestYamt(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.faz(FILE1)

    def tearDown(self):
        for fname in glob.glob("file*"):
            os.unlink(fname)


class TestMain(unittest.TestCase):

    def setUp(self):
        f = open("fazfile", "w")
        f.write(FILE1)
        f.close()

    def test_something(self):
        main.main(arguments=[])

    def tearDown(self):
        for fname in glob.glob("file*"):
            os.unlink(fname)
        os.unlink("fazfile")


class TestInputFileDoesNotExist(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.expectedFailure
    def test_something(self):
        main.main(arguments=["nonexistent_file"])

    def tearDown(self):
        pass


class TestMainDebug(unittest.TestCase):

    def setUp(self):
        f = open("fazfile", "w")
        f.write(FILE1)
        f.close()

    def test_something(self):
        main.main(arguments=["-d"])

    def tearDown(self):
        for fname in glob.glob("file*"):
            os.unlink(fname)
        os.unlink("fazfile")


class TestMissingInput(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.expectedFailure
    def test_something(self):
        main.faz()

    def tearDown(self):
        pass


class TestMissingInputs(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.faz(FILE2)

    def tearDown(self):
        for fname in glob.glob("file*"):
            os.unlink(fname)


class TestYAMTFileInDir(unittest.TestCase):

    def setUp(self):
        for fname in glob.glob(".faz/tmp*"):
            os.remove(fname)
        os.rmdir(".faz")
        f = open(".faz", "w")
        f.close()

    @unittest.expectedFailure
    def test_something(self):
        main.faz(FILE1)

    def tearDown(self):
        os.unlink(".faz")


class TestOuputsNotCreated(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.expectedFailure
    def test_something(self):
        main.faz(FILE3)

    def tearDown(self):
        pass


class TestInputsDoNotExist(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.faz(FILE4)

    def tearDown(self):
        pass


class TestOutputsAreOlderThanInputs(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.faz(FILE5)

    def tearDown(self):
        pass


class TestWildcardInName(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.faz(FILE6)

    def tearDown(self):
        pass


class TestParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        tasks = parser.parse_input_file(FILE1)
        self.failUnlessEqual(6, len(tasks))

    def tearDown(self):
        pass


class TestEnvironment(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        env = parser.create_environment(FILE7.splitlines())
        self.failUnlessEqual(env["test"], "1")
        self.failUnlessEqual(env["a"], "2")
        self.failUnlessEqual(env["b"], "3")

    def tearDown(self):
        pass


class TestVariableExpansion(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.faz(FILE8)

    def tearDown(self):
        for fname in glob.glob("file*"):
            os.unlink(fname)
        os.unlink('asdf')


class TestCircularDependencyException(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        with self.assertRaises(CircularDependencyException):
            main.faz(FILE9)

    def tearDown(self):
        pass


class TestTaskMethods(unittest.TestCase):

    def setUp(self):
        self.filenames = ["file1",
                          "file2",
                          "file3",
                          "file_1",
                          "file_2",
                          "file_3",
                          "file__1",
                          "file__2",
                          ]
        self.should_not_be_present = ["file4",
                                      "file5",
                                      "file6",
                                      "file7",
                                      "file8",
                                      "file9",
                                      ]
        for filename in self.should_not_be_present:
            if os.path.exists(filename) and os.path.isfile(filename):
                os.unlink(filename)
        for filename in self.filenames:
            with open(filename, "w") as f:
                f.close()
        self.task = Task(["file[0-3]", "file_*"],
                         ["file[4-6]"],
                         ["touch file4\n", "touch file5\n", "touch file6\n", "echo $[test_var]\n", "echo $test_var\n"],
                         ["force"],
                         {"test_var": "test_var_value"})

    def test_task(self):
        self.task()

    def test_code_variable_expansion(self):
        self.task.expand_variables()
        self.assertTrue(any([line for line in self.task.code if "test_var_value" in line]))

    def test_outputs_do_not_exist(self):
        task = Task(["file[0-3]", "file_*"],
                    ["file99", "file234"],
                    ["touch file4\n", "touch file5\n", "touch file6\n"],
                    ["force"],
                    {"test_var": "test_var_value"})
        with self.assertRaises(TaskFailedException):
            task()

    def test_return_code_is_not_0(self):
        task = Task(["file[0-3]", "file_*"],
                    ["file99", "file234"],
                    ["touch file4\n",
                     "touch file5\n",
                     "touch file6\n",
                     "ls non_existant_dir\n"],
                    ["force"],
                    {"test_var": "test_var_value"})
        with self.assertRaises(TaskFailedException):
            task()

    def test_use_the_force(self):
        f = open("file22", "w")
        f.close()
        time.sleep(0.1)
        f = open("file33", "w")
        f.close()
        self.assertTrue(os.path.getmtime("file33") > os.path.getmtime("file22"))
        task = Task(["file22"],
                    ["file33"],
                    ["touch file33\n"],
                    ["force"],
                    {"test_var": "test_var_value"})
        result = self.task.dependencies_are_newer(["file33"], ["file22"])
        self.assertFalse(result)
        self.assertTrue(task.inputs == ["file22"])
        self.assertTrue(task.outputs == ["file33"])
        self.assertTrue(task.code == ["touch file33\n"])
        self.assertTrue(task.options == ["force"])
        self.assertTrue(task.interpreter == "bash")
        self.assertTrue(task.force)
        task()
        os.unlink("file22")
        os.unlink("file33")

    def test_files_exist(self):
        self.assertTrue(self.task.files_exist(["file1", "file2", "file3"]))

    def test_filename_shell_expansion(self):
        results = self.task.expand_filenames(["file[0-3]", "file_?", "file__*"])
        for result, filename in zip(results, self.filenames):
            self.assertEqual(result, filename)

    def test_filename_variable_expansion(self):
        results = self.task.expand_filenames(["$test_var"])
        self.assertEqual(results[0], "test_var_value")

    def test_nonexistant_file(self):
        results = self.task.expand_filenames(["file[4-9]"])
        self.assertEqual(results[0], "NONEXISTENT")

    def test_dependencies_are_newer(self):
        for filename in ["old_file1", "old_file2"]:
            with open(filename, "w") as f:
                f.close()
        time.sleep(0.1)
        for filename in ["new_file1", "new_file2"]:
            with open(filename, "w") as f:
                f.close()
        result = self.task.dependencies_are_newer(["old_file1", "old_file2"],
                                                  ["new_file1", "new_file2"])
        self.assertTrue(result)
        [os.unlink(filename) for filename in ["old_file1", "old_file2"]]
        [os.unlink(filename) for filename in ["new_file1", "new_file2"]]

    def test_dependencies_are_older(self):
        for filename in ["new_file1", "new_file2"]:
            with open(filename, "w") as f:
                f.close()
        time.sleep(0.1)
        for filename in ["old_file1", "old_file2"]:
            with open(filename, "w") as f:
                f.close()
        result = self.task.dependencies_are_newer(["old_file1", "old_file2"],
                                                  ["new_file1", "new_file2"])
        self.assertFalse(result)
        [os.unlink(filename) for filename in ["old_file1", "old_file2"]]
        [os.unlink(filename) for filename in ["new_file1", "new_file2"]]

    def tearDown(self):
        for filename in self.filenames:
            os.unlink(filename)


if __name__ == '__main__':
    unittest.main(verbosity=3)
