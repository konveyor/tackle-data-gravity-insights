# Tx2Graph - Transaction Dependency Extractor

Transaction Dependency Extractor analyzes CRUD-based (Create, Read, Update, Delete) database dependencies across transaction and stores into a Neo4j graph database.

## Prerequisites

- Python 3.x
- Neo4j server

## Usage

```bash
tx2g --help
Usage: tx2g [OPTIONS]

  This command loads DiVA database transactions into a graph

Options:
  -i, --input PATH  DiVA Transaction JSON file  [required]
  -c, --clear       Clear all Table nodes before loading
  -v, --verbose     Enable Verbose mode
  --help            Show this message and exit.
```

## Getting Started

These instructions will take you step by step through generating and importing the output from Tackle-DiVA into Neo4j.

### Step 1

You must first have Java source files to scan or use a sample file. You can generate them using [Tackle-DiVA](https://github.com/konveyor/tackle-diva).

```bash
docker run --rm \
  -v </path-to-source-code-folder>:/app \
  -v $(PWD):/diva-distribution/output \
  quay.io/konveyor/tackle-diva
```

This will write the output files to the current working directory. Of course you can substitute `$(PWD)` for whatever output folder you'd like. You only need the `transaction.json` file to populate the Neo4j graph.

If you want to use the scan we have already produced from the [DayTrader7](https://github.com/WASdev/sample.daytrader7) or [TradingApp](https://github.com/saud-aslam/trading-app) application, look in the `samples` folder for `daytrader-transactions.json` and `trading-app-transactions.json` respectively.

### Step 2

Execute `tx2g` specifying the transaction JSON file using the `--input` parameter. You can optionally use `-c` to clear the graph first and `-v` for more verbose output.

```bash
tx2g --input samples/daytrader-transaction.json -c -v
```

### Step 3

Open Neo4j portal at http://localhost:7474/browser/ and query nodes.

- Show all nodes :

  ```cypher
  MATCH (a)-[]->(b) RETURN (a)-[]->(b)
  ```

- Focus on Write operation :

  ```cypher
  MATCH (a)-[:Write]->(b) RETURN (a)-[:Write]->(b)
  ```

- Focus on Read operation :

  ```cypher
  MATCH (a)-[:Read]->(b) RETURN (a)-[:Read]->(b)
  ```
  
- Delete all nodes :

  ```cypher
  MATCH (v) DETACH DELETE v
  ```
  
## Sample Queries

Find instances that have heap dependencies to transactions

```cypher
Match p=(K)-[:HEAP_DEPENDENCY]-(M:ClassNode)-[]-(N:SQLTable)-[]-(Q:ClassNode) return p
```

Find instances where multiple classes partake in a database transaction

```cypher
Match p=(M:ClassNode)-[]-(N:SQLTable)-[]-(Q:ClassNode) return p
```
