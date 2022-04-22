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
Test cases for C2G CLI
"""
import os
import logging
import unittest
from click.testing import CliRunner
from dgi.cli import cli
from py2neo import Graph

######################################################################
#  C 2 G   C L I   T E S T   C A S E S
######################################################################


NEO4J_BOLT_URL = os.getenv("NEO4J_BOLT_URL", "bolt://neo4j:tackle@neo4j:7687")

class TestS2GCLI(unittest.TestCase):
    """Test Cases for c2g command"""

    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self) -> None:
        g = Graph(NEO4J_BOLT_URL)
        g.delete_all()

    def test_help(self):
        """Test help command """
        result = self.runner.invoke(cli, ["c2g", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_missing_input(self):
        """Test --input with no filename """
        result = self.runner.invoke(cli, ["c2g", "--input"])
        self.assertNotEqual(result.exit_code, 0)
        assert (
            "Error: Option '--input' requires an argument." in result.output
        )

    def test_not_found_output(self):
        """Test --input directory not found """
        result = self.runner.invoke(cli, ["c2g", "--input", "foo"])
        self.assertEqual(result.exit_code, 2)
        assert "Directory 'foo' does not exist." in result.output

    def test_abstraction_level_is_class(self):
        """Test --abstraction set to 'class'"""
        result = self.runner.invoke(
            cli, ["--abstraction=class", "c2g", "--input=tests/fixtures/doop_out", "--validate"])
        assert "abstraction level is class" in result.output
        self.assertEqual(result.exit_code, 0)

    def test_abstraction_level_is_method(self):
        """Test --abstraction set to 'method'"""
        result = self.runner.invoke(
            cli, ["--abstraction=method", "c2g", "--input=tests/fixtures/doop_out", "--validate"])
        assert "abstraction level is method" in result.output
        self.assertEqual(result.exit_code, 0)

    def test_abstraction_level_is_full(self):
        """Test --abstraction set to 'full'"""
        result = self.runner.invoke(
            cli, ["--abstraction=full", "c2g", "--input=tests/fixtures/doop_out", "--validate"])
        assert "abstraction level is full" in result.output
        self.assertEqual(result.exit_code, 0)

    def test_abstraction_level_is_wrong(self):
        """Test raise exception when --abstraction set to 'gobbledygook'"""
        result = self.runner.invoke(
            cli, ["--abstraction=gobbledygook", "c2g", "--input=tests/fixtures/doop_out", "--validate"])
        assert "Not a valid abstraction level" in result.output
        self.assertEqual(result.exit_code, 2)
