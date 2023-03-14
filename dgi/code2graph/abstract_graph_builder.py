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
Abstract Graph Builder

This is the abstract base class for all of the graph builders
"""
from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd

from dgi.code2graph.process_facts import ConsumeFacts
from dgi.utils.logging import Log

# Author information
__author__ = "Rahul Krishna"
__license__ = "Apache 2.0"
__version__ = "1.0"
__maintainer__ = "Rahul Krishna"
__email__ = "rkrsn@ibm.com"
__status__ = "Research Prototype"


# pylint: disable=too-few-public-methods
class AbstractGraphBuilder(ABC):
    """Abstract graph builder is a base class that is implemented by method and class graph builders.
    """
    def __init__(self, opt):
        self.opt = opt

    @staticmethod
    @abstractmethod
    def _clear_all_nodes():
        """Delete all nodes"""

    @abstractmethod
    def _create_prev_and_next_nodes(self, prev_meth: Dict, next_meth: Dict):
        """_summary_

        Args:
            prev_df_entry (Dict): A dictionary of method information for source method
            next_df_entry (Dict): A dictionary of method information for destination method
        """

    @abstractmethod
    def _populate_heap_edges(self, heap_flows: pd.DataFrame) -> None:
        """Populate heap carried dependencies
        Args:
            heap_flows (pd.DataFrame): Heap flows as a pandas dataframe
        """

    @abstractmethod
    def _populate_dataflow_edges(self, data_flows: pd.DataFrame) -> None:
        """Populate data flow dependencies
        Args:
            data_flows (pd.DataFrame): Data flows as a pandas dataframe
        """

    @abstractmethod
    def _populate_callreturn_edges(self, call_ret_flows: pd.DataFrame) -> None:
        """Populate data flow dependencies
        Args:
            call_ret_flows (pd.DataFrame): Data flows as a pandas dataframe
        """

    def build_ddg(self, clear: bool = True) -> None:
        """Build the data dependency graph"""
        consume = ConsumeFacts(conf=self.opt)

        heap_flows, data_flows, call_return_flows = consume.process_and_get_facts_data()

        # Remove all stray nodes in the graph
        if clear:
            self._clear_all_nodes()

        # Process heap flows
        self._populate_heap_edges(heap_flows)

        # Process Data flows
        self._populate_dataflow_edges(data_flows)

        # Process call return flows
        self._populate_callreturn_edges(call_return_flows)

        Log.info("Populating entrypoints")
