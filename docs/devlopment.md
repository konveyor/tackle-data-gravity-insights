---
layout: default
title: Development
nav_order: 6
---
# Set up your Developer Environment

This project contains a `.devcontainer` folder that will set up a Docker environment in Visual Studio Code with the Remote Containers extension to provide a consistent repeatable disposable development environment for all of the developer.

You will need the following software installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com)
- [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension from the Visual Studio Marketplace

All of these can be installed manually by clicking on the links above or you can use a package manager like **Homebrew** on Mac of **Chocolatey** on Windows.

It is a good idea to add VSCode to your path so that you can invoke it from the command line. To do this, open VSCode and type `Shift+Command+P` on Mac or `Shift+Ctrl+P` on Windows to open the command palette and then search for "shell" and select the option **Shell Command: Install 'code' command in Path**. This will install VSCode in your path.

## Bring up the development environment

To bring up the development environment you should clone this repo, change into the repo directory, and start Visual Studio Code:

```bash
$ git clone git@github.com:konveyor/tackle-data-gravity-insights.git
$ cd tackle-data-gravity-insights
$ code .
```

Note that there is a period `.` after the `code` command. This tells Visual Studio Code to open the editor and load the current folder of files. Visual Studio Code will prompt you to **Reopen in a Container** and you should push this button. This will take a while the first time as it builds the Docker image and creates a container from it to develop in. After teh first time, this environment should come up almost instantaneously.

If it does not automatically prompt you to open the project in a container, you can select the green icon at the bottom left of your VSCode UI and select: **Remote Containers: Reopen in Container**.

Once the environment is loaded you should be placed at a `bash` prompt in the `/app` folder inside of the development container. This folder is mounted to the current working directory of your repository on your computer. This means that any file you edit while inside of the `/app` folder in the container is actually being edited on your computer. You can then commit your changes to `git` from either inside or outside of the container.

This project uses **Neo4j** which will also be added to your development environment running in a separate container and accessible at `neo4j:7474` from inside the development environment and outside from your web browser at: http://localhost:7474. The default development username is `neo4j` and the default password is `tackle`.
