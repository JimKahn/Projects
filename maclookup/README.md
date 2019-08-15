# maclookup
This is utility which takes a NIC's MAC address and
queries the macaddress.io server to collect it's
properties.

For example, the MAC's vendor is identified.
Whether the MAC is on a virtual machine is identified.

## Usage
### Normal use case:
    > ./maclookup.py <MAC> --key=<API_KEY>

The MAC is of the form "8c:85:90:48:90:0e".
The KEY is of  the form "qewrpoiupuasdfzcxvqewrpoiupuasd".

The mac information will be display in the console.
If the MAC is valid, the exit code will be 0.
If any error occurs, the exit code will reflect the
failure syndrome. 


### To check if the MAC is on a virtual machine:
    > ./maclookup.py <MAC> --key=<API_KEY> --isvm

The MAC is of the form "8c:85:90:48:90:0e".
The KEY is of  the form "qewrpoiupuasdfzcxvqewrpoiupuasd".

The MAC information will be displayed on the console.
If the MAC is on a virtual machine, the exit code will be 0.
Otherwise, the exit code will be non-zero.

## Installation
This utility requires Python 3.7.4. Earlier versions
of Python 3 may be problematic due to SSL service changes.

Python 2 is not supported.

This utilitiy has been tested on the latest MacOS and linux
Ubuntu 18 software distributions.

## Operation

This is a Python3 utility.  It uses the socket protocol
to perform an HTTPS GET REST request to obtain information
about the MAC.

For the HTTPS ciphers, the latest Python3 SSL services are
employed.  Usage of this utility on older Python3 distributions
will be problematic due to usage of the latest SSL services.

These Python3 services will use currently secure TLS protocols
(e.g. TLS 1.1 or later).

CA certificates are not configured for this utility.  This
is desirable for an extra layer of security.


