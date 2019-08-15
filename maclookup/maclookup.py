#! /usr/bin/env python3

'''
MAC lookup utility using macaddress.io web site.
REST API request requires a user API key.

Usage:
    Standard usage.  Lookup up MAC and display summary.
    > maclookup <MAC> --key=<API_KEY>

    Virtual Machine usage.  Check if MAC is on a VM.
    > maclookup <MAC> --key=<API_KEY> --isvm

 Return Codes:
   0: MAC is valid.  If "--isvm" flag used, this MAC is on a virtual machine.
   EEXIST: MAC is valid and on a physical machine.
   ENODEV: MAC is invalid.
   EIO: Unspecified HTTP error ocurred during lookup process.

Version 0.1 8/14/2019 by J. Kahn
  Basic framework.

'''

import argparse
import http.client
import socket
import ssl
import json
import sys
import errno

utilName = 'maclookup'

HTTP_BAD_REQUEST = 400       # >400 is a failure.
HTTP_OK_REQUEST  = 300       # <300 is OK; >= 300 is bad news.
API_KEY_MIN      = 8         # If api key is <8 characters, it's probably bad.
HTTPS_PORT       = 443       # Use SSL encryption on this port


class socket_connection():
    """
    Perform a MAC address lookup using sockets API.
    Provides methods for open, close, and lookup.
    Plus extra methods for evaluating the lookup results.

    """
    connection = None
    api_key = None

    def open(self, serverURL=None, serverAPI=None, port=80, api_key=None):
        """
        Open a socket connection.

        Parameters:
        serverURL (str): MAC lookup server URL.
        serverAPI (str): server REST API URL
        port (int): Port to use for connection.
        api_key (str): User API key string

        Returns: None
        """
        if not serverURL:
            raise ValueError('Missing server URL')
        if not serverAPI:
            raise ValueError('Missing server API URL')
        if not api_key or len(api_key) < API_KEY_MIN:
            raise ValueError('Invalid api_key')
        self.serverURL = serverURL
        self.serverAPI = serverAPI
        self.port = port
        self.api_key = api_key

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port == HTTPS_PORT:
            # If using HTTPS, need to configure ssl.
            # XX: Should provide client CA cert too.
            ctx = ssl.create_default_context()
            self.connection = ctx.wrap_socket(self.socket, server_hostname=serverURL)
            #print(self.connection.version)
            self.connection.connect((serverURL, port))
        else:
            # If using HTTP, just open the connection.
            self.connection = self.socket
            self.connection.connect((serverURL, port))

    def close(self):
        """
        Close the socket connection.

        Parameters: None

        Returns: None
        """
        if self.connection:
           self.connection.close()

    def lookup_mac(self, mac=None):
        """
        Lookup the MAC address.
        
        Parameters:
        mac (str): MAC address

        Returns:
        rsp (dict):  Get response from MAC lookup server.
        """
        if not mac:
            raise ValueError('Missing MAC address')

        payload = '/v1?apiKey=' + self.api_key + '&output=json&search=' + mac
        request = 'GET ' + payload +  ' HTTP/1.1\r\nHOST:' + self.serverAPI + '\r\n\r\n'
        self.connection.send(request.encode('utf-8'))
        response = self.connection.recv(8192)
        raw = repr(response.decode('utf-8'))
        raw = raw[1:-1]        # Strip off tick marks around string
        data = raw.split('\\r\\n')
        rsp = {}
        #
        # Process response, capturing the http status and json lookup data.
        #
        for line in data:
            #print(line)
            if line.startswith('HTTP'):
                fields = line.split()
                rsp['status'] = int(fields[1])
                rsp['reason'] = fields[2]
                if int(fields[1]) >= HTTP_BAD_REQUEST:
                    break
            if line.startswith('{'):
                data = json.loads(line)
                rsp.update(data)
        return rsp

    def is_mac_valid(self, response):
        """
        Check if MAC is valid.

        Parameters:
        response (dict): Get response from lookup.

        Returns:
        True: MAC is valid
        False: MAC is invalid
        """
        if response['status'] < HTTP_OK_REQUEST:
            macInfo = response['macAddressDetails']
            return macInfo['isValid']
        return False

    def is_vm(self, response):
        """
        Check if MAC is on a virtual machine.

        Parameters:
        response (dict): Get response from lookup.

        Returns:
        True: MAC is on a virtual machine
        False: MAC is not on a virtual machine
        """
        if response['status'] < HTTP_OK_REQUEST:
            macinfo = response['macAddressDetails']
            if macinfo['isValid'] == True:
                # XX: Check status
                 if macinfo['virtualMachine'] != 'Not detected':
                    return True
        return False

    def print(self, response):
        """ 
        Print the MAC lookup summary.

        Parameters:
        response (dict): Get response from lookup.

        Returns: None
        """
        #print(response)
        if response['status'] < HTTP_BAD_REQUEST:
            vendor = response['vendorDetails']
            macinfo = response['macAddressDetails']
            if macinfo['isValid']:
                info = 'MAC ' + macinfo['searchTerm'] + ' (' + vendor['companyName'] + ') '
                if macinfo['virtualMachine'] != 'Not detected':
                    info = info +  'on Virtual Machine'
            else:
                info = 'MAC  ' + macinfo['searchTerm'] + ' is Invalid'
            print(info)
        else:
            print('ERROR:', response['status'], response['reason'])


class http_connection():
    """
    Perform a MAC address lookup using the http module.
    Provides methods for open, close, and lookup.
    Plus extra methods for evaluating the lookup results.
    """
    connection = None
    api_key = None

    def open(self, serverURL=None, serverAPI=None, port=80, api_key=None):
        """
        Open a http connection.

        Parameters:
        serverURL (str): MAC lookup server URL.
        port (int): Port to use for connection.
        api_key (str): User API key string

        Returns:
        None
        """
        if not serverURL:
            raise ValueError('Missing server URL')
        if not serverAPI:
            raise ValueError('Missing server API URL')
        if not api_key or len(api_key) < API_KEY_MIN:
            raise ValueError('Invalid api_key')
        self.serverURL = serverURL
        self.serverAPI = serverAPI
        self.port = port
        self.api_key = api_key
        self.connection = http.client.HTTPSConnection(serverAPI, timeout=5)

    def close(self):
        """
        Close the http connection.

        Parameters: None

        Returns: None
        """
        if self.connection:
            self.connection.close()

    def lookup_mac(self, mac=None):
        """
        Lookup the MAC address.
        
        Parameters:
        mac (str): MAC address

        Returns:
        rsp (dict):  Get response from MAC lookup server.
        """
        if not mac:
            raise ValueError('Missing MAC address')

        payload = '/v1?apiKey=' + self.api_key + '&output=json&search=' + mac
        self.connection.request('GET', payload)
        response =self.connection.getresponse()
        # Collect response status
        rsp = {}
        rsp['status'] = response.status
        rsp['reason'] = response.reason

        # Collect the MAC response or the error info.
        raw = response.read()
        raw = raw.decode('utf-8')
        data = json.loads(raw)
        rsp.update(data)
        return rsp
 
    def is_mac_valid(self, response):
        """
        Check if MAC is valid.

        Parameters:
        response (dict): Get response from lookup.

        Returns:
        True: MAC is valid
        False: MAC is invalid
        """
        if response['status'] < HTTP_OK_REQUEST:
            macInfo = response['macAddressDetails']
            return macInfo['isValid']
        return False

    def is_vm(self, response):
        """
        Check if MAC is on a virtual machine.

        Parameters:
        response (dict): Get response from lookup.

        Returns:
        True: MAC is on a virtual machine
        False: MAC is not on a virtual machine
        """
        if response['status'] < HTTP_OK_REQUEST:
            macInfo = response['macAddressDetails']
            if macInfo['isValid'] == True:
                # XX: Check status
                if macinfo['virtualMachine'] != 'Not detected':
                    return True
        return False

    def print(self, response):
        """ 
        Print the MAC lookup summary.

        Parameters:
        response (dict): Get response from lookup.

        Returns: None
        """
        #print(response)
        if response['status'] < HTTP_BAD_REQUEST:
            vendor = response['vendorDetails']
            macinfo = response['macAddressDetails']
            if macinfo['isValid']:
                info = 'MAC ' + macinfo['searchTerm'] + ' (' + vendor['companyName'] + ') '
                if macinfo['virtualMachine'] != 'Not detected':
                    info = info +  'on Virtual Machine'
            else:
                info = 'MAC  ' + macinfo['searchTerm'] + ' is Invalid'
            print(info)
        else:
            print('ERROR:', response['status'], response['reason'])


def main():
    """
    CLI interface -- Parse CLI parameters and call connection object to perform MAC lookup.

    Parameters: None

    Returns:
    EOK (int): MAC is valid
    EEXIST (int):  MAC is valid and on a physical machine.
    ENODEV (int):  MAC is invalid.
    EIO (int):  Unspecified HTTP error ocurred during lookup process.
    """
    parser = argparse.ArgumentParser(prog=utilName)
    parser.add_argument('mac', type=str, 
                        help='NIC MAC address')
    parser.add_argument('--key', dest='api_key', required=True, type=str,
                        help='User API key credential') 
    parser.add_argument('--isvm', dest='isvm',  action='store_true',
                        help='Check if MAC is on a virtual machine') 
    args = parser.parse_args()

    # macaddress web site definitions.
    serverURL = 'macaddress.io'
    serverAPI =  'api.' + serverURL   # REST URL
    portURL = 443

    # Example using HTTP module.
    #request = http_connection()
    #request.open(serverURL, serverAPI,  portURL, args.api_key)
    #result = request.lookup_mac(args.mac)
    #request.close()
 
    # HTTP using socket API.
    request = socket_connection()
    request.open(serverURL, serverAPI, portURL, args.api_key)
    result = request.lookup_mac(args.mac)
    request.close()

    # Print the MAC summary.
    request.print(result)

    # If http GET failed, return IO error.
    if result['status'] >= HTTP_OK_REQUEST:
        sys.exit(errno.EIO)

    # If MAC is invalid, return non-existant device error.
    if request.is_mac_valid(result) == False:
        sys.exit(errno.ENODEV)

    # if checking is a VM MAC, return device exists if MAC is a physical device.
    if args.isvm and request.is_vm(result) == False:
        sys.exit(errno.EEXIST)

    # Return OK status
    sys.exit(0)

if __name__ == '__main__':
    main()
