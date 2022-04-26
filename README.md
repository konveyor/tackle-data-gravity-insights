# Tackle Data Gravity Insights

[![Build Status](https://github.com/konveyor/tackle-data-gravity-insights/actions/workflows/ci-build.yml/badge.svg)](https://github.com/konveyor/tackle-data-gravity-insights/actions)
[![PyPI version](https://badge.fury.io/py/tackle-dgi.svg)](https://badge.fury.io/py/tackle-dgi)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Tackle Data Gravity Insights is a new way to gain insights into your monolithic application code so that you can better refactor it into domain driven microservices. It takes a wholistic approach to application modernization and refactoring by triangulating between code, and, data, and transactional boundaries.

Application modernization is a complex topic with refactoring being the most complicated undertaking. Current tools only look at the application source code or only at the runtime traces when refactoring. This, however, yields a myopic view that doesn't take into account data relationships and transactional scopes. This project hopes to join the three views of application, data, and transactions into a 3D view of the all of the application relationships so that you can easily discover application domains of interest and refactor them into microservices. Accordingly, DGI consists of three key components:

**1. Call-/Control-/Data-dependency Analysis (code2graph):** This is a source code analysis component that extracts various static code interaction features pertaining to object/dataflow dependencies and their respective lifecycle information. It presents this information in a graphical format with Classes as _nodes_ and their dataflow, call-return, and heap-dependency interactions _edges_.

**2. Schema:** This component of DGI infers the schema of the underlying databases used in the application. It presents this information in a graphical format with database tables and columns as _nodes_ and their relationships (e.g., foreign key, etc.) as _edges_.

**3. Transactions to graph (tx2graph):** This component of DGI leverages [Tackle-DiVA](https://github.com/konveyor/tackle-diva) to perform a data-centric application analysis. It imports a set of target application source files (*.java/xml) and provides following analysis result files. It presents this information in a graphical format with database tables and classes as _nodes_ and their transactional relationships as _edges_.

## Installation

Tackle Data Gravity Insights is written in Python and can be installed using the Python package manager `pip`.

```bash
pip install tackle-dgi
```

## Usage

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

## Demo

This is a demonstration of the usage of DGI

1. [Demonstration](https://github.com/konveyor/tackle-data-gravity-insights/tree/main/docs/demo.md)

## Running DGI

To run this project please refer to the steps in the getting started guide

1. [Getting Started](https://github.com/konveyor/tackle-data-gravity-insights/tree/main/docs/getting-started.md)

## Contributing

To contribute to this project you will need to set up your development environment and set up some files. The steps are in the following file:

1. [Set up your Developer Environment](https://github.com/konveyor/tackle-data-gravity-insights/tree/main/docs/development.md)
