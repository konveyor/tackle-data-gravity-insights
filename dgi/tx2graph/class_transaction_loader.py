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
Class Transaction Loader Module
"""

import re
from neomodel import DoesNotExist

from dgi.tx2graph.abstract_transaction_loader import AbstractTransactionLoader

# Import our modules
from dgi.models import ClassNode, SQLTable


class ClassTransactionLoader(AbstractTransactionLoader):
    """Transaction edges between classes and DBTables
    """
    def find_or_create_program_node(self, method_signature):
        class_short_name = method_signature.split(".")[-2]
        class_name = ".".join(method_signature.split(".")[:-1])
        try:
            node = ClassNode.nodes.get(node_short_name=class_short_name)
        except DoesNotExist:
            node = ClassNode(
                node_class=class_name, node_short_name=class_short_name
            ).save()
        return node

    def find_or_create_sql_table_node(self, table_name):
        try:
            node = SQLTable.nodes.get(name=table_name)
        except DoesNotExist:
            node = SQLTable(name=table_name).save()

        return node

    def populate_transaction_read(
        self, method_signature, txid, table, action, the_sql_query
    ) -> None:
        class_node = self.find_or_create_program_node(method_signature)
        table_node = self.find_or_create_sql_table_node(table)
        rel = class_node.transaction_read.relationship(table_node)
        if not rel:
            class_node.transaction_read.connect(
                table_node,
                {
                    "txid": txid,
                    "tx_meth": method_signature.split(".")[-1],
                    "action": action,
                    "sql_query": the_sql_query,
                },
            )

    def populate_transaction_write(
        self, method_signature, txid, table, action, the_sql_query
    ):
        class_node = self.find_or_create_program_node(method_signature)
        table_node = self.find_or_create_sql_table_node(table)
        rel = class_node.transaction_write.relationship(table_node)
        if not rel:
            class_node.transaction_write.connect(
                table_node,
                {
                    "txid": txid,
                    "tx_meth": method_signature.split(".")[-1],
                    "action": action,
                    "sql_query": the_sql_query,
                },
            )

    def populate_transaction_callgraph(
        self, callstack: dict, tx_id: int, entrypoint: str
    ) -> None:
        """Add transaction write edges to the database

        Args:
            label (dict): This is a dictionary of the attribute information for the edge. It contains information such
                          as the entrypoint class, method, etc.
            txid (int):   This is the ID assigned to the transaction.
            table (str):  The is the name of the table.
        """
        return

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
            transaction (str):   The transaction under processing.
            action (str):        The action that initiated the transaction
        """
        method_that_access_table = transaction["stacktrace"][-1]
        class_name_next = re.sub(
            "/", ".", method_that_access_table["method"].split(", ")[1][1:]
        )
        method_name_next = (
            method_that_access_table["method"].split(", ")[2].split("(")[0]
        )
        method_signature = ".".join([class_name_next, method_name_next])

        the_sql_query = transaction["sql"]

        for tx_read in read:
            if tx_read.casefold() in the_sql_query.casefold():
                self.populate_transaction_read(
                    method_signature,
                    txid,
                    tx_read.casefold(),
                    action,
                    the_sql_query.casefold(),
                )
        for tx_write in write:
            if tx_write.casefold() in the_sql_query.casefold():
                self.populate_transaction_write(
                    method_signature,
                    txid,
                    tx_write.casefold(),
                    action,
                    the_sql_query.casefold(),
                )
