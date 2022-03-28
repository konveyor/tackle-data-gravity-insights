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

from neomodel import StringProperty, IntegerProperty, ArrayProperty, JSONProperty, StructuredRel
from neomodel.properties import ArrayProperty, IntegerProperty, StringProperty, JSONProperty

__author__ = "Rahul Krishna"
__license__ = "Apache License"
__version__ = "1.0"
__maintainer__ = "Rahul Krishna"
__email__ = "rkrsn@ibm.com"
__status__ = "Research Prototype"

class TransactionRead(StructuredRel):
    """ Transaction Read
    """
    txid = IntegerProperty(required=True)
    tx_meth = StringProperty(required=True)
    action = StringProperty(required=True)

class TransactionWrite(StructuredRel):
    """ Transaction Write
    """
    txid = IntegerProperty(required=True)
    tx_meth = StringProperty(required=True)
    action = StringProperty(required=True)

class HeapCarriedRelationship(StructuredRel):
    """ A heap carried relationship between a pair of methods
    """
    pmethod = JSONProperty(required=False)
    nmethod = JSONProperty(required=False)
    weight = IntegerProperty(required=True)
    heap_object = JSONProperty(required=False)
    context = ArrayProperty(JSONProperty(), required=False)


class DataRelationship(StructuredRel):
    """ A data flow relationship between a pair of methods
    """
    pmethod = JSONProperty(required=False)
    nmethod = JSONProperty(required=False)
    weight = IntegerProperty(required=True)
    context = ArrayProperty(JSONProperty(), required=False)

class CallReturnRelationship(StructuredRel):
    """ A call-return relationship between a pair of methods
    """
    pmethod = JSONProperty(required=False)
    nmethod = JSONProperty(required=False)
    weight = IntegerProperty(required=True)
    pcontext = JSONProperty(required=False)
    ncontext = JSONProperty(required=False)
    