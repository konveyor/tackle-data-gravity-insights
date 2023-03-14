# pylint: disable=R0801
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
Schema Loader

This module is responsible for loading the schema into the GraphDB
"""

from dgi.utils.progress_bar_factory import ProgressBarFactory
from dgi.models import SQLColumn, SQLTable
from dgi.utils.logging import Log


def remove_all_nodes():
    """Clears existing nodes from the graph"""
    all_nodes = SQLColumn.nodes.all()
    for node in all_nodes:
        node.delete()
    all_nodes = SQLTable.nodes.all()
    for node in all_nodes:
        node.delete()


def process_foreign_keys(all_foreign_keys: list):
    """Processes the foreign key relations into the graph

    Args:
        all_foreign_keys (list): A list of foreign keys from the schema
    """
    Log.info("Processing foreign keys:")
    with ProgressBarFactory.get_progress_bar() as prog_bar:
        for entry in prog_bar.track(all_foreign_keys, total=len(all_foreign_keys)):
            my_table_name = entry[0]
            my_column_name = entry[1]
            ref_table_name = entry[2]
            ref_column_name = entry[3]
            # Log.info(f"Processing foreign key from {my_table_name}.{my_column_name} to {ref_table_name}.{ref_column_name}")
            my_tab = SQLTable.nodes.get(name=my_table_name)
            if my_tab:
                my_col = my_tab.columns.get(name=my_column_name)
                if my_col:
                    ref_tab = SQLTable.nodes.get(name=ref_table_name)
                    if ref_tab:
                        ref_col = ref_tab.columns.get(name=ref_column_name)
                        if ref_col:
                            # Log.info(f"Connecting {my_tab.name}.{my_col.name} to {ref_tab.name}.{ref_col.name}")
                            my_col.foreign_key.connect(ref_col)
                        else:
                            Log.info(
                                f"*** Error: Could not find reference column: {ref_column_name}"
                            )
                    else:
                        Log.info(
                            f"*** Error: Could not find reference table: {ref_table_name}"
                        )
                else:
                    Log.info(f"*** Error: Could not find self column: {my_column_name}")
            else:
                Log.info(f"*** Error: Could not find self table: {my_table_name}")


def load_graph(result):
    """Populates the graph from a dictionary"""
    all_foreign_keys = []

    Log.info("Processing schema tables:")
    with ProgressBarFactory.get_progress_bar() as prog_bar:
        for schema in prog_bar.track(result["tables"], total=len(result["tables"])):
            # Log.info(schema["table_name"])
            table = SQLTable.nodes.get_or_none(name=schema["table_name"])
            if table:
                table.schema = schema["schema"]
                table.primary_key = schema["primary_key"]
                table.index = schema["index"]
                table.save()
            else:
                table = SQLTable(
                    name=schema["table_name"],
                    schema=schema["schema"],
                    primary_key=schema["primary_key"],
                    index=schema["index"],
                ).save()
            for column in schema["columns"]:
                name = column["name"]
                # Log.info(f" - {name}")
                col = table.columns.get_or_none(name=name)
                if col:
                    col.datatype = column["type"]
                    if column["name"] in schema["primary_key"]:
                        col.is_primary = True
                    col.save()
                else:
                    # col = SQLColumn(name=column["name"], datatype=column["type"], size=column["size"])
                    col = SQLColumn(name=column["name"], datatype=column["type"])
                    if column["name"] in schema["primary_key"]:
                        col.is_primary = True
                    col.save()
                    table.columns.connect(col)

                # process foreign keys
                if column["references"]:
                    all_foreign_keys.append(
                        (
                            schema["table_name"],
                            name,
                            column["references"]["table"],
                            column["references"]["column"],
                        )
                    )

    if len(all_foreign_keys) > 0:
        process_foreign_keys(all_foreign_keys)
    else:
        Log.warn("No foreign key relationships found.")
