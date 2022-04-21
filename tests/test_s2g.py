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
from cmath import log
import os
import logging
import unittest
from py2neo import Graph
from click.testing import CliRunner
from dgi.cli import cli

logging.disable(logging.CRITICAL)

NEO4J_BOLT_URL = os.getenv("NEO4J_BOLT_URL", "bolt://neo4j:dgi@neo4j:7687")

######################################################################
#  S 2 G   C L I   T E S T   C A S E S
######################################################################
class TestS2GCLI(unittest.TestCase):
    """Test Cases for S2G command"""

    graph = None

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        cls.graph = Graph(NEO4J_BOLT_URL)

    def setUp(self):
        self.runner = CliRunner()

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
        result = self.runner.invoke(cli, ["--clear", "s2g", "--input", "tests/fixtures/test-schema.ddl"])
        self.assertEqual(result.exit_code, 0)

    def test_validate_only(self):
        """Test validating the a good file """
        result = self.runner.invoke(cli, ["s2g", "--validate", "--input", "tests/fixtures/test-schema.ddl"])
        self.assertEqual(result.exit_code, 0)
        assert "File [tests/fixtures/test-schema.ddl] validated." in result.output

    def test_output_file(self):
        """Test writing output file """
        result = self.runner.invoke(cli, ["s2g", "--validate", "--input", "tests/fixtures/test-schema.ddl", "--output", "test.json"])
        self.assertEqual(result.exit_code, 0)
        assert "Writing: test.json" in result.output
        os.remove("test.json")

    def test_neo_graph_count(self):
        """Test the number of nodes were populated """
        result = self.runner.invoke(cli, ["--clear", "s2g", "--input", "tests/fixtures/test-schema.ddl"])
        self.assertEqual(result.exit_code, 0)

        cypher = "MATCH (n:SQLTable) RETURN COUNT(n)"
        cursor = TestS2GCLI.graph.run(cypher)
        self.assertEqual(cursor.evaluate(), 6)

    def test_neo_graph_sqltables(self):
        """Test the SQLTables were populated """
        result = self.runner.invoke(cli, ["--clear", "s2g", "--input", "tests/fixtures/test-schema.ddl"])
        self.assertEqual(result.exit_code, 0)

        cypher = "MATCH (n:SQLTable) RETURN n.name as name"
        cursor = TestS2GCLI.graph.run(cypher).data()
        data = [n["name"] for n in cursor]
        self.assertIn("ACCOUNTPROFILEEJB", data)
        self.assertIn("QUOTEEJB", data)
        self.assertIn("KEYGENEJB", data)
        self.assertIn("ACCOUNTEJB", data)
        self.assertIn("ORDEREJB", data)
        self.assertIn("HOLDINGEJB", data)

    def test_neo_graph_sqlcolumns(self):
        """Test the SQLColumns were populated """
        result = self.runner.invoke(cli, ["--clear", "s2g", "--input", "tests/fixtures/test-schema.ddl"])
        self.assertEqual(result.exit_code, 0)
        cypher1 = "MATCH (:SQLTable{name:\"ACCOUNTPROFILEEJB\"})-[:CONTAINS]->(m:SQLColumn) RETURN m.name as name"
        cursor1 = TestS2GCLI.graph.run(cypher1).data()
        data1 = [n["name"] for n in cursor1]
        self.assertIn("PASSWD", data1)
        cypher2 = "MATCH (:SQLTable{name:\"QUOTEEJB\"})-[:CONTAINS]->(m:SQLColumn) RETURN m.name as name"
        cursor2 = TestS2GCLI.graph.run(cypher2).data()
        data2 = [n["name"] for n in cursor2]
        self.assertEqual(len(data2), 7)
        self.assertIn("COMPANYNAME", data2)
        self.assertIn("VOLUME", data2)
        cypher3 = "MATCH (:SQLTable{name:\"ORDEREJB\"})-[:CONTAINS]->(m:SQLColumn) RETURN m.name as name"
        cursor3 = TestS2GCLI.graph.run(cypher3).data()
        data3 = [n["name"] for n in cursor3]
        self.assertIn("ACCOUNT_ACCOUNTID", data3)
        self.assertIn("ORDERSTATUS", data3)
        self.assertIn("COMPLETIONDATE", data3)

    def test_neo_graph_primarykey(self):
        """Test if the primary key(s) were populated """
        result = self.runner.invoke(cli, ["--clear", "s2g", "--input", "tests/fixtures/test-schema.ddl"])
        self.assertEqual(result.exit_code, 0)
        cypher4 = "MATCH (:SQLTable{name:\"QUOTEEJB\"})-[:CONTAINS]->(m:SQLColumn) RETURN m.is_primary as name"
        cursor4 = TestS2GCLI.graph.run(cypher4).data()
        data4 = [n["name"] for n in cursor4]
        self.assertEqual(True, data4[0])

    def test_neo_graph_foreignkey(self):
        """Test if the foreign key(s) were populated """
        result = self.runner.invoke(cli, ["--clear", "s2g", "--input", "tests/fixtures/test-schema.ddl"])
        self.assertEqual(result.exit_code, 0)
        cypherForeign = "MATCH (:SQLColumn{name:\"QUOTE_SYMBOL\"})-[:FOREIGN_KEY]->(m:SQLColumn) RETURN m.name as name"
        cursorForeign = TestS2GCLI.graph.run(cypherForeign).data()
        dataForeign = [n["name"] for n in cursorForeign]
        self.assertIn("SYMBOL", dataForeign)
