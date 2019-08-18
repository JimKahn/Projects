#! /bin/bash
# Docker container build.

# Using recent Ubuntu LTS distribution.
docker build -t ubuntu_client:18.04 .

# Use bridge network to access external network.
docker run -it --net=bridge --name client ubuntu_client:18.04 /bin/bash
