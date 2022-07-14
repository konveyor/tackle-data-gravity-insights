# Image for a Python 3 development environment
FROM python:3.9-slim

# Add any tools that are needed beyond Python 3.9
RUN apt-get update && \
    apt-get install -y sudo zsh vim make git zip tree curl wget jq && \
    apt-get autoremove -y && \
    apt-get clean -y

# Create a user for development
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user with passwordless sudo privileges
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /usr/bin/zsh \
    && usermod -aG sudo $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME 

# Set up the Python development environment
WORKDIR /app
RUN python -m pip install --upgrade pip && \
    pip install --upgrade wheel

# Become a regular user for development
USER $USERNAME

# Enable color terminal for docker exec bash
ENV TERM=xterm-256color

ENV SHELL /bin/zsh

# Install oh-my-zsh for zsh on wheels 
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true
