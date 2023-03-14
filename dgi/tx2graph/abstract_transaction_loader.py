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
Abstract Transaction Loader Module
"""

import re

import json
from collections import OrderedDict
from abc import ABC, abstractmethod
from typing import Dict
import yaml
from neomodel import db
from neomodel import StructuredNode
from dgi.utils.logging import Log
from dgi.utils.progress_bar_factory import ProgressBarFactory
from dgi.tx2graph.utils import sqlexp


class AbstractTransactionLoader(ABC):
    """ABC for tx2graph
    """
    @staticmethod
    def _consume_and_process_label(label: str) -> Dict:
        """Format label into a proper JSON string

        Args:
        label (str): The label as an unformatted string
        """

        # -- DiVA's JSON is malformed. Here, we fix those malformations --
        label = re.sub(r"\n", "", label)
        label = re.sub(r" ", "", label)
        label = re.sub(r"{", '{"', label)
        label = re.sub(r":", '":', label)
        label = re.sub(r",", ',"', label)
        label = re.sub(r"\[", '["', label)
        label = re.sub(r"\]", '"]', label)

        # -- convert to json --
        label = json.loads(label)

        return label

    @staticmethod
    def _clear_all_nodes(force_clear_all: bool):
        """Delete all nodes"""
        Log.warn("The CLI argument clear is turned ON. Deleting pre-existing nodes.")
        db.cypher_query("MATCH (n:SQLTable)-[r]-(m) DELETE r")
        db.cypher_query("MATCH (n)-[r]-(m:SQLTable) DELETE r")
        db.cypher_query("MATCH (n:SQLTable) DELETE n")
        db.cypher_query("MATCH (n:SQLColumn)-[r]-(m) DELETE r")
        db.cypher_query("MATCH (n)-[r]-(m:SQLColumn) DELETE r")
        db.cypher_query("MATCH (n:SQLColumn) DELETE n")
        if force_clear_all:
            Log.warn("Force clear has been turned ON. ALL nodes will be deleted.")
            db.cypher_query("MATCH (n)-[r]-(m) DELETE r")
            db.cypher_query("MATCH (n) DELETE n")

    def crud0(self, ast, write=False):
        """Second stage CRUD"""
        if isinstance(ast, list):
            res = [set(), set()]
            for child in ast[1:]:
                read_set, write_set = self.crud0(child, ast[0] != "select")
                res[0] |= read_set
                res[1] |= write_set
            return res

        if isinstance(ast, dict) and ":from" in ast:
            txn_set = [
                list(txn.values())[0] if isinstance(txn, dict) else txn
                for txn in ast[":from"]
                if not isinstance(txn, tuple)
            ]
            res = set()
            for txn in txn_set:
                if isinstance(txn, list):
                    res |= self.crud0(txn, False)[0]
                else:
                    res.add(txn)
            return [set(), res] if write else [res, set()]

        return [set(), set()]

    def crud(self, sql):
        """First stage CRUD"""
        resp = sqlexp(sql.lower())  # pylint: disable=not-callable
        if resp:
            return self.crud0(resp[1])
        return [set(), set()]

    def analyze(self, txn_set):
        """Analyze the transaction set"""
        for txn in txn_set:
            stack = []
            if txn["transaction"] and txn["transaction"][0]["sql"] != "BEGIN":
                txn["transaction"] = [{"sql": "BEGIN"}] + txn["transaction"]
            for operand in txn["transaction"]:
                if operand["sql"] == "BEGIN":
                    stack.append([set(), set()])
                    operand["rwset"] = stack[-1]
                elif operand["sql"] in ("COMMIT", "ROLLBACK"):
                    if len(stack) > 1:
                        stack[-2][0] |= stack[-1][0]
                        stack[-2][1] |= stack[-1][1]
                    stack[-1][0] = set(stack[-1][0])
                    stack[-1][1] = set(stack[-1][1])
                    stack.pop()
                else:
                    read_set, write_set = self.crud(operand["sql"])
                    stack[-1][0] |= read_set
                    stack[-1][1] |= write_set
        return txn_set

    @abstractmethod
    def find_or_create_program_node(self, method_signature: str) -> StructuredNode:
        """Create an node pertaining to a program feature like class, method, etc.

        Args:
            method_signature (_type_): The full method method signature
        """

    @abstractmethod
    def find_or_create_sql_table_node(self, table_name: str) -> StructuredNode:
        """Create an nodes pertaining to a SQL Table.

        Args:
            table_name (str): The name of the table
        """

    @abstractmethod
    def populate_transaction_read(self, method_signature, txid, table, action, the_sql_query) -> None:  # noqa: R0913
        """Add transaction read edges to the database

        Args:
            label (dict): This is a dictionary of the attribute information for the edge. It contains information such
                          as the entrypoint class, method, etc.
            txid (int):   This is the ID assigned to the transaction.
            table (str):  The is the name of the table.
        """

    @abstractmethod
    def populate_transaction_write(self, method_signature, txid, table, action, the_sql_query) -> None:
        """Add transaction write edges to the database

        Args:
            label (dict): This is a dictionary of the attribute information for the edge. It contains information such
                          as the entrypoint class, method, etc.
            txid (int):   This is the ID assigned to the transaction.
            table (str):  The is the name of the table.
        """

    # pylint: disable=too-many-arguments
    @abstractmethod
    def populate_transaction(
        self,
        label: dict,
        txid: int,
        read: str,
        write: str,
        transaction: list,
        action: str,
    ):
        """Add transaction write edges to the database

        Args:
            label (dict):        This is a dictionary of the attribute information for the edge. It contains information
                                 such as the entrypoint class, method, etc.
            txid (int):          This is the ID assigned to the transaction.
            read (str):          The name of table that has read operations performed on it.
            write (str):         The name of the table that has the write operations performed on it.
            transactions (str):  A list of all the transactions.
            action (str):        The action that initiated the transaction
        """

    @abstractmethod
    def populate_transaction_callgraph(
        self, callstack: dict, tx_id: int, entrypoint: str
    ) -> None:
        """Add transaction write edges to the database

        Args:
            callstack (dict): The callstack from the entrypoint to the transaction.
            tx_id (int)      : This is the ID assigned to the transaction.
            entrypoint (str): The entrypoint that initiated this transaction.
        """

    def tx2neo4j(self, transactions, label):
        """Load the graphDB with transaction data"""

        # If there are no transactions to process, nothing to do here.
        if len(transactions) == 0:
            return

        label = self._consume_and_process_label(label)
        entrypoint = label["entry"]["methods"][0]
        action = label.get("action")
        if action is not None:
            action = action[tuple(label["action"].keys())[0]][0]

        for transaction_dict in transactions:
            txid = transaction_dict["txid"]
            read, write = transaction_dict["transaction"][0]["rwset"]
            for each_transaction in transaction_dict["transaction"][
                1:-1
            ]:  # [0] -> BEGIN, [-1] -> COMMIT
                self.populate_transaction_callgraph(
                    each_transaction["stacktrace"], txid, entrypoint
                )
                self.populate_transaction(
                    label, txid, read, write, each_transaction, action
                )

    def load_transactions(self, input_file, clear, force_clear=False):
        """Load transactions data"""

        yaml.add_representer(
            OrderedDict,
            lambda dumper, data: dumper.represent_mapping(
                "tag:yaml.org,2002:map", list(data.items())
            ),
        )
        # pylint: disable=consider-using-with,unspecified-encoding
        data = json.load(open(input_file), object_pairs_hook=OrderedDict)

        # --------------------------
        # Remove all existing nodes?
        # --------------------------
        if clear:
            self._clear_all_nodes(force_clear)

        Log.info(f"{type(self).__name__}: Populating transactions")

        with ProgressBarFactory.get_progress_bar() as prog_bar:
            for (_, entry) in prog_bar.track(enumerate(data), total=len(data)):
                txn_set = self.analyze(entry["transactions"])
                del entry["transactions"]
                label = yaml.dump(entry, default_flow_style=True).strip()
                self.tx2neo4j(txn_set, label)
