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
Tackle Data Gravity Insights

Command Line Interface (CLI) for Tackle Data Gravity Insights
"""
from argparse import ArgumentError
from email.policy import default
import os
import sys
import yaml
import json
import yaml
import click
import logging
import importlib.resources

from tqdm import tqdm
from collections import OrderedDict
from neomodel import config
from simple_ddl_parser import parse_from_file
from neomodel import config
from pathlib import Path
from collections import namedtuple
# Import our packages
from .schema2graph import schema_loader
from .code2graph import ClassGraphBuilder, MethodGraphBuilder
from .tx2graph import ClassTransactionLoader, MethodTransactionLoader
from .code2graph.utils.parse_config import Config


######################################################################
# cli - Grouping for sub commands
######################################################################


@click.group()
@click.option("--abstraction", "-a", default="class", help="The level of abstraction to use when building the graph. Valid options are: class, method, or full.", show_default=True)
@click.option("--quiet/--verbose", "-q/-v", required=False, help="Be more quiet/verbose", default=False, is_flag=True, show_default=True)
@click.option("--clear/--dont-clear", "-c/-dnc", help="Clear (or don't clear) graph before loading", default=True, is_flag=True, show_default=True)
@click.pass_context
def cli(ctx, abstraction, quiet, clear):
    """Tackle Data Gravity Insights"""
    ctx.ensure_object(dict)
    ctx.obj['abstraction'] = abstraction
    ctx.obj['verbose'] = not quiet
    ctx.obj['clear'] = clear

######################################################################
# schema2graph - Populates the graph from an SQL schema DDL
######################################################################


@cli.command()
@click.option("--input", "-i", type=click.Path(exists=True), required=True, help="The SQL/DDL file to load into the graph")
@click.option("--output", "-o", required=False, help="The JSON file to write the schema to")
@click.option("--validate", "-v", help="Validate file if OK but don't populate graph", is_flag=True, hidden=True)
@click.pass_context
def s2g(ctx, input, output, validate):
    """This command parses SQL schema DLL into a graph"""

    # Read the DDL file
    click.echo(f"Reading: {input}")
    result = None
    try:
        result = parse_from_file(input, group_by_type=True)
    except FileNotFoundError as error:
        raise click.ClickException(error)

    # Optionally write it output to json
    if output:
        click.echo(f"Writing: {output}")
        with open(output, "w") as f:
            contents = json.dumps(result, indent=4)
            f.write(contents)

    if validate:
        click.echo(f"File [{input}] validated.")
        exit(0)

    if ctx.obj['clear']:
        click.echo("Clearing graph...")
        schema_loader.remove_all_nodes()

    click.echo("Building Graph...")
    schema_loader.load_graph(result)
    click.echo("Graph build complete")


######################################################################
#  tx2graph - Loads output from DiVA into graph
######################################################################
@cli.command()
@click.option("--input", "-i", type=click.Path(exists=True), required=True, help="DiVA Transaction JSON file")
@click.option("--validate", help="Testing mode, the graph won't be built.", is_flag=True, hidden=True)
@click.pass_context
def tx2g(ctx, input, validate):
    """This command loads DiVA database transactions into a graph"""

    if ctx.obj["verbose"]:
        click.echo("Verbose mode: ON")

    # ------------------
    # Configure NeoModel
    # ------------------
    config.DATABASE_URL = os.environ.get("NEO4J_BOLT_URL")
    config.ENCRYPTED_CONNECTION = False

    # -------------------------
    # Set logging configuration
    # -------------------------
    loglevel = logging.WARNING
    if (ctx.obj["verbose"]):
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format="[%(levelname)s] %(message)s")

    class_transaction_loader = ClassTransactionLoader()
    method_transaction_loader = MethodTransactionLoader()

    if ctx.obj["abstraction"].lower() == "full":
        if validate:
            click.echo("Validate mode: abstraction level is {}".format(
                ctx.obj["abstraction"].lower()))
            sys.exit()

        class_transaction_loader.load_transactions(
            input, clear=ctx.obj['clear'])
        # We don't want to clear the table node twice.
        # Otherwise, we'll use the table nodes created above
        method_transaction_loader.load_transactions(input, clear=False)

    elif ctx.obj["abstraction"].lower() == "class":
        if validate:
            click.echo("Validate mode: abstraction level is {}".format(
                ctx.obj["abstraction"].lower()))
            sys.exit()
        class_transaction_loader.load_transactions(
            input, clear=ctx.obj['clear'])

    elif ctx.obj["abstraction"].lower() == "method":
        if validate:
            click.echo("Validate mode: abstraction level is {}".format(
                ctx.obj["abstraction"].lower()))
            sys.exit()

        method_transaction_loader.load_transactions(
            input, clear=ctx.obj['clear'])

    else:
        raise click.BadArgumentUsage(
            "Not a valid abstraction level. Valid options are 'class', 'method', 'full'.")

    click.echo("Transactions populated")


######################################################################
#  code2graph - Imports code dependencies into the graph
######################################################################
@cli.command()
@click.option("--input", "-i", type=click.Path(exists=True, resolve_path=True, file_okay=False), required=True, help="DOOP output facts directory.")
@click.option("--validate", help="Testing mode, the graph won't be built.", is_flag=True, hidden=True)
@click.pass_context
def c2g(ctx, input, validate):
    """This command loads Code dependencies into the graph"""

    click.echo("code2graph generator started...")

    if ctx.obj["verbose"]:
        click.echo("Verbose mode: ON")

    # -------------------------
    # Set logging configuration
    # -------------------------
    loglevel = logging.WARNING
    if (ctx.obj["verbose"]):
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format="[%(levelname)s] %(message)s")

    # -------------------------
    # Initialize configurations
    # -------------------------
    proj_root = importlib.resources.files('dgi.code2graph')
    usr_cfg = Config(config_file=proj_root.joinpath("etc", "config.yml"))
    usr_cfg.load_config()

    # Add the input dir to configuration.
    usr_cfg.set_config(key="GRAPH_FACTS_DIR", val=input)

    # ---------------
    # Configure Neo4J
    # ---------------
    config.DATABASE_URL = os.environ.get("NEO4J_BOLT_URL")
    config.ENCRYPTED_CONNECTION = False

    # ---------------
    # Build the graph
    # ---------------

    click.echo("Building Graph...")

    class_g_builder = ClassGraphBuilder(usr_cfg)
    method_g_builder = MethodGraphBuilder(usr_cfg)

    if ctx.obj["abstraction"].lower() == "full":
        if validate:
            click.echo("Validate mode: abstraction level is {}".format(
                ctx.obj["abstraction"].lower()))
            sys.exit()
        class_g_builder.build_ddg(clear=ctx.obj['clear'])
        # We don't want to clear the table node twice.
        # Otherwise, we'll use the table nodes created above
        method_g_builder.build_ddg(clear=ctx.obj['clear'])

    elif ctx.obj["abstraction"].lower() == "class":
        if validate:
            click.echo("Validate mode: abstraction level is {}".format(
                ctx.obj["abstraction"].lower()))
            sys.exit()
        class_g_builder.build_ddg(clear=ctx.obj['clear'])

    elif ctx.obj["abstraction"].lower() == "method":
        if validate:
            click.echo("Validate mode: abstraction level is {}".format(
                ctx.obj["abstraction"].lower()))
            sys.exit()
        method_g_builder.build_ddg(clear=ctx.obj['clear'])

    else:
        raise click.BadArgumentUsage(
            "Not a valid abstraction level. Valid options are 'class', 'method', 'full'.")

    click.echo("code2graph build complete")
