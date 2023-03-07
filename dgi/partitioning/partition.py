################################################################################
# Copyright IBM Corporation 2021, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License a#t˚†
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################
"""
Partition DGI Graph
"""
import json
from collections import defaultdict
from pathlib import Path
from statistics import mode
from typing import Union
from neomodel.exceptions import DoesNotExist
from cargo import Cargo
from dgi.models.entities import ClassNode, MethodNode


def recommend_partitions(    # noqa:  R0913,R0914
        hostname: str, hostport, auth_str: str, output: str, partitions: int,
        seed_input: Union[Path, None] = None, verbosity: bool = True) -> None:
    """Recommend partitions with CARGO.

    Args:
        hostname(str): Neo4j hostname
        hostport(str): Neo4j port
    """
    cargo = Cargo(
        use_dgi=True,
        dgi_neo4j_hostname=hostname,
        dgi_neo4j_hostport=hostport,
        dgi_neo4j_auth=auth_str,
        verbose=verbosity,
    )

    if seed_input is None:
        _, assignments = cargo.run("auto", max_part=partitions)
    else:
        _, assignments = cargo.run("file", labels_file=seed_input)

    class_partitions = defaultdict(lambda: [])

    for method_signature, partition in assignments.items():
        try:
            dgi_method_node = MethodNode.nodes.get(
                node_method=method_signature)
            dgi_method_node.partition_id = partition
            dgi_method_node.save()
        except DoesNotExist:
            pass
        class_name = method_signature.rsplit(".", 1)[0]
        class_partitions[class_name].append(partition)

    for class_name, methods_partitions in class_partitions.items():
        try:
            dgi_class_node = ClassNode.nodes.get(node_class=class_name)
            dgi_class_node.partition_id = mode(methods_partitions)
            dgi_class_node.save()
        except DoesNotExist:
            pass

    # for class_name, methods_partitions in class_partitions.items():
    #     class_partitions[class_name] = mode(methods_partitions)

    with open(Path(output).joinpath('partitions.json'), 'w+', encoding='utf-8') as partitions_file:
        json.dump(assignments, partitions_file, indent=4, sort_keys=True)
