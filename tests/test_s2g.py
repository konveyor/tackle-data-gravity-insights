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
Test cases for S2G CLI
"""
import os
import logging
import unittest
from click.testing import CliRunner
from dgi.cli import cli
from py2neo import Graph

######################################################################
#  S 2 G   C L I   T E S T   C A S E S
######################################################################


NEO4J_BOLT_URL = os.getenv("NEO4J_BOLT_URL")


class TestS2GCLI(unittest.TestCase):
    """Test Cases for S2G command"""

    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self) -> None:
        g = Graph(NEO4J_BOLT_URL)
        g.delete_all()

    def test_help(self):
        """Test help command """
        result = self.runner.invoke(cli, ["s2g", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_no_args(self):
        """ Call with to arguments """
        result = self.runner.invoke(cli, ["s2g"])
        self.assertNotEqual(result.exit_code, 0)
        assert (
            "Error: Missing option '--input' / '-i'." in result.output
        )

    def test_missing_input(self):
        """Test --input with no filename """
        result = self.runner.invoke(cli, ["s2g", "--input"])
        self.assertNotEqual(result.exit_code, 0)
        assert (
            "Error: Option '--input' requires an argument." in result.output
        )

    def test_not_found_output(self):
        """Test --input with file not found """
        result = self.runner.invoke(cli, ["s2g", "--input", "foo"])
        self.assertEqual(result.exit_code, 2)
        assert "Path 'foo' does not exist." in result.output

    def test_good_output(self):
        """Test with good output """
        result = self.runner.invoke(
            cli, ["--clear", "s2g", "--input", "tests/fixtures/test-schema.ddl"])
        print(result.exception)
        self.assertEqual(result.exit_code, 0)

    def test_validate_only(self):
        """Test validating the a good file """
        result = self.runner.invoke(
            cli, ["s2g", "--validate", "--input", "tests/fixtures/test-schema.ddl"])
        self.assertEqual(result.exit_code, 0)
        assert "File [tests/fixtures/test-schema.ddl] validated." in result.output

    def test_output_file(self):
        """Test writing output file """
        result = self.runner.invoke(
            cli, ["s2g", "--validate", "--input", "tests/fixtures/test-schema.ddl", "--output", "test.json"])
        self.assertEqual(result.exit_code, 0)
        assert "Writing: test.json" in result.output
        os.remove("test.json")
