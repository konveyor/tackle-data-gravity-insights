# pylint: disable=duplicate-code
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
Class Graph Builder Module

This module builds a class level abstraction graph.
It is very similar to the method graph builder but with ClassNodes

"""

import logging
from typing import Dict

import pandas as pd
from neomodel import db
from neomodel.exceptions import DoesNotExist

from dgi.code2graph.abstract_graph_builder import AbstractGraphBuilder
# Import local packages
from dgi.models import ClassNode
from dgi.utils import ProgressBarFactory
from dgi.utils.logging import Log

# Author information
__author__ = "Rahul Krishna"
__license__ = "Apache 2.0"
__version__ = "1.0"
__maintainer__ = "Rahul Krishna"
__email__ = "rkrsn@ibm.com"
__status__ = "Research Prototype"


# pylint: disable=too-few-public-methods, duplicate-code
class ClassGraphBuilder(AbstractGraphBuilder):
    """ Build a class level abstraction graph
    """

    @staticmethod
    def _clear_all_nodes():
        """Delete all nodes"""
        Log.warn("The option clear is turned ON. Deleting pre-existing nodes.")
        db.cypher_query("MATCH (n:ClassNode)-[r]-(m) DELETE r")
        db.cypher_query("MATCH (n)-[r]-(m:ClassNode) DELETE r")
        db.cypher_query("MATCH (n:ClassNode) DELETE n")
        # count = 0
        # for node in ClassNode.nodes.all():
        #     count += 1
        #     node.delete()
        # Log.warn(f"Deleted {count} ClassNodes")

    def _create_prev_and_next_nodes(self, prev_meth: Dict, next_meth: Dict):
        prev_class_name = prev_meth["class"]
        prev_class_short_name = prev_class_name.split(".")[-1]

        try:
            prev_graph_node = ClassNode.nodes.get(node_short_name=prev_class_short_name)
        except DoesNotExist:
            # Method information
            prev_graph_node = ClassNode(
                node_class=prev_class_name, node_short_name=prev_class_short_name
            ).save()

        next_class_name = next_meth["class"]
        next_class_short_name = next_class_name.split(".")[-1]

        try:
            next_graph_node = ClassNode.nodes.get(node_short_name=next_class_short_name)
        except DoesNotExist:
            # Method information
            next_graph_node = ClassNode(
                node_class=next_class_name, node_short_name=next_class_short_name
            ).save()

        return prev_graph_node, next_graph_node

    def _populate_heap_edges(self, heap_flows: pd.DataFrame) -> None:
        """Populate heap carried dependencies
        Args:
            heap_flows (pd.DataFrame): Heap flows as a pandas dataframe
        """
        Log.info("Populating heap carried dependencies edges")
        rel_id = 0
        with ProgressBarFactory.get_progress_bar() as progress:
            for (_, row) in progress.track(
                heap_flows.iterrows(), total=heap_flows.shape[0]
            ):
                prev_meth = row.prev
                next_meth = row.next

                prev_graph_node, next_graph_node = self._create_prev_and_next_nodes(
                    prev_meth, next_meth
                )

                if prev_graph_node != next_graph_node:
                    rel = prev_graph_node.heap_flows.relationship(next_graph_node)
                    rel_id += 1
                    if rel and (
                        rel.pmethod,
                        rel.nmethod,
                        rel.context,
                        rel.heap_object,
                    ) == (
                        prev_meth["name"],
                        next_meth["name"],
                        row.context,
                        row.heap_obj,
                    ):
                        rel.weight += 1
                        rel.rel_id = rel_id
                        rel.save()
                    else:
                        relationship_property = {
                            "weight": 1,
                            "rel_id": rel_id,
                            "pmethod": prev_meth["name"],
                            "nmethod": next_meth["name"],
                            "context": row.context,
                            "heap_object": row.heap_obj,
                        }
                        prev_graph_node.heap_flows.connect(
                            next_graph_node, relationship_property
                        )

    def _populate_dataflow_edges(self, data_flows: pd.DataFrame) -> None:
        """Populate data flow dependencies
        Args:
            data_flows (pd.DataFrame): Data flows as a pandas dataframe
        """
        Log.info("Populating dataflow edges")
        rel_id = 0
        with ProgressBarFactory.get_progress_bar() as progress:
            for (_, row) in progress.track(
                data_flows.iterrows(), total=data_flows.shape[0]
            ):
                prev_meth = row.prev
                next_meth = row.next

                prev_graph_node, next_graph_node = self._create_prev_and_next_nodes(
                    prev_meth, next_meth
                )

                if prev_graph_node != next_graph_node:
                    rel = prev_graph_node.data_flows.relationship(next_graph_node)
                    rel_id += 1
                    if rel and (rel.pmethod, rel.nmethod, rel.context) == (
                        prev_meth["name"],
                        next_meth["name"],
                        row.context,
                    ):
                        rel.rel_id = rel_id
                        rel.weight += 1
                        rel.save()
                    else:
                        next_graph_node.data_flows.connect(
                            prev_graph_node,
                            {
                                "weight": 1,
                                "rel_id": rel_id,
                                "pmethod": prev_meth["name"],
                                "nmethod": next_meth["name"],
                                "context": row.context,
                            },
                        )

    def _populate_callreturn_edges(self, call_ret_flows: pd.DataFrame) -> None:
        """Populate data flow dependencies
        Args:
            call_ret_flows (pd.DataFrame): Data flows as a pandas dataframe
        """
        logging.info("Populating call-return dependencies edges")
        rel_id = 0
        with ProgressBarFactory.get_progress_bar() as progress:
            for (_, row) in progress.track(
                call_ret_flows.iterrows(), total=call_ret_flows.shape[0]
            ):
                prev_meth = row.prev
                next_meth = row.next

                prev_graph_node, next_graph_node = self._create_prev_and_next_nodes(
                    prev_meth, next_meth
                )

                if prev_graph_node.node_class != next_graph_node.node_class:
                    rel = prev_graph_node.call_ret_flows.relationship(next_graph_node)
                    rel_id += 1
                    if rel and (
                        rel.pmethod,
                        rel.nmethod,
                        rel.pcontext,
                        rel.ncontext,
                    ) == (
                        prev_meth["name"],
                        next_meth["name"],
                        row.prev_context,
                        row.next_context,
                    ):
                        rel.rel_id = rel_id
                        rel.weight += 1
                        rel.save()
                    else:
                        next_graph_node.call_ret_flows.connect(
                            prev_graph_node,
                            {
                                "weight": 1,
                                "rel_id": rel_id,
                                "pmethod": prev_meth["name"],
                                "nmethod": next_meth["name"],
                                "pcontext": row.prev_context,
                                "ncontext": row.next_context,
                            },
                        )
