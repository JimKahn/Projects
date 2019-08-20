# Maclookup Utility
This is utility which takes a NIC's MAC address and
queries the macaddress.io server to collect it's
properties.  The utility will display the company that
created the NIC and whether it is in a virtual machine
or Docker container.

If you enter an invalid MAC, the utility will note
that it is invalid.


## Usage
### Normal use case:
    > ./maclookup.py <MAC> --key=<API_KEY>

The MAC is of the form "8c:85:90:48:90:0e".
The API_KEY is of  the form "qewrpoiupuasdfzcxvqewrpoiupuasd".
Both the MAC and the KEY must be provided for proper operation.

The MAC information will be display in the console terminal window.
If the MAC is valid, the exit code will be zero.
If any error occurs, the exit code will be a non-zero.

### To check if the MAC is on a virtual machine:
    > ./maclookup.py <MAC> --key=<API_KEY> --isvm

The "--isvm" flag requests validation that the MAC is on
a virtual platform.  If the MAC is not on a virtual platform,
the exit code will be non-zero.  If an error occurs, the
exit code will be non-zero.  The exit code denotes the failure
syndrome.

# System Requirements
This utility has been tested on MacOS version 10.15 and
Ubuntu versions 16.04 (or later).  This includes the
maclookup Docker container.

Windows operation has not been tested.

This utility requires Python 3.5 (or later). Earlier versions
of Python 3 may be problematic due to SSL API changes.  Python 2
is not supported.

## Installation
Manual installation consists of copying the following files to the server:
  * maclookup.py     - lookup MAC information
  * test.sh          - test cases for lookup utility
  * run-container.sh - Docker container deployment script

An easier method is to simply check out a copy of these files from the github repository:
  > git clone https://git@github.com/JimKahn/Projects .


### Docker Container Installation
A Docker container is provided  on docker hub.
The deploy the maclookup container:
  * docker login
  * ./run-container.sh

The docker login step requires a docker username and password.
Once the login is completed, just run the "run-container.sh" script
to pull over the docker image and activate the container.

You should see the container id and admin account CLI prompt on the terminal screen.
To run the valdiation test, type:
  > ./test.sh

Each test status and a test summary will be displayed on the console.
The file test.log contains more detailed test results.

You can also manually run the maclookup.py utility and provide the MAC address and
API_KEY.


# Design Overview

This macklookup.py is a Python3 script using the socket API
to open a session on port 443.  The socket is wrapped
in an SSL API which performs the negotiation and data transfer.
It also handles the certificate check.  (Prior to Python3.2,
the API did not handle certificate checking and it used
older deprecated SSL protocols.)

Duplicating the Python SSL API would take longer as you would
need to manage the SSL negotiation and certification validation.

The API key is visible in the command line.  This undesirable from a security
standpoint.  It should be treated as part of a SSH key pair and not visible on the
CLI.

The docker container uses the account "admin" rather than "root" for greater security.

Since the docker container is a client and not a server, it does not require
signed certificate for HTTPS operation.  If it were a server, then a signed
certificate would be required.  Self-signed certificates are not a good
work-around as many SSL libraries do not accept self-signed certificates
(e.g. Python).

Scripts are employed to create and activate the docker container.  Due to the
limited requirements of the docker container, bash scripting was employed.
Ansible scripting would be a better solution for more sophisticated requirements.





