---
layout: default
title: Demo
nav_order: 5
---
# Demo

For the demo, we'll use [daytrader7](https://github.com/WASdev/sample.daytrader7) as an example. Feel free to follow along with your own application and your personal directories. But, keep track of the _directories_ where the application _source code_ and the _built jar/war/ear_ reside and replace them appropriately below.

1. To get started, clone this repo and save the repository root as `$DGI_ROOT`:

    ```sh
    git clone https://github.com/konveyor/tackle-data-gravity-insights.git
    cd tackle-data-gravity-insights
    ```

    > This repository comes with a `demo` folder to work through an example app.
  
2. Let's download a copy of our sample application and build it.
  
    ```sh
    # Download and extract the demo application
    wget -c https://github.com/WASdev/sample.daytrader7/archive/refs/tags/v1.4.tar.gz -O - | tar -xvz -C demo/sample-application
    # Now build the application
    docker run --rm -v $(pwd)/demo/sample-application/sample.daytrader7-1.4:/build maven:3.8.4-openjdk-8-slim mvn --file=/build/pom.xml install
    ```

    This will create an EAR file called `daytrader-ee7-1.0-SNAPSHOT.ear` in `demo/sample-application/sample.daytrader7-1.4/daytrader-ee7/target` directory.

3. For convenience, let's put the generated `daytrader-ee7-1.0-SNAPSHOT.ear` in the `demo/code2graph-samples/doop-input` folder
  
    ```sh
    cp demo/sample-application/sample.daytrader7-1.4/daytrader-ee7/target/daytrader-ee7-1.0-SNAPSHOT.ear demo/code2graph-samples/doop-input