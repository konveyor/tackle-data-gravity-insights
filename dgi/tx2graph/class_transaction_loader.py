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

from neomodel import DoesNotExist

from dgi.tx2graph.abstract_transaction_loader import AbstactTransactionLoader

# Import our modules
from dgi.models import ClassNode, SQLTable


class ClassTransactionLoader(AbstactTransactionLoader):
    def __init__(self) -> None:
        super().__init__()

    def find_or_create_program_node(self, method_signature):
        # method_name = method_signature.split(".")[-1]
        class_short_name = method_signature.split(".")[-2]
        class_name = ".".join(method_signature.split(".")[:-1])
        try:
            node = ClassNode.nodes.get(node_short_name=class_short_name)
        except DoesNotExist:
            node = ClassNode(
                node_class=class_name, node_short_name=class_short_name
            ).save()
        return node

    def find_or_create_SQL_table_node(self, table_name):
        try:
            node = SQLTable.nodes.get(name=table_name)
        except DoesNotExist:
            node = SQLTable(name=table_name).save()

        return node

    def populate_transaction_read(self, label, txid, table):
        entry_method_signature = label["entry"]["methods"][0]
        class_node = self.find_or_create_program_node(entry_method_signature)
        table_node = self.find_or_create_SQL_table_node(table)
        rel = class_node.transaction_read.relationship(table_node)
        if not rel:
            action = (
                "null"
                if label.get("http-param") is None
                else label.get("http-param").get("action")[0]
            )
            class_node.transaction_read.connect(
                table_node,
                {
                    "txid": txid,
                    "tx_meth": entry_method_signature.split(".")[-1],
                    "action": action,
                },
            )

    def populate_transaction_write(self, label, txid, table):
        entry_method_signature = label["entry"]["methods"][0]
        class_node = self.find_or_create_program_node(entry_method_signature)
        table_node = self.find_or_create_SQL_table_node(table)
        rel = class_node.transaction_write.relationship(table_node)
        if not rel:
            action = (
                "null"
                if label.get("http-param") is None
                else label.get("http-param").get("action")[0]
            )
            class_node.transaction_write.connect(
                table_node,
                {
                    "txid": txid,
                    "tx_meth": entry_method_signature.split(".")[-1],
                    "action": action,
                },
            )
