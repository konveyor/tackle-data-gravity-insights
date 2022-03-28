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

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      ArrayProperty, RelationshipTo)
from .relationships import (HeapCarriedRelationship, DataRelationship,
                            CallReturnRelationship, TransactionWrite, TransactionRead)

from neomodel.properties import (ArrayProperty,
                                 IntegerProperty, UniqueIdProperty, StringProperty, BooleanProperty)
from neomodel.relationship_manager import RelationshipFrom

__author__ = "Rahul Krishna"
__license__ = "Apache 2.0"
__version__ = "1.0"
__maintainer__ = "Rahul Krishna"
__email__ = "rkrsn@ibm.com"
__status__ = "Research Prototype"


class MethodNode(StructuredNode):
    """ A basic node to be inherited. Every node has 3 relationships:
        1. Heap relationship
        2. Call return relationship
        3. Data flow relationship

        In addition to the base node properties, also introduces the following properties:
        1. node id
        2. node class
        3. node method
        4. node reachable contexts
    """
    # Properties of the node
    node_id = UniqueIdProperty()
    node_name = StringProperty(required=True)
    node_class = StringProperty(required=True)
    node_class_name = StringProperty(required=True)
    node_method = StringProperty(required=True, unique_index=True)

    # Relationships
    heap_flows = RelationshipTo(
        "MethodNode", "HEAP_DEPENDENCY", model=HeapCarriedRelationship)
    data_flows = RelationshipFrom(
        "MethodNode", "DATA_DEPENDENCY", model=DataRelationship)
    call_ret_flows = RelationshipFrom(
        "MethodNode", "CALL_RETURN_DEPENDENCY", model=CallReturnRelationship)
    transaction_read = RelationshipFrom(
        "SQLTable", "TRANSACTION_READ", model=TransactionRead)
    transaction_write = RelationshipTo(
        "SQLTable", "TRANSACTION_WRITE", model=TransactionWrite)


class ClassNode(StructuredNode):
    """ A basic node to be inherited. Every node has 3 relationships:
        1. Heap relationship
        2. Call return relationship
        3. Data flow relationship

        In addition to the base node properties, also introduces the following properties:
        1. node id
        2. node class
        3. node method
        4. node reachable contexts
    """
    # Properties of the node
    node_id = UniqueIdProperty()
    node_class = StringProperty(required=True)
    node_short_name = StringProperty(required=True)
    node_is_entrypoint = BooleanProperty(default=False)
    partition_id = IntegerProperty()

    # Relationships
    heap_flows = RelationshipTo(
        "ClassNode", "HEAP_DEPENDENCY", model=HeapCarriedRelationship)
    data_flows = RelationshipFrom(
        "ClassNode", "DATA_DEPENDENCY", model=DataRelationship)
    call_ret_flows = RelationshipFrom(
        "ClassNode", "CALL_RETURN_DEPENDENCY", model=CallReturnRelationship)
    transaction_read = RelationshipFrom(
        "SQLTable", "TRANSACTION_READ", model=TransactionRead)
    transaction_write = RelationshipTo(
        "SQLTable", "TRANSACTION_WRITE", model=TransactionWrite)


class SQLColumn(StructuredNode):
    """ Represents a column in an SQL table """
    # uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    datatype = StringProperty(required=True)
    size = ArrayProperty(required=False)  # Decimals have precision
    is_primary = BooleanProperty(required=False, default=False)
    foreign_key = RelationshipTo('SQLColumn', 'FOREIGN_KEY')


class SQLTable(StructuredNode):
    """ Represents a table in an SQL database """
    name = StringProperty(unique_index=True, required=True)
    schema = StringProperty(required=False)
    primary_key = ArrayProperty(required=False)
    # index = JSONProperty(required=False)
    columns = RelationshipTo(SQLColumn, 'CONTAINS')
