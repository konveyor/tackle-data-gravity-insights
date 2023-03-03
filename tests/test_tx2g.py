################################################################################
# Copyright IBM Corporation 2021, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

"""
Test cases for TX2G CLI
"""
import os
import logging
import unittest
from unittest.mock import patch
from wsgiref import validate
from click.testing import CliRunner
from dgi.cli import cli
from py2neo import Graph
from ipdb import set_trace

######################################################################
#  T X 2 G   C L I   T E S T   C A S E S
######################################################################


NEO4J_BOLT_URL = os.getenv(
    "NEO4J_BOLT_URL", "neo4j://neo4j:konveyor@neo4j:7687")

loglevel = logging.CRITICAL
logging.basicConfig(level=loglevel)


class TestTX2GCLI(unittest.TestCase):
    """Test Cases for TX2G command"""

    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self) -> None:
        pass

    def test_help(self):
        """Test help command"""
        result = self.runner.invoke(cli, ["tx2g", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_no_args(self):
        """Call with no arguments"""
        result = self.runner.invoke(cli, ["tx2g"])
        self.assertNotEqual(result.exit_code, 0)
        assert "Missing option '--input' / '-i'." in result.output

    def test_missing_input(self):
        """Test --input with no filename"""
        result = self.runner.invoke(cli, ["tx2g", "--input"])
        self.assertNotEqual(result.exit_code, 0)
        assert "Option '--input' requires an argument." in result.output

    def test_not_found_input(self):
        """Test --input with file not found"""
        result = self.runner.invoke(cli, ["tx2g", "--input", "foo"])
        print(result.output)
        assert (
            "Invalid value for '--input' / '-i': Path 'foo' does not exist."
            in result.output
        )

    def test_verbose_mode(self):
        """Test verbose mode on"""
        result = self.runner.invoke(
            cli,
            [
                "--validate",
                "tx2g",
                "--input",
                "tests/fixtures/daytrader_transaction.json",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        assert "Validate mode" in result.output

    def test_good_output_with_http_param(self):
        """Test with good output *with* HTTP param"""
        result = self.runner.invoke(
            cli,
            ["--clear", "tx2g", "--input",
                "tests/fixtures/daytrader_transaction.json"],
        )
        self.assertEqual(result.exit_code, 0)

    def test_good_output_without_http_param(self):
        """Test with good output *without* HTTP param"""
        result = self.runner.invoke(
            cli,
            [
                "--clear",
                "tx2g",
                "--input",
                "tests/fixtures/trading_app_transactions.json",
            ],
        )
        self.assertEqual(result.exit_code, 0)

    def test_abstraction_level_is_class(self):
        """Test --abstraction set to 'class'"""
        result = self.runner.invoke(
            cli,
            [
                "--validate",
                "tx2g",
                "--abstraction=class",
                "--input=tests/fixtures/daytrader_transaction.json",
            ],
        )
        assert "abstraction level is class" in result.output
        self.assertEqual(result.exit_code, 0)

    def test_abstraction_level_is_method(self):
        """Test --abstraction set to 'method'"""
        result = self.runner.invoke(
            cli,
            [
                "--validate",
                "tx2g",
                "--abstraction=method",
                "--input=tests/fixtures/daytrader_transaction.json",
            ],
        )
        assert "abstraction level is method" in result.output
        self.assertEqual(result.exit_code, 0)

    def test_abstraction_level_is_full(self):
        """Test --abstraction set to 'full'"""
        result = self.runner.invoke(
            cli,
            [
                "--validate",
                "tx2g",
                "--abstraction=full",
                "--input=tests/fixtures/daytrader_transaction.json",
            ],
        )
        assert "abstraction level is full" in result.output
        self.assertEqual(result.exit_code, 0)

    def test_abstraction_level_is_wrong(self):
        """Test raise exception when --abstraction set to 'gobbledygook'"""
        result = self.runner.invoke(
            cli,
            [
                "--validate",
                "tx2g",
                "--abstraction=gobbledygook",
                "--input=tests/fixtures/daytrader_transaction.json",
            ],
        )
        assert (
            "Invalid value for '--abstraction' / '-a': 'gobbledygook' is not one of 'class', 'method', 'full'."
            in result.output
        )
        self.assertEqual(result.exit_code, 2)
