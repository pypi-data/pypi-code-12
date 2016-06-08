# encoding: UTF-8

import click, unittest
from click.testing import CliRunner


class TestInterpreter(unittest.TestCase):

  def test_hello_world(self):
      @click.command()
      @click.argument('name')
      def hello(name):
          click.echo('Hello %s!' % name)

      runner = CliRunner()
      result = runner.invoke(hello, ['Peter'])
      assert result.exit_code == 0
      assert result.output == 'Hello Peter!\n'
