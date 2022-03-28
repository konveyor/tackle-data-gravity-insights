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

import os
import re
import sys
import json
import errno
from csv import reader
from ipdb import set_trace
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple

# Add the main project path to the python path.
proj_root = Path.cwd()
sys.path.append(proj_root.__str__())

from .utils.parse_config import Config


class ConsumeFacts:
    def __init__(self, conf: Config) -> None:
        """ Take raw datalog facts and convert them to a comsumable form.

        Args:
            p_root (str): Path to the project root folder.  
            facts_dir (str): Path to the facts folder.  
            opt_cfg (Config): Other configs
        """
        self.conf = conf
        self.__setup()

    def __setup(self) -> None:
        """ Perform some setup for auxiliary paths, data structures, etc.
        """
        self.absolute_facts_dir = Path(self.conf.GRAPH_FACTS_DIR)
        self.method_info = dict()
        self.contexts = dict()

    def _jsonify_method_string(self, raw: str) -> str:
        """ Convert doop style method information to a json formatted string

        Args:
            raw (str): Method information as a doop style string

        Returns:
            str: JSON string representation of the method information
        """

        # In the method info already exists, use that...
        raw = re.sub("[(:)]", " ", raw[1:-1])
        try:
            class_name, return_type, method_sig, _ = *raw.split(),
        except ValueError:
            class_name, return_type, method_sig = *raw.split(),

        key = "::".join([class_name, method_sig])
        if key in self.method_info:
            method_dict = self.method_info[key]
        else:
            # If not, add a new instance to the dictionary
            method_dict = {
                "name": method_sig,
                "class": class_name,
                "return_type": return_type
            }
            self.method_info[key] = method_dict

        return method_dict

    def _jsonify_context(self, raw: str) -> str:
        """ Convert context string to a json string.

        Args:
            ctx_list (str): Doop format context string

        Returns:
            str: JSON string representation of the doop context

        Notes:
            Take the context information from: "[class_name_1/method_name_1/obj_name_1/id1, class_name_2/method_name_2/obj_name_2/id2]"
            And, converts it to the following format:
            "{
                {
                    "class": "class_name_1",
                    "method": "method_name_1",
                    "object": "obj_name_1",
                    "instance": id1,
                },
                {
                    "class": "class_name_2",
                    "method": "method_name_2",
                    "object": "obj_name_2",
                    "instance": id2,
                }
            }" 
        """

        raw_str = re.sub("[\[\]]", "", raw)
        raw_ctx_lst = raw_str.split(', ')

        for i, str_el in enumerate(raw_ctx_lst):
            if str_el in ("<<immutable-context>>", "<<immutable-hcontext>>", "<<string-builder>>", "<<string-buffer>>"):
                raw_ctx_lst[i] = {
                    "class": None,
                    "method": str_el,
                    "type": None,
                    "object": None,
                    "instance": 0,
                }
            elif "MockObject" in str_el:
                class_name, object_name = *str_el.split("::"),
                method_name = None
                raw_ctx_lst[i] = {
                    "class": class_name,
                    "method": method_name,
                    "type": None,
                    "object": object_name,
                    "instance": 0,
                }
            else:
                raw_substr = raw_ctx_lst[i].split('/')
                class_name, method_signature = * \
                    raw_substr[0][1:-1].split(": "),
                try:
                    method_rtype, method_name, _ = * \
                        re.sub("[(:)]", " ", method_signature).split(),
                except ValueError:
                    method_rtype, method_name = * \
                        re.sub("[(:)]", " ", method_signature).split(),

                object_name = raw_substr[1]
                instance_id = raw_substr[2]
                raw_ctx_lst[i] = {
                    "class": class_name,
                    "method": method_name,
                    "type": method_rtype,
                    "object": object_name,
                    "instance": int(instance_id)
                }

        ctx_json_str = json.dumps(raw_ctx_lst)

        # Add the found context to a dictionary.
        # NOTE: For now, we keep the values empty. In a later method (`_update_context_transistions(...)`), we update it lazily.
        self.contexts.update({ctx_json_str: {'prev': [], 'next': []}})

        return raw_ctx_lst

    def _jsonify_heap_obj(self, heapobj_str: str) -> str:
        """ Create a JSON string from raw heap object string from doop

        Args:
            heapobj_str (str): Heap object as a string

        Returns:
            str: JSON string
        """
        raw_substr = re.sub("[<:>]", "", heapobj_str)
        if raw_substr in {'string-constant', 'string-builder', 'java.lang.StringMockObject', 'null pseudo heap'}:
            heap_obj_dict = {
                "class": raw_substr,
                "method": None,
                "object": None,
                "instance": 0,
            }
        elif "MockObject" in heapobj_str:
            class_name, object_name = *heapobj_str.split("::"),
            method_name = None
            heap_obj_dict = {
                "class": class_name,
                "method": method_name,
                "object": object_name,
                "instance": 0,
            }
        else:
            raw_substr = raw_substr.split('/')
            class_name, _, method_signature = *raw_substr[0].split(" "),

            try:
                method_rtype, method_name = *method_signature.split(),
            except ValueError:
                method_name = method_signature.split()[0]
                method_rtype = None,

            object_name = raw_substr[1].split()[1]
            instance_id = raw_substr[2]
            heap_obj_dict = {
                "class": class_name,
                "method": method_name,
                "type": method_rtype,
                "object": object_name,
                "instance": int(instance_id)
            }

        return heap_obj_dict

    def _process_method_info(self, method_info_file: Path) -> None:
        """ Process method information into a dictionary for reference

        Args:
            method_info_file (Path): Path to doop method information file
        """
        self.method_info = dict()
        with open(method_info_file, "r") as file_obj:
            csv_reader = reader(file_obj, delimiter='\t')
            for row in csv_reader:
                key = "::".join(row[::-1][1:3])
                if key not in self.method_info:
                    self.method_info[key] = {
                        "name": row[1],
                        "class": row[2],
                        "return_type": row[3]
                    }

    def _process_heap_carried_dependencies(self, fact_loc: Path) -> pd.DataFrame:
        """ Process heap carried dependencies

        Args:
            fact_loc (Path): Path to the heap carried dependency flows file.

        Returns:
            pd.DataFrame: The dataframe containing processed heap carried dependencies
        """
        heap_flows_df = pd.read_csv(fact_loc, header=None, delimiter='\t')
        heap_flows_df.columns = ['context', 'heap_obj', 'prev', 'next']
        heap_flows_df.context = heap_flows_df.context.apply(
            self._jsonify_context)
        heap_flows_df.prev = heap_flows_df.prev.apply(
            self._jsonify_method_string)
        heap_flows_df.next = heap_flows_df.next.apply(
            self._jsonify_method_string)
        heap_flows_df.heap_obj = heap_flows_df.heap_obj.apply(
            self._jsonify_heap_obj)
        return heap_flows_df

    def _process_call_return_dependencies(self, calls_fact_loc: Path, returns_fact_loc: Path) -> pd.DataFrame:
        """ Process call-return dependencies

        Args:
            calls_fact_loc (Path): Path to the call dependencies file.
            returns_fact_loc (Path): Path to the return dependencies file.

        Returns:
            pd.DataFrame: The dataframe containing processed call-return dependencies
        """
        callret_flows_df = pd.read_csv(
            calls_fact_loc, header=None, delimiter='\t')
        pd.concat([callret_flows_df, pd.read_csv(
            returns_fact_loc, header=None, delimiter='\t')])
        callret_flows_df.columns = [
            'prev_context', 'prev', 'next_context', 'next']
        callret_flows_df.prev_context = callret_flows_df.prev_context.apply(
            self._jsonify_context)
        callret_flows_df.next_context = callret_flows_df.next_context.apply(
            self._jsonify_context)
        callret_flows_df.prev = callret_flows_df.prev.apply(
            self._jsonify_method_string)
        callret_flows_df.next = callret_flows_df.next.apply(
            self._jsonify_method_string)
        return callret_flows_df

    def _process_data_dependencies(self, fact_loc: Path) -> pd.DataFrame:
        """ Process data dependent instructions

        Args:
            fact_loc (Path): Path to the data dependent flows.

        Returns:
            pd.DataFrame: The dataframe containing processed data dependencies
        """
        data_flows_df = pd.read_csv(fact_loc, header=None, delimiter='\t')
        data_flows_df.columns = ['context', 'prev', 'next']
        data_flows_df.context = data_flows_df.context.apply(
            self._jsonify_context)
        data_flows_df.prev = data_flows_df.prev.apply(
            self._jsonify_method_string)
        data_flows_df.next = data_flows_df.next.apply(
            self._jsonify_method_string)
        return data_flows_df

    def get_method_info(self) -> Dict:
        """ Method information as a dictionary

        Returns:
            Dict: Method information
        """
        if not self.method_info:
            method_info_file = self.absolute_facts_dir.joinpath(
                self.conf.METHOD_INFORMATION_FILE)
            self._process_method_info(method_info_file)

        return self.method_info

    def get_contexts(self) -> set:
        """ Get context information as a dictionary

        Returns:
            Dict: Context information
        """

        assert self.contexts, "Context information has not yet been derived. Run `process_and_get_facts_data()` first."

        return self.contexts

    def process_and_get_facts_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """ Process all facts and return the data

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Heap flows, data flows, and call/return flows.
        """

        # ------------------
        # Method information
        # ------------------
        method_info_file = self.absolute_facts_dir.joinpath(
            self.conf.METHOD_INFORMATION_FILE)

        if not method_info_file.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(
                errno.ENOENT), method_info_file.__str__())

        self._process_method_info(method_info_file)

        # -----------------------------
        # Heap carried dependency flows
        # -----------------------------
        heap_facts_file = self.absolute_facts_dir.joinpath(
            self.conf.HEAP_DEPENDENCY_FILE)

        if not heap_facts_file.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(
                errno.ENOENT), heap_facts_file.__str__())

        heap_flows = self._process_heap_carried_dependencies(heap_facts_file)

        # ---------------------
        # Data dependency flows
        # ---------------------
        data_dep_facts_file = self.absolute_facts_dir.joinpath(
            self.conf.DATA_DEPENDENCY_FILE)

        if not data_dep_facts_file.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(
                errno.ENOENT), data_dep_facts_file.__str__())

        data_flows = self._process_data_dependencies(data_dep_facts_file)

        # ----------------------------
        # Call-return dependency flows
        # ----------------------------
        call_dep_facts_file = self.absolute_facts_dir.joinpath(
            self.conf.CALL_DEPENDENCY_FILE)
        return_dep_facts_file = self.absolute_facts_dir.joinpath(
            self.conf.RETURN_DEPENDENCY_FILE)

        if not call_dep_facts_file.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(
                errno.ENOENT), call_dep_facts_file.__str__())

        if not return_dep_facts_file.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(
                errno.ENOENT), return_dep_facts_file.__str__())

        call_return_flows = self._process_call_return_dependencies(
            call_dep_facts_file, return_dep_facts_file)

        return heap_flows, data_flows, call_return_flows
