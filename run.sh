#!/bin/bash

DEV_DIR=.devcontainer
CUR_DIR=$(PWD)

# STDOUT colors
RED='\033[0;31m'
DG='\033[1;30m'
NC='\033[0m' # No Color

cd $DEV_DIR
docker compose up --build --detach

rundoop() {
    # Run DOOP
    cd $DEV_DIR
    echo -e "${RED}[+]Generating DOOP datalog facts...${DG}"
    docker-compose exec -w /root/doop doop sh -c "./doop -a dependency-analysis -i /root/doop-data/input/ --cfg --Xfacts-subset APP --id facts --facts-only --stats none --open-programs jackee --also-resolve java.lang.Object --also-resolve java.lang.String --reflection-high-soundness-mode --reflection-invent-unknown-objects"

    # Run Souffle
    echo -e "${RED}[+]Processing facts to generate data dependency information...${DG}"
    docker-compose exec doop souffle --no-warn --fact-dir=/root/doop-data/facts/database --output-dir=/root/doop-data/output analysis-logic/dependency-analysis.dl -j$(($(nproc --all) + 1))
}

install_packages() {
    # Install the app
    cd $DEV_DIR
    echo -e "${RED}[+]Installing required python packages${DG}"
    docker compose exec -w /app app sudo pip install -r requirements.txt
    echo -e "${RED}[+]Installing tackle commands${DG}"
    docker compose exec -w /app app sudo pip install --editable .
}

run_ola() {
    # Build OLA DDG
    cd $DEV_DIR
    echo -e "${RED}[+]Building DDG${NC}"
    docker compose exec -w /app app c2g -v -c
}

run_diva() {
    # Add transaction data to DGI
    cd $DEV_DIR
    echo -e "${RED}[+] Adding transaction data to DDG${NC}"
    docker compose exec -w /app app tx2g --input=dgi/tx2graph/samples/transaction.json -c -v
}

run_schema() {
    # Add database schema data to DGI
    cd $DEV_DIR
    echo -e "${RED}[+] Adding database schema data to DDG${NC}"
    docker compose exec -w /app app s2g -i tests/fixtures/test-schema.ddl
}

dump_neo4j() {
    # Dump graph
    cd $DEV_DIR
    echo -e "${RED}[+]Dumping neo4 graph${NC}"
    docker compose stop neo4j
    docker compose run neo4j bin/neo4j-admin dump --to=/data/OLA.dump # Dump the DB
    docker compose restart neo4j
    docker compose cp neo4j:/data/OLA.dump $CUR_DIR/neodata/demo/data/OLA__$(date '+%d%m%y_%H%M').dump
    docker compose exec neo4j rm /data/OLA.dump
    echo -e "${NC}"
}

# Done...
cd $CUR_DIR
runall() {
    rundoop && install_packages && run_ola && run_diva && run_schema && dump_neo4j
}
"$@"
