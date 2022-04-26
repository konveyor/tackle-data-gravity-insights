# Getting Started Guide

This guide will get you started using the various commands for data Gravity Insights. Before attempting these steps, make sure that you have read [Set up your Development Environment](development.md)


## 1. Installation

  - Tackle Data Gravity Insights is written in Python and can be installed using the Python package manager `pip`.

    ```bash
    pip install tackle-dgi
    ```
  - Requirements: This project requires the following softwares/packages to be installed on the machine.

       - [Docker Desktop](https://www.docker.com/products/docker-desktop)
       - [wget](https://pypi.org/project/wget/)

  - You will need an instance of Neo4j to store the graphs that `dgi` creates. You can start one up in a docker container.

    ```bash
    docker run -d --name neo4j \
        -p 7474:7474 \
        -p 7687:7687 \
        -e NEO4J_AUTH="neo4j/tackle" \
        neo4j
    ```
  
  - We set an environment variable to let `dgi` know where to find this neo4j container.
    ```bash
    export NEO4J_BOLT_URL="bolt://neo4j:tackle@localhost:7687"    
    ```

  - You can now use the `dgi` command to load information about your application into the graph database. We start with `dgi --help`. This should produce:

    ```man
    Usage: dgi [OPTIONS] COMMAND [ARGS]...

      Tackle Data Gravity Insights

    Options:
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
      s2g   This command parses SQL schema DLL into a graph
      tx2g  This command loads DiVA database transactions into a graph

    ```

## 2. Setting up a Sample Application to analyze

This is a demonstration of the usage of DGI. For this, we'll use [daytrader7](https://github.com/WASdev/sample.daytrader7) as an example. Feel free to follow along with your own application and your personal directories. But, keep track of the _directories_ where the application _source code_ and the _built jar/war/ear_ reside and replace them appropriately below.

1. Let's download a copy of our sample application and build it.
  
    ```sh
    # Download and extract the demo application
    wget -c https://github.com/WASdev/sample.daytrader7/archive/refs/tags/v1.4.tar.gz -O - | tar -xvz -C demo/sample-application
    # Now build the application
    docker run --rm -v $(pwd)/demo/sample-application/sample.daytrader7-1.4:/build maven:3.8.4-openjdk-8-slim mvn --file=/build/pom.xml install
    ```

    This will create an EAR file called `daytrader-ee7-1.0-SNAPSHOT.ear` in `demo/sample-application/sample.daytrader7-1.4/daytrader-ee7/target` directory.

2. For convenience, let's put the generated `daytrader-ee7-1.0-SNAPSHOT.ear` in the `demo/code2graph-samples/doop-input` folder
  
    ```sh
    cp demo/sample-application/sample.daytrader7-1.4/daytrader-ee7/target/daytrader-ee7-1.0-SNAPSHOT.ear demo/code2graph-samples/doop-input
    ```

## 3. Running code2graph

In this step, we'll run code2graph to populate the graph with various static code interaction features pertaining to object/dataflow dependencies and their respective lifecycle information.

1) First, we'll run [DOOP](https://bitbucket.org/yanniss/doop/src/master/) to process the compiled `*.jar` files. For ease of use, DOOP has been pre-compiled and hosted as a docker container in quay.io/rkrsn/doop-main. We'll use that for this demo. 

  ```sh
  docker run -it --rm -v $(pwd)/demo/code2graph-samples/doop-input:/root/doop-data/input -v $(pwd)/demo/code2graph-samples/doop-output:/root/doop-data/output quay.io/rkrsn/doop-main:latest rundoop
  ```

   - Running DOOP may roughly takes 5-6 mins

   - We used the `demo/code2graph-samples/doop-input/` folder from Step (2.2) above to store the the compiled jars, wars, and ears
  
  - We used a new folder `demo/code2graph-samples/doop-output` to save all the information (formatted as *.csv files) gathered from DOOP.

2) After gathering the data with DOOP, we'll now run code2graph to synthesize DOOP output into a graph stored on neo4j. 
  
  - The syntax for code2graph can be see with `dgi c2g --help`. Below:
    
    ```sh
    $ dgi c2g
    
    Usage: dgi c2g [OPTIONS]

    This command loads Code dependencies into the graph

    Options:
      -i, --input DIRECTORY  DOOP output facts directory.  [required]
      --help                 Show this message and exit.
    ```

  - We'll run code2graph by pointing it to the doop generated facts from step 1. above:
  
    ```sh
    dgi --abstraction [class|method|full] [--clear] [--verbose] c2g --input=demo/code2graph-samples/doop-output
    ```

    After successful completion, you should see:

    ```bash
    ❯ dgi --clear --abstraction class --clear --verbose c2g --input=demo/code2graph-samples/doop-output
    Graph generator started...
    Verbose mode: ON
    Building Graph...
    [INFO] Clear flag detected... Deleting pre-existing ClassNodes nodes.
    [INFO] Populating heap carried dependencies edges
    100%|██████████| 7122/7122 [00:30<00:00, 234.78it/s]
    [INFO] Populating dataflow edges
    100%|██████████| 5022/5022 [00:08<00:00, 562.53it/s]
    [INFO] Populating call-return dependencies edges
    100%|██████████| 7052/7052 [00:14<00:00, 489.56it/s]
    Graph build complete
    [INFO] Built data dependency graph successfully
    ```

## 4. Running schema2graph

1) To run scheme to graph, use `dgi [OPTIONS] s2g --input=<path/to/ddl>`. For this demo, we have a sample DDL for daytrader at `demo/schema2graph-samples/daytrader-orcale.ddl`, let us use that:

    ```sh
    dgi --clear --verbose s2g --input=demo/schema2graph-samples/daytrader-orcale.ddl
    ```
    
    This should give us:

    ```sh
    Clearing graph...
    Building Graph...
    Processing schema tables:
    100%|██████████| 12/12 [00:00<00:00, 69.40it/s]
    0it [00:00, ?it/s]
    Processing foreign keys:
    Graph build complete
    ```

## 5. Populating Database Transactions with DiVA

Here we'll first use [Tackle-DiVA](https://github.com/konveyor/tackle-diva) to infer transaction traces from the source code. DiVA is available as a docker image, so we just need to run DiVA by pointing to the source code directory and the desired output directory (for which we'll user the demo folder again). 

1. Run the following command to get the transaction traces from DiVA:

    ```bash
    docker run --rm -v $(pwd)/demo/sample-application/sample.daytrader7-1.4:/app -v $(pwd)/demo/tx2graph-samples:/diva-distribution/output quay.io/konveyor/tackle-diva
    ```

    This should output 6 files in the `demo/tx2graph-samples` folder. One of these will be a json file called `transaction.json` with all the transactions. 

2. We'll now run DGI's `tx2g` command to populate the graph with SQL tables, transaction data, and their relationships to the code. 
   
   ```sh
   dgi --abstraction class --clear --verbose tx2g --input=demo/tx2graph-samples/transaction.json
   ```

   After a successful run, you'll see:
   
   ```sh
   Verbose mode: ON
   [INFO] Clear flag detected... Deleting pre-existing SQLTable nodes.
   Building Graph...
   [INFO] Populating transactions
   100%|██████████| 158/158 [00:01<00:00, 125.73it/s]
   Graph build complete
   ```

## 6. (Optional) Creating an offline dump of the neo4j DGI graph

We'll save the graph generated so far locally for further analysis. This enables us to use a free version of Neo4J Bloom to interact with the graph.

1. First we stop the neo4j container
   
   ```sh
   docker compose --project-directory=.devcontainer stop neo4j
   ```
   
2. Then, we'll use `neo4j-admin` to dump the DB.
   
   ```sh
   docker compose --project-directory=.devcontainer run neo4j bin/neo4j-admin dump --to=/data/DGI.dump
   ```

   You'll now find a `DGI.dump` file, which has the entire DB with code2graph, schema2graph, and tx2graph.

## Using Neo4J Desktop explore the graph

In order to explore the neo4j graph, visit [http://localhost:7474/browser/](http://localhost:7474/browser/). Then,

* Under connect URL, select `neo4j://` and enter: `localhost:7687`
  
* Under username, enter: `neo4j`

* Under password, enter: `tackle`
  
This should bring you to the browser page where you can explore the DGI graph.
