#! /bin/bash
# Docker run maclookup container.

# Container run Name.
container_name="maclookup"

# Docker Hub image name.
image_name="jimkahm/maclookup:latest"


# Usage message
usage()
{
    echo "Run maclookup container"
    echo "Usage: run-container.sh [rm | attach]"
    echo
    echo "rm     - Remove previously run container"
    echo "attach - Restart and attach previously run container"
}

# Check if container can be restarted.
is_container_present()
{
    id=`docker ps -a | sed -e s/.*NAMES// | grep -c ${container_name}`
    if [ $id -eq 0 ]; then
	# Container is gone.
        echo "** Error: Container ${container_name} not found."
        exit 2
    fi
}

#
# Check for any optional arguments and handle them here.
#
if [ -n "$*" ]; then
    if [ "$*" == "rm" ]; then
        is_container_present
        docker rm ${container_name}
	echo "Container ${container_name} removed"
	exit 0
    fi
    if [ "$*" == "attach" ]; then
        is_container_present
        docker restart ${container_name}
        docker attach ${container_name}
	exit 0
    fi
    # Invalid arguements
    usage
    exit 22
fi

#
# If no optional arguments, build a new container.
#
docker pull ${image_name}

# Use bridge network to allow access to external network.
docker run -it --net=bridge --name=${container_name} ${image_name} /bin/bash
