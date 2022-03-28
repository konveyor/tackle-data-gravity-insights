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

from cProfile import label
import re
import yaml
from neomodel import StructuredNode
import json
import logging
from collections import OrderedDict
from abc import ABC, abstractmethod
from dgi.models import SQLTable, SQLColumn
from typing import List, Dict
from dgi.tx2graph.utils import sqlexp
from tqdm import tqdm


class AbstactTransactionLoader(ABC):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def _consume_and_process_label(label: str) -> Dict:
        """Format lable into a proper JSON string 

        Args:
        label (str): The lable as an unformatted string
        """
        # -- Strip newline --
        label = re.sub("\n", '', label)
        # -- format 'entry' key --
        label = re.sub("entry", '"entry"', label)
        # -- format 'action' key --
        label = re.sub("action", '"action"', label)
        # -- format 'methods' key --
        label = re.sub("methods", '"methods"', label)
        # -- format 'http-param' key --
        label = re.sub("http-param", '"http-param"', label)
        label = re.sub("\[", '["', label)
        label = re.sub("\]", '"]', label)

        # -- convert to json --
        label = json.loads(label)

        return label

    @staticmethod
    def _clear_all_nodes():
        """ Delete all nodes """
        for node in SQLTable.nodes.all():
            node.delete()

        for node in SQLColumn.nodes.all():
            node.delete()

    def crud0(self, ast, write=False):
        if isinstance(ast, list):
            res = [set(), set()]
            for child in ast[1:]:
                rs, ws = self.crud0(child, ast[0] != 'select')
                res[0] |= rs
                res[1] |= ws
            return res
        elif isinstance(ast, dict) and ':from' in ast:
            ts = [list(t.values())[0] if isinstance(t, dict)
                  else t for t in ast[':from'] if not isinstance(t, tuple)]
            res = set()
            for t in ts:
                if isinstance(t, list):
                    res |= self.crud0(t, False)[0]
                else:
                    res.add(t)
            return [set(), res] if write else [res, set()]
        else:
            return [set(), set()]

    def crud(self, sql):
        r = sqlexp(sql.lower())
        if r:
            return self.crud0(r[1])
        else:
            return [set(), set()]

    def analyze(self, txs):
        for tx in txs:
            stack = []
            if tx['transaction'] and tx['transaction'][0]['sql'] != 'BEGIN':
                tx['transaction'] = [{'sql': 'BEGIN'}] + tx['transaction']
            for op in tx['transaction']:
                if op['sql'] == 'BEGIN':
                    stack.append([set(), set()])
                    op['rwset'] = stack[-1]
                elif op['sql'] in ('COMMIT', 'ROLLBACK'):
                    if len(stack) > 1:
                        stack[-2][0] |= stack[-1][0]
                        stack[-2][1] |= stack[-1][1]
                    stack[-1][0] = set(stack[-1][0])
                    stack[-1][1] = set(stack[-1][1])
                    stack.pop()
                else:
                    rs, ws = self.crud(op['sql'])
                    stack[-1][0] |= rs
                    stack[-1][1] |= ws
        return txs

    @abstractmethod
    def find_or_create_program_node(self, method_signature: str) -> StructuredNode:
        """Create an node pertaining to a program feature like class, method, etc. 

        Args:
            method_signature (_type_): The full method method signature
        """
        pass

    @abstractmethod
    def find_or_create_SQL_table_node(self, table_name: str) -> StructuredNode:
        """Create an nodes pertaining to a SQL Table.

        Args:
            table_name (str): The name of the table
        """
        pass

    @abstractmethod
    def populate_transaction_read(label: dict, txid: int, table: str) -> None:
        """Add transaction read edges to the database

        Args:
            label (dict): This is a dictionary of the attribute information for the edge. It contains information such 
                          as the entrypoint class, method, etc. 
            txid (int):   This is the ID assigned to the transaction.
            table (str):  The is the name of the table.
        """
        pass

    @abstractmethod
    def populate_transaction_write(label: dict, txid: int, table: str) -> None:
        """Add transaction write edges to the database

        Args:
            label (dict): This is a dictionary of the attribute information for the edge. It contains information such 
                          as the entrypoint class, method, etc. 
            txid (int):   This is the ID assigned to the transaction.
            table (str):  The is the name of the table.
        """
        pass

    def tx2neo4j(self, transactions, label):
        # If there are no transactions to process, nothing to do here.
        if not transactions:
            return

        label = self._consume_and_process_label(label)

        for transaction_dict in transactions:
            txid = transaction_dict['txid']
            read, write = transaction_dict['transaction'][0]['rwset']
            for t in read:
                self.populate_transaction_read(label, txid, t)
            for t in write:
                self.populate_transaction_write(label, txid, t)

    def load_transactions(self, input, clear):

        # ----------------------
        # Load transactions data
        # ----------------------
        yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_mapping(
            'tag:yaml.org,2002:map', list(data.items())))
        data = json.load(open(input), object_pairs_hook=OrderedDict)

        # --------------------------
        # Remove all existing nodes?
        # --------------------------
        if clear:
            logging.info(
                "Clear flag detected... Deleting pre-existing SQLTable nodes.")
            self._clear_all_nodes()

        logging.info("{}: Populating transactions".format(type(self).__name__))
        for c, entry in tqdm(enumerate(data), total=len(data)):
            txs = self.analyze(entry['transactions'])
            del(entry['transactions'])
            label = yaml.dump(entry, default_flow_style=True).strip()
            self.tx2neo4j(txs, label)
