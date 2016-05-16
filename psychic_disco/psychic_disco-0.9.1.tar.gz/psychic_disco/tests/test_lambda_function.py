import unittest
from psychic_disco import lambda_function
from psychic_disco.lambda_function import LambdaFunction


class TestLambdaFunction(unittest.TestCase):
    def test_declared_functions(self):
        f = LambdaFunction("listdir", "os")
        self.assertIn(f, lambda_function.declared_functions())

    def test_proper_name(self):
        f = LambdaFunction("listdir", "os")
        self.assertEqual(f.proper_name, "os-listdir")

if __name__ == "__main__":
    unittest.main()
