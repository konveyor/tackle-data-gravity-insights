---
layout: default
title: Getting Started
nav_order: 4
---
# Getting Started Guide

This guide will get you started using the various commands for Data Gravity Insights (DGI). If you would like to contribute to the project you can [Set up your Development Environment](development.md). Regular users can just follow the steps below:

## Prerequisites

If this is your first time using Tackle Data Gravity Insights you must first install some prerequisite software. Here are  the instructions to install the [Prerequisites](/docs/prerequisites.md)

## Step 1. Install Data Gravity Insights CLI

There are two ways to install the `dgi` command line interface:

### Install DGI CLI system wide

You can install `dgi` globally into your system packages as root with:

```bash
sudo pip install tackle-dgi
```

This will make the `dgi` command globally available. You can then run it from anywhere on your computer.

### Install DGI CLI locally

If you do not want to install it system wide you can install `dgi` locally with:

```bash
pip install tackle-dgi
```

This will install the `dgi` command locally under your home folder in a hidden folder called: `~/.local/bin`. If you choose this approach, you must add this folder to your `PATH` with:

```bash
export PATH=$PATH:$HOME/.local/bin
```

### Run Neo4J Community Edition container

You will need an instance of Neo4j to store the graphs that `dgi` creates. You can start one up in a container using `docker` or `podman` (to use `podman` just substitute `podman` for `docker` in the command below).

  ```bash
  docker run -d --name neo4j \
      -p 7474:7474 \
      -p 7687:7687 \
      -v neo4j:/data \
      -e NEO4J_AUTH="neo4j/tackle" \
      docker.io/neo4j:latest
  ```

You must set an environment variable to let `dgi` know where to find this neo4j container.

```bash
export NEO4J_BOLT_URL="bolt://neo4j:tackle@localhost:7687"    
```

### Installation complete

You can now use the `dgi` command to load information about your application into the graph database. We start with `dgi --help`. This should produce:

```man
Usage: dgi [OPTIONS] COMMAND [ARGS]...

  Tackle Data Gravity Insights

Options:
  -n, --neo4j-bolt TEXT  Neo4j Bolt URL
  -q, --quiet            Be more quiet
  -c, --clear            Clear graph before loading  [default: True]
  --help                 Show this message and exit.

Commands:
  c2g   This command loads Code dependencies into the graph
  s2g   This command parses SQL schema DDL into a graph
  tx2g  This command loads DiVA database transactions into a graph
```

## Step 2. Setting up a Sample Application to analyze

This is a demonstration of the usage of DGI. For this, we'll use [daytrader7](https://github.com/WASdev/sample.daytrader7) as an example. Feel free to follow along with your own application and your personal directories. But, keep track of the _directories_ where the application _source code_ and the _built jar/war/ear_ reside and replace them appropriately below.

Let's download a copy of our sample application and build it. If you already have your own application ear file you can skip this step.
  
1. First let's create a folder called `demo` and change into it to extract the code to:

    ```bash
    mkdir demo
    cd demo
    ```

2. If you have your own Java application, you can skip this step. If you want to use the DayTrader7 demo, you must load and extract the demo DayTrader7 application using `wget` (if you don't have `wget` you can install it here: [install wget](https://pypi.org/project/wget/)):

    ```bash
    wget -c https://github.com/WASdev/sample.daytrader7/archive/refs/tags/v1.4.tar.gz -O - | tar -xvz -C .
    ```

3. Now build the application

    ```bash
    docker run --rm -v $(pwd)/sample.daytrader7-1.4:/build docker.io/maven:3.8.4-openjdk-8-slim mvn --file=/build/pom.xml install
    ```

    This will create an EAR file called `daytrader-ee7-1.0-SNAPSHOT.ear` in `sample.daytrader7-1.4/daytrader-ee7/target` directory.

## Step 3. Run code2graph

In this step, we'll run code2graph to populate the graph with various static code interaction features pertaining to object/dataflow dependencies and their respective lifecycle information.

Code2graph uses the output from a tool called [DOOP](https://bitbucket.org/yanniss/doop/src/master/). 

1. First let's prepare an input and output folders for `doop` called `doop-input` and `doop-output` respectively and copy the generated `daytrader-ee7-1.0-SNAPSHOT.ear` file in the `doop-input` folder. You should already be in the `demo` folder from the previous steps before making these directories:
  
    ```bash
    mkdir doop-input
    mkdir doop-output
    cp sample.daytrader7-1.4/daytrader-ee7/target/daytrader-ee7-1.0-SNAPSHOT.ear doop-input
    ```

    _Note: if you are using your own application ear file, copy it into the `doop-input` folder_

    Just to double check, you should see the DayTrader ear or your ear file in the `doop-input` folder:

    ```bash
    $ ls doop-input/
    daytrader-ee7-1.0-SNAPSHOT.ear
    ```

2. Next, we'll run DOOP to process the compiled `*.jar` files. 

    For ease of use, DOOP has been pre-compiled and hosted as a docker image at `quay.io/rkrsn/doop-main`. We'll use that for this demo.

    ```bash
    docker run -it --rm -v $(pwd)/doop-input:/root/doop-data/input -v $(pwd)/doop-output:/root/doop-data/output quay.io/rkrsn/doop-main:latest rundoop
    ```

    _Note: Running DOOP may roughly takes 5-6 mins_

    Let's review what we have done so far:

      - We used the `doop-input/` folder to store the the compiled jars, wars, and ears

      - We used a new folder `doop-output` to save all the information (formatted as *.csv files) gathered from DOOP.

3. After gathering the data with DOOP, we'll now run code2graph to synthesize DOOP output into a graph stored on neo4j. 
  
    The syntax for code2graph can be see with `dgi c2g --help`. Below:

    ```sh
    $ dgi c2g
    
    Usage: dgi c2g [OPTIONS]

      This command loads Code dependencies into the graph

    Options:
      -i, --input DIRECTORY           DOOP output facts directory.  [required]
      -a, --abstraction [class|method|full]
                                      The level of abstraction to use when
                                      building the graph  [default: class]
      --help                          Show this message and exit.
    ```

   We'll run code2graph by pointing it to the doop generated facts from the step above:
  
    ```sh
    dgi --clear c2g --abstraction=class --input=doop-output
    ```
    
    Note that we could have passed in [class|method|full] as the abstraction. If you decide to run with the `method` or `full` level of abstraction, make sure you use the same abstraction level when running with `tx2g` as well.

    After successful completion, you should see:

    ```bash
    $ dgi --clear c2g --abstraction=class --input=doop-output
    code2graph generator started...
    Verbose mode: ON
    Building Graph...
    [INFO] Populating heap carried dependencies edges
    100%|█████████████████████| 7138/7138 [01:37<00:00, 72.92it/s]
    [INFO] Populating dataflow edges
    100%|█████████████████████| 5022/5022 [01:31<00:00, 54.99it/s]
    [INFO] Populating call-return dependencies edges
    100%|█████████████████████| 7052/7052 [02:26<00:00, 48.30it/s]
    [INFO] Populating entrypoints
    code2graph build complete
    ```

## Step 4. Running schema2graph

To run scheme to graph, use `dgi [OPTIONS] s2g --input=<path/to/ddl>`. For this demo, we have a sample DDL for daytrader at `demo/schema2graph-samples/daytrader-orcale.ddl`, let us use that:

```sh
dgi --clear s2g --input=./sample.daytrader7-1.4/daytrader-ee7-web/src/main/webapp/dbscripts/oracle/Table.ddl
```

This should give us:

```sh
Clearing graph...
Building Graph...
Processing schema tables:
100%|████████████████████| 12/12 [00:00<00:00, 69.40it/s]
0it [00:00, ?it/s]
Processing foreign keys:
Graph build complete
```

## Step 5. Populating Database Transactions with DiVA

Here we'll first use [Tackle-DiVA](https://github.com/konveyor/tackle-diva) to infer transaction traces from the source code. DiVA is available as a docker image, so we just need to run DiVA by pointing to the source code directory and the desired output directory (for which we'll user the demo folder again). 

1. Run the following command to get the transaction traces from DiVA:

    ```bash
    mkdir tx2graph-output
    docker run --rm -v $(pwd)/sample.daytrader7-1.4:/app -v $(pwd)/tx2graph-output:/diva-distribution/output quay.io/konveyor/tackle-diva
    ```

    This should output 6 files in the `./tx2graph-output` folder. One of these will be a json file called `transaction.json` with all the transactions.

2. We'll now run DGI's `tx2g` command to populate the graph with SQL tables, transaction data, and their relationships to the code.

   ```sh
   dgi --clear tx2g --input=./tx2graph-output/transaction.json
   ```

   After a successful run, you'll see:

   ```sh
   Verbose mode: ON
   [INFO] Clear flag detected... Deleting pre-existing SQLTable nodes.
   Building Graph...
   [INFO] Populating transactions
   100%|████████████████████| 158/158 [00:01<00:00, 125.73it/s]
   Graph build complete
   ```

## Step 6. (Optional) Creating an offline dump of the neo4j DGI graph

We'll save the graph generated so far locally for further analysis. This enables us to use a free version of Neo4J Bloom to interact with the graph.

1. First we stop the neo4j container because the data can't be backup while Neo4J is running.

   ```sh
   docker stop neo4j
   ```

2. Then, we'll use `neo4j-admin` command to dump the DB.

   ```sh
   docker run --rm -v neo4j:/data -v $(pwd):/var/dump neo4j bin/neo4j-admin dump --to=/var/dump/DGI.dump
   ```

   You'll now find a `DGI.dump` file, which has the entire DB with code2graph, schema2graph, and tx2graph in your current folder.

3. If you want to continue to use `dgi` with Neo4J don't forget to restart Neo4J:

   ```sh
   docker start neo4j
   ```  
   
## Using Neo4J Desktop explore the graph

In order to explore the neo4j graph, visit [http://localhost:7474/browser/](http://localhost:7474/browser/). Then,

* Under connect URL, select `neo4j://` and enter: `localhost:7687`
  
* Under username, enter: `neo4j`

* Under password, enter: `tackle`
  
This should bring you to the browser page where you can explore the DGI graph.

![full_graph](../../assets/images/full_graph.png)