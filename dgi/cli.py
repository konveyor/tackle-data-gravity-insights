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
Tackle Data Gravity Insights

Command Line Interface (CLI) for Tackle Data Gravity Insights
"""
import importlib.resources
import json
import os
import sys
from pathlib import Path

import rich_click as click
from neomodel import config
from simple_ddl_parser import parse_from_file

# Import our packages
from dgi.code2graph import ClassGraphBuilder, MethodGraphBuilder
from dgi.partitioning.partition import recommend_partitions

from dgi.schema2graph import schema_loader
from dgi.tx2graph import ClassTransactionLoader, MethodTransactionLoader
from dgi.utils.parse_config import Config
from dgi.utils.logging import Log

######################################################################
# cli - Grouping for sub commands
######################################################################


@click.group()
@click.option(
    "--neo4j-bolt",
    "-n",
    envvar="NEO4J_BOLT_URL",
    default="neo4j://neo4j:konveyor@localhost:7687",
    help="Neo4j Bolt URL",
)
@click.option(
    "--quiet",
    "-q",
    required=False,
    help="Be more quiet",
    default=False,
    is_flag=True,
    show_default=True,
)
@click.option(
    "--validate",
    "-v",
    help="Validate but don't populate graph",
    default=False,
    is_flag=True,
)
@click.option(
    "--clear",
    "-c",
    help="Clear graph before loading",
    default=False,
    is_flag=True,
    show_default=True,
)
@click.pass_context
def cli(ctx, validate, quiet, clear, neo4j_bolt):
    """Tackle Data Gravity Insights"""
    ctx.ensure_object(dict)
    ctx.obj["validate"] = validate
    ctx.obj["verbose"] = not quiet
    ctx.obj["clear"] = clear
    ctx.obj["bolt"] = neo4j_bolt

    # Configure Neo4J
    config.DATABASE_URL = ctx.obj["bolt"]
    config.ENCRYPTED_CONNECTION = False


######################################################################
# schema2graph - Populates the graph from an SQL schema DDL
######################################################################
@cli.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True),
    required=True,
    help="The SQL/DDL file to load into the graph",
)
@click.option(
    "--output", "-o", required=False, help="The JSON file to write the schema to"
)
@click.pass_context
def s2g(ctx, input, output):  # pylint: disable=redefined-builtin
    """Schema2Graph parses SQL schema (*.DDL file) into the graph"""

    # Read the DDL file
    input = Path(input)
    Log.info(f"Reading: {input.absolute()}")
    result = None
    try:
        result = parse_from_file(input, group_by_type=True)
    except FileNotFoundError as error:
        raise click.ClickException(error)

    # Optionally write it output to json
    if output:
        Log.info(f"Writing: {output}")
        with open(output, "w", encoding='utf-8') as file:
            contents = json.dumps(result, indent=4)
            file.write(contents)

    if ctx.obj["validate"]:
        Log.info(f"File [{input}] validated.")
        sys.exit(0)

    if ctx.obj["clear"]:
        Log.warn("Clear flag is turned ON. Clearing graph.")
        schema_loader.remove_all_nodes()

    Log.info("Building Graph..")
    schema_loader.load_graph(result)
    Log.info("Graph build complete")


######################################################################
#  tx2graph - Loads output from DiVA into graph
######################################################################
@cli.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True),
    required=True,
    help="DiVA Transaction JSON file",
)
@click.option(
    "--abstraction",
    "-a",
    type=click.Choice(["class", "method", "full"]),
    default="full",
    help="The level of abstraction to use when building the graph",
    show_default=True,
)
@click.option(
    "--force-clear",
    "-fc",
    help="Clear all nodes in the graph before loading. WARNING: THERE IS REASON THIS IS HIDDEN. ONLY USE "
    "FOR TESTING!",
    default=False,
    is_flag=True,
    show_default=True,
    hidden=True,
)
@click.pass_context
def tx2g(ctx, input, abstraction, force_clear):  # pylint: disable=redefined-builtin
    """Transaction2Graph add edges denoting CRUD operations to the graph."""

    if ctx.obj["verbose"]:
        Log.info("Verbose mode: ON")

    class_transaction_loader = ClassTransactionLoader()
    method_transaction_loader = MethodTransactionLoader()

    if abstraction.lower() == "full":
        if ctx.obj["validate"]:
            Log.info(
                f"Validate mode: abstraction level is {abstraction.lower()}")

            sys.exit()

        class_transaction_loader.load_transactions(
            input, clear=ctx.obj["clear"])
        # We don't want to clear the table node twice.
        # Otherwise, we'll lose the table nodes created above
        method_transaction_loader.load_transactions(input, clear=False)

    elif abstraction.lower() == "class":
        if ctx.obj["validate"]:
            Log.info(
                f"Validate mode: abstraction level is {abstraction.lower()}"
            )
            sys.exit()
        class_transaction_loader.load_transactions(
            input, clear=ctx.obj["clear"], force_clear=force_clear
        )

    elif abstraction.lower() == "method":
        if ctx.obj["validate"]:
            Log.info(
                f"Validate mode: abstraction level is {abstraction.lower()}"
            )
            sys.exit()

        method_transaction_loader.load_transactions(
            input, clear=ctx.obj["clear"], force_clear=force_clear
        )

    else:
        raise click.BadArgumentUsage(
            "Not a valid abstraction level. Valid options are 'class', 'method', 'full'."
        )

    Log.info("Transactions populated")


######################################################################
#  code2graph - Imports code dependencies into the graph
######################################################################
@cli.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, resolve_path=True, file_okay=False),
    required=True,
    help="DOOP output facts directory.",
)
@click.option(
    "--abstraction",
    "-a",
    type=click.Choice(["class", "method", "full"]),
    default="full",
    help="The level of abstraction to use when building the graph",
    show_default=True,
)
@click.pass_context
def c2g(ctx, input, abstraction):  # pylint: disable=redefined-builtin
    """Code2Graph add various program dependencies (i.e., call return, heap, and data) into the graph"""

    Log.info("code2graph generator started.")

    if ctx.obj["verbose"]:
        Log.info("Verbose mode: ON")

    # -------------------------
    # Initialize configurations
    # -------------------------
    proj_root = importlib.resources.files("dgi.code2graph")
    usr_cfg = Config(config_file=proj_root.joinpath("etc", "config.yml"))  # pylint: disable=E1121
    usr_cfg.load_config()

    # Add the input dir to configuration.
    usr_cfg.set_config(key="GRAPH_FACTS_DIR", val=input)

    # ---------------
    # Build the graph
    # ---------------

    Log.info("Building Graph.")

    class_g_builder = ClassGraphBuilder(usr_cfg)
    method_g_builder = MethodGraphBuilder(usr_cfg)

    if abstraction.lower() == "full":
        if ctx.obj["validate"]:
            Log.info(
                "Validate mode: abstraction level is {abstraction.lower()}"
            )
            sys.exit()
        Log.info("Full level abstraction adds both Class and Method nodes.")
        class_g_builder.build_ddg(clear=ctx.obj["clear"])
        method_g_builder.build_ddg(clear=ctx.obj["clear"])

    elif abstraction.lower() == "class":
        if ctx.obj["validate"]:
            Log.info(
                f"Validate mode: abstraction level is {abstraction.lower()}"
            )
            sys.exit()
        Log.info("Class level abstraction.")
        class_g_builder.build_ddg(clear=ctx.obj["clear"])

    elif abstraction.lower() == "method":
        if ctx.obj["validate"]:
            Log.info(
                f"Validate mode: abstraction level is {abstraction.lower()}"
            )
            sys.exit()
        Log.info("Method level abstraction.")
        method_g_builder.build_ddg(clear=ctx.obj["clear"])

    else:
        raise click.BadArgumentUsage(
            "Not a valid abstraction level. Valid options are 'class', 'method', 'full'."
        )

    Log.info("code2graph build complete")


#########################################################################################################
#  PARTITION - Runs the CARGO partitioning algorithm on the DGI graph to recommend/refine µS partitioning
#########################################################################################################
@cli.command()
@click.option(
    "--seed-input",
    "-i",
    type=click.Path(exists=True, resolve_path=True, file_okay=True),
    default=None,
    help="A file of user desired seed partitions.",
)
@click.option(
    "--partitions-output",
    "-o",
    type=click.Path(exists=True, resolve_path=True, file_okay=True),
    default=Path(os.getcwd()),
    help="A destination to save the final partitions.",
)
@click.option(
    "--partitions",
    "-k",
    type=int,
    default=None,
    help="Number of desired partitions. If no number is provided, CARGO will interpret a sane partitioning "
    "strategy.",
    show_default=True,
)
@click.pass_context
def partition(ctx, seed_input, partitions_output, partitions):
    """Partition is a command runs the CARGO algorithm to (re-)partition a monolith into microservices"""
    Log.info("Partitioning the monolith with CARGO")

    # Process the bolt url to be used by CARGO
    if "bolt://" in ctx.obj["bolt"]:
        # Strip scheme (in case it starts with bolt://)
        bolt_url = ctx.obj["bolt"].removeprefix("bolt://")
    elif "neo4j://" in ctx.obj["bolt"]:
        # Strip scheme (in case it starts with neo4j://)
        bolt_url = ctx.obj["bolt"].removeprefix("neo4j://")
    elif "https://" in ctx.obj["bolt"]:
        # Strip scheme (in case it starts with https://)
        bolt_url = ctx.obj["bolt"].removeprefix("https://")

    bolt_url = ctx.obj["bolt"].removeprefix("neo4j://")  # Strip scheme
    auth_str, netloc = bolt_url.split("@")
    hostname, hostport = netloc.split(":")
    recommend_partitions(hostname, hostport, auth_str,
                         partitions_output, partitions, seed_input)
