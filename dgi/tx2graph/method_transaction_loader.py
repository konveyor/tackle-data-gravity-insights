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
Method Transaction Loader Module
"""

import re

from neomodel import DoesNotExist

# Import our modules
from dgi.models import SQLTable, MethodNode
from dgi.tx2graph.abstract_transaction_loader import AbstractTransactionLoader


class MethodTransactionLoader(AbstractTransactionLoader):
    """CRUD operation at a method level.
    """

    def find_or_create_program_node(self, method_signature: str, is_entrypoint=False) -> MethodNode:
        method_name = method_signature.split(".")[-1]
        class_short_name = method_signature.split(".")[-2]
        class_name = ".".join(method_signature.split(".")[:-1])

        try:
            node = MethodNode.nodes.get(node_method=method_signature)
        except DoesNotExist:
            node = MethodNode(
                node_method=method_signature,
                node_class=class_name,
                node_class_name=class_short_name,
                node_name=method_name,
                node_short_name=class_short_name,
                node_is_tx_entry=is_entrypoint,
            ).save()

        return node

    def find_or_create_sql_table_node(self, table_name) -> SQLTable:
        try:
            node = SQLTable.nodes.get(name=table_name)
        except DoesNotExist:
            node = SQLTable(name=table_name).save()

        return node

    def populate_transaction_read(
        self, method_signature, txid, table, action, the_sql_query
    ) -> None:
        method_node = self.find_or_create_program_node(method_signature)
        table_node = self.find_or_create_sql_table_node(table)
        rel = method_node.transaction_read.relationship(table_node)
        if not rel:
            method_node.transaction_read.connect(
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
        method_node = self.find_or_create_program_node(method_signature)
        table_node = self.find_or_create_sql_table_node(table)
        rel = method_node.transaction_write.relationship(table_node)
        if not rel:
            method_node.transaction_write.connect(
                table_node,
                {
                    "txid": txid,
                    "tx_meth": method_signature.split(".")[-1],
                    "action": action,
                    "sql_query": the_sql_query,
                },
            )

    def populate_transaction_callgraph(
            self, callstack: dict, tx_id: int, entrypoint: str) -> None:
        """Add transaction write edges to the database

        Args:
            callstack (dict): The callstack from the entrypoint to the transaction.
            tx_id (int)      : This is the ID assigned to the transaction.
            entrypoint (str): The entrypoint that initiated this transaction.
        """
        # Create a method node for this entrypoint
        self.find_or_create_program_node(entrypoint, is_entrypoint=True)

        # Iterate over all the calls in the callstack and build the callgraph.
        for prev_call, next_call in zip(callstack[:-1], callstack[1:]):
            # We strip the class signature (which is in the JNI type signature format) to use a dot notation
            # E.g., Lcom/abc/class --> com.abc.class.
            class_name_prev = re.sub("/", ".", prev_call["method"].split(", ")[1][1:])
            # Likewise, we process the method signature as well.
            method_name_prev = prev_call["method"].split(", ")[2].split("(")[0]
            method_signature_prev = ".".join([class_name_prev, method_name_prev])
            prev_node = self.find_or_create_program_node(method_signature_prev)

            class_name_next = re.sub("/", ".", next_call["method"].split(", ")[1][1:])
            method_name_next = next_call["method"].split(", ")[2].split("(")[0]
            method_signature_next = ".".join([class_name_next, method_name_next])
            next_node = self.find_or_create_program_node(method_signature_next)

            rel = prev_node.transaction_method_call.relationship(next_node)
            if not rel:
                prev_node.transaction_method_call.connect(
                    next_node, {"txid": tx_id, "service_entry": entrypoint}
                )

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
