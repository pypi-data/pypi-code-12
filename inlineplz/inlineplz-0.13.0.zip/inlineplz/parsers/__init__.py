# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from inlineplz.parsers.prospector import ProspectorParser
from inlineplz.parsers.eslint import ESLintParser
from inlineplz.parsers.gherkinlint import GherkinLintParser
from inlineplz.parsers.jscs import JSCSParser
from inlineplz.parsers.jshint import JSHintParser
from inlineplz.parsers.jsonlint import JSONLintParser
from inlineplz.parsers.yamllint import YAMLLintParser
from inlineplz.parsers.rstlint import RSTLintParser
from inlineplz.parsers.markdownlint import MarkdownLintParser
from inlineplz.parsers.stylint import StylintParser
from inlineplz.parsers.rflint import RobotFrameworkLintParser


PARSERS = {
    'prospector': ProspectorParser,
    'eslint': ESLintParser,
    'gherkin-lint': GherkinLintParser,
    'jshint': JSHintParser,
    'jscs': JSCSParser,
    'jsonlint': JSONLintParser,
    'yamllint': YAMLLintParser,
    'rstlint': RSTLintParser,
    'markdownlint': MarkdownLintParser,
    'stylint': StylintParser,
    'rflint': RobotFrameworkLintParser
}
