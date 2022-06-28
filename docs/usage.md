---
layout: default
title: Installation & Usage
nav_order: 2
---
# Installation

Tackle Data Gravity Insights is written in Python and can be installed using the Python package manager `pip`.

```bash
pip install tackle-dgi
```
# Usage

You will need an instance of Neo4j to store the graphs that `dgi` creates. You can start one up in a docker container and set an environment variable to let `dgi` know where to find it.

```bash
docker run -d --name neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH="neo4j/tackle" \
    neo4j

export NEO4J_BOLT_URL="bolt://neo4j:tackle@localhost:7687"    
```

You can now use the `dgi` command to load information about your application into the graph database.

```man
dgi --help

Usage: dgi [OPTIONS] COMMAND [ARGS]...

  Tackle Data Gravity Insights

Options:
  -n, --neo4j-bolt TEXT           Neo4j Bolt URL
  -a, --abstraction TEXT          The level of abstraction to use when
                                  building the graph. Valid options are:
                                  class, method, or full.  [default: class]
  -q, --quiet / -v, --verbose     Be more quiet/verbose  [default: verbose]
  -c, --clear / -dnc, --dont-clear
                                  Clear (or don't clear) graph before loading
                                  [default: clear]
  --help                          Show this message and exit.

Commands:
  c2g   This command loads Code dependencies into the graph
  s2g   This command parses SQL schema DDL into a graph
  tx2g  This command loads DiVA database transactions into a graph
```
