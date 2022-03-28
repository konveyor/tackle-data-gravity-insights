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

# Install CLI for development with:
#   pip install --editable .
from tqdm import tqdm
from dgi.models import SQLColumn, SQLTable

def remove_all_nodes():
    """ Clears existing nodes from the graph """
    all_nodes = SQLColumn.nodes.all()
    for node in all_nodes:
        node.delete()
    all_nodes = SQLTable.nodes.all()
    for node in all_nodes:
        node.delete()

def load_graph(result):
    """ Populates the graph from a dictionary """
    all_foreign_keys = []

    print("Processing schema tables:")
    for schema in tqdm(result["tables"], total=len(result["tables"])):
        # print(schema["table_name"])
        table = SQLTable.nodes.get_or_none(name=schema["table_name"])
        if table:
            table.schema = schema["schema"]
            table.primary_key=schema["primary_key"]
            table.index=schema["index"]
            table.save()
        else:
            table = SQLTable(
                name=schema["table_name"], 
                schema=schema["schema"], 
                primary_key=schema["primary_key"],
                index=schema["index"]
            ).save()
        for column in schema["columns"]:
            name = column["name"]
            # print(f" - {name}")
            col = table.columns.get_or_none(name=name)
            if col:
                col.datatype=column["type"]
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
                all_foreign_keys.append((schema["table_name"],name,column["references"]["table"],column["references"]["column"]))
                
    print("Processing foreign keys:")
    for entry in tqdm(all_foreign_keys, total=len(all_foreign_keys)):
        my_table_name = entry[0]
        my_column_name = entry[1]
        ref_table_name = entry[2]
        ref_column_name = entry[3]
        # print(f"Processing foreign key from {my_table_name}.{my_column_name} to {ref_table_name}.{ref_column_name}")
        my_tab = SQLTable.nodes.get(name=my_table_name)
        if my_tab:
            my_col = my_tab.columns.get(name=my_column_name)
            if my_col:                    
                ref_tab = SQLTable.nodes.get(name=ref_table_name)
                if ref_tab:
                    ref_col = ref_tab.columns.get(name=ref_column_name)
                    if ref_col:
                        # print(f"Connecting {my_tab.name}.{my_col.name} to {ref_tab.name}.{ref_col.name}")
                        my_col.foreign_key.connect(ref_col)
                    else:
                        print(f"*** Error: Could not find reference column: {ref_column_name}")
                else:
                    print(f"*** Error: Could not find reference table: {ref_table_name}")
            else:  
                print(f"*** Error: Could not find self column: {my_column_name}")
        else:
            print(f"*** Error: Could not find self table: {my_table_name}")
        
