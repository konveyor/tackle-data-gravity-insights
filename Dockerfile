# Creates a runtime environemnt for DGI with some tools
FROM python:3.9-slim

# Add any tools that are needed beyond Python 3.9
RUN apt-get update && \
    apt-get install -y sudo zsh vim make git zip tree curl wget jq && \
    apt-get autoremove -y && \
    apt-get clean -y

# Create a user for development
ARG USERNAME=dgi
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user with passwordless sudo privileges
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /usr/bin/zsh \
    && usermod -aG sudo $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME 

# Set up the Python development environment
RUN python -m pip install --upgrade pip wheel && \
    pip install tackle-dgi

# Become a regular user for development
USER $USERNAME

# Enable color terminal for docker exec bash
ENV TERM=xterm-256color \
    NEO4J_BOLT_URL="neo4j://neo4j:konveyor@neo4j:7687"

# DGI is the entrypoint with default folder /data
WORKDIR /data
ENTRYPOINT ["dgi"]
CMD ["--help"]
