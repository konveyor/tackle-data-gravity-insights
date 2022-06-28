---
layout: default
title: Prerequisites
nav_order: 3
---

# Prerequisites

**Tackle Data Gravity Insights** is written in Python requires at least Python 3.9 and pip installed. Also, in order to provide a repeatable working environment, DGI uses Docker or Podman to perform analysis using software pre-installed into docker images. This allows you to build and analyze Java applications without having to have Maven or Java installed on your computer.

## TL;DR for Mac

If you are using a Mac and have [Homebrew](https://brew.sh) installed you can install Python, Pip and Docker with the following commands:

```bash
brew install python@3.9
brew install --cask docker
```

Note: Any version of Python after 3.9 is also acceptable.

If you are not on a Mac or want to perform a manual install please keep reading.

## Using a Multipass VM

The next easiest way to get started is by using a virtual machine. This will eliminate the need to install Python or Docker/Podman on your workstation.

Multipass is a tool by Canonical that allows you to get an instant Ubuntu VM with a single command. It uses the native hypervisor of your OS and runs on Linux, Mac, and Windows. You can download multipass from [multipass.run](https://multipass.run)

Multipass uses industry standard cloud-init files. We have included a cloud-init file called `cloud-config.yaml` in the root of this repo that will establish all of the software required to run DGI in an isolated VM with Podman. You can start a multipass VM and share your current folder with the following command from the root of this repo:

```bash
$ multipass launch jammy -v \
    --name dgi \
    --cpus 4 \
    --mem 8G \
    --disk 20G \
    --cloud-init cloud-config.yaml 
$ multipass mount . dgi:/dgi
$ multipass shell dgi
$ cd /dgi
```

This will launch an Ubuntu 22.04 LTS (Jammy) VM with 4 cpus, 8GB memory, and a 20GB disk, installing Python and Podman for you. It will then mount your current directory into the VM at the /dgi mount point. Finally it will place you inside a shell in the VM. Everything you do inside the VM in the `/dgi` folder will be saved to your current folder on yur computer for future use.

You can stop the VM with:

```bash
$ multipass stop dgi
```

## Manual Install Python 3.9 and pip3

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
