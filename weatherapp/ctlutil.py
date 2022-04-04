"""
This module contains the CtlUtil class. CtlUtil objects set up a connection to
Stem and handle communication concerning consensus documents and descriptor
files.

@var unparsable_email_file: A log file for contacts with unparsable emails.
"""

'''
.............................
..........STEM DOCS..........
.............................
Stem is a Python controller library for Tor.
With it you can use Tor's control protocol to script against the Tor process, or build things such as Nyx.
Stem's latest version is 1.8 (released December 29th, 2019).

https://stem.torproject.org/#:~:text=Stem%20is%20a%20Python%20controller,released%20December%2029th%2C%202019).

'''
import logging
import re
import string
import getpass
import sys
import socket

import stem
import stem.connection
import stem.version

from stem import Flag
from stem.control import Controller
from config import config 


unparsable_email_file = 'log/unparsable_emails.txt'


class CtlUil:
    '''
    A class that handles communication with the local Tor process via Stem.

    @type _CONTROL_HOST: str
    @cvar _CONTROL_HOST: Constant for the control host of the Stem connection.

    @type _CONTROL_PORT: int
    @cvar _CONTROL_PORT: Constant for the control port of the Stem connection.

    @type _AUTHENTICATOR: str
    @cvar _AUTHENTICATOR: Constant for the authenticator string of the Stem
                          connection.


    @type control_host: str
    @ivar control_host: Control host of the Stem connection.

    @type control_port: int
    @ivar control_port: Control port of the Stem connection.

    @type control: stem.control.Controller
    @ivar control: Stem controller connection.

    @type authenticator: str
    @ivar authenticator: Authenticator string of the Stem connection.

    @type control: Stem Connection
    @ivar control: Connection to Stem.

    '''


    _CONTROL_HOST = '127.0.0.1'
    _CONTROL_PORT = config.control_port
    _AUTHENTICATOR = config.authenticator



    def __init__(self, control_host = _CONTROL_HOST,
                control_port = _CONTROL_PORT, sock = None,
                authenticator = _AUTHENTICATOR):

        '''
        Initialize the CtlUtil object, connect to Stem.
        '''
        self.control_host = control_host
        self.control_port = control_port
        self.authenticator = authenticator    
        try:
            self.control = Controller.from_port(port = self.control_port)
        except stem.SocketError:
            errormsg = "Could not connect to Tor control port.\n" + \
            "Is Tor running on %s with its control port opened on %s?" %\
            (control_host, control_port)
            logging.error(errormsg )
            raise 




        # Authenticate connection
        self.control.authenticate(config.authenticator)

    def __del__(self) :
        '''
        Closes the connection when the CtlUtil object is garbage collected.
        (From original Tor Weather)
        '''

        self.control.close()

    def is_up(self, fingerprint):
        '''
        Check if this node is up (actively running) 
        by requesting a consensus document for node C{fingerprint}. 
     
        If a document is received successfully, then the node is up; 
        if a document is not received, then the router is down.
        If a node is hiberanating, it will return C{False}.


        @type fingerprint: str
        @param fingerprint: Fingerprint of the node in question.

        @rtype: bool
        @return: C{True} if the node is up, C{False} if it's down.
        
        '''

        # try:
        #     self.control.get_network_status(fingerprint)
        #     return True
        # except:
        #     return False

        cons = self.get_single_consensus(fingerprint)
        if cons == '':
            return False
        else:
            return True



    def is_exit(self, fingerprint):
        try:
            desc = self.control.get_server_descriptor(fingerprint)
            return desc.exit_policy.can_exit_to(port = 80)
        except stem.ControllerError:
            errormsg = "Unable to get server descriptor for '%s'" % (fingerprint)
            logging.error(errormsg )
            return False
        

    def is_stable(self, fingerprint):
        '''
        Check if a Tor node has the stable flag.

        @type fingerprint: str
        @param fingerprint: The fingerprint of the router to check

        @rtype: bool
        @return: True if this router has a valid consensus with the stable
        flag, false otherwise.
        '''

        try:
            desc = self.control.get_network_status(fingerprint)
            return Flag.Stable in desc.flags
        except stem.ControllerError:
            errormsg = "Unable to get router status entry for '%s'" % (fingerprint)
            logging.error(errormsg)
            return False


    def is_hibernating(self, fingerprint):
        """
        Check if the Tor relay with fingerprint C{fingerprint} is hibernating.

        @type fingerprint: str
        @param fingerprint: The fingerprint of the Tor relay to check.

        @rtype: bool
        @return: True if the Tor relay has a current descriptor file with
        the hibernating flag, False otherwise."""

        try:
            desc = self.control.get_server_descriptor(fingerprint)
            return desc.hibernating
        except stem.ControllerError:
            return False
    
    pass