# Prerequisites

**Tackle Data Gravity Insights** is written in Python requires at least Python 3.9 and pip installed. Also, in order to provide a repeatable working environment, GDI uses Docker or Podman to perform analysis using software pre-installed into docker images. This allows you to build and analyze Java applications without having to have Maven or Java installed on your computer.

## TL;DR for Mac

If you are using a Mac and have [Homebrew](https://brew.sh) installed you can install Python, Pip and Docker with the following commands:

```bash
brew install python@3.9
brew install --cask docker
```

If you are not on a Mac or want to perform a manual install please keep reading.

## Install Python 3.9 and pip3

You can see your Python version with the following command:

```bash
$ python3 --version
Python 3.9.7
```

It should return Python 3.9.x or greater. If it doesn't please install Python 3 or upgrade your Python 3 version.

- [Install Python 3.9](https://www.python.org/downloads/)

Once Python 3.9 is installed, you install Tackle DGI using the Python package manager `pip`. If you don't have `pip` follow the Instructions to install PIP before continuing.

- [Install PIP](https://pip.pypa.io/en/stable/installation/)

## Install Docker or Podman

You will need a container runtime. You can use Docker or Podman. If you don't have either of them you can install one or the other from the links below (you only need one):

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Podman](https://podman.io/getting-started/installation.html)

_(Optional)_ If you are using Podman and want to be able to cut and paste the Docker commands in the tutorial, just set an alias for `docker` and point it to `podman`.

```bash
alias docker=$(which podman)
```

All of the tutorial commands that use `docker` will now call `podman` instead.

## Prerequisites complete

That is all the prerequisite you need to get started. You can now return ot installing Tackle data Gravity Insights on your computer.
