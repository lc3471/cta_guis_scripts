#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# Copyright (c) 2018, Stephen Goadhouse <sgoadhouse@virginia.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
 
#-------------------------------------------------------------------------------
#  Control a Aim TTi PL-P Series DC Power Supplies with PyVISA
#-------------------------------------------------------------------------------

# For future Python3 compatibility:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
    from . import SCPI
except ValueError:
    from SCPI import SCPI
    
from time import sleep
import pyvisa as visa
import re

class AimTTiCPX400DP(SCPI):
    """Basic class for controlling and accessing an Aim TTi PL-P Series
    Power Supply. This series of power supplies only minimally adheres
    to any LXI specifications and so it uses its own commands although
    it adheres to the basic syntax of SCPI. The underlying accessor
    functions of SCPI.py are used but the top level are all re-written
    below to handle the very different command syntax. This shows how
    one might add packages to support other such power supplies that
    only minimally adhere to the command standards.
    """

    def __init__(self, resource, wait=1.0):
        """Init the class with the instruments resource string

        resource - resource string or VISA descriptor, like TCPIP0::192.168.1.100::9221::SOCKET 
        wait     - float that gives the default number of seconds to wait after sending each command

        NOTE: According to the documentation for this power supply, the
        resource string when using the Ethernet access method must look
        like TCPIP0::192.168.1.100::9221::SOCKET where 192.168.1.100 is
        replaced with the specific IP address of the power supply. The
        inclusion of the 9221 port number and SOCKET keyword are
        apparently mandatory for these power supplies.
        """
        super(AimTTiCPX400DP, self).__init__(resource, max_chan=3, wait=wait,
                                        cmd_prefix='',
                                        read_termination='\n',
                                        write_termination='\r\n')

    def setLocal(self):
        """Set the power supply to LOCAL mode where front panel keys work again
        """
        self._instWrite('LOCAL')
    
    def setRemote(self):
        """Set the power supply to REMOTE mode where it is controlled via VISA
        """
        # Not supported explicitly by this power supply but the power
        # supply does switch to REMOTE automatically. So send any
        # command to do it.
        self._instWrite('*WAI')
    
    def setVTracking(self):
        """Set the power supply to Voltage Tracking Mode where
        Slave output tracks Master output"""
        self._instWrite('CONFIG 0')

    def setIndependent(self):
        """Set the power supply to Independent Mode where
        Slave and Master outputs operate independently"""
        self._instWrite('CONFIG 2')

    def isVTracking(self):
        """return True if Voltage Tracking is on, False if outputs operate
        independently"""
        ret = self._instQuery('CONFIG?')
        if (ret[0]=='0'):
            return True
        else:
            return False
        
    def isOutputOn(self, channel=None):
        """Return true if the output of channel is ON, else false
        
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
            
        _str = 'OP{}?'.format(self.channel)
        ret = self._instQuery(_str)

        # Only check first character so that there can be training whitespace that gets ignored
        if (ret[0] == '1'):
            return True
        else:
            return False
    
    def outputOn(self, channel=None, wait=None):
        
        if channel is not None:
            self.channel = channel
        if wait is None:
            wait = self._wait
            
        _str = 'OP{} 1'.format(self.channel)
        self._instWrite(_str)
        sleep(wait)             # give some time for PS to respond
    
    def outputOff(self, channel=None, wait=None):
        
        if channel is not None:
            self.channel = channel
        if wait is None:
            wait = self._wait
            
        _str = 'OP{} 0'.format(self.channel)
        self._instWrite(_str)
        sleep(wait)             # give some time for PS to respond
    
    def outputOnAll(self, wait=None):
        
        if wait is None:
            wait = self._wait

        _str = 'OPALL 1'.format(self.channel)
        self._instWrite(_str)
        sleep(wait)             # give some time for PS to respond
    
    def outputOffAll(self, wait=None):
        
        if wait is None:
            wait = self._wait

        _str = 'OPALL 0'.format(self.channel)
        self._instWrite(_str)
        sleep(wait)             # give some time for PS to respond
    
    def setVoltage(self, voltage, channel=None, wait=None):
        
        if channel is not None:
            self.channel = channel
        if wait is None:
            wait = self._wait
            
        _str = 'V{} {}'.format(self.channel, voltage)
        self._instWrite(_str)
        sleep(wait)             # give some time for PS to respond
        
    def setCurrent(self, current, channel=None, wait=None):
        
        if channel is not None:
            self.channel = channel
        if wait is None:
            wait = self._wait
            
        _str = 'I{} {}'.format(self.channel, current)
        self._instWrite(_str)
        sleep(wait)             # give some time for PS to respond

        
    def queryVoltage(self, channel=None):

        if channel is not None:
            self.channel = channel
            
        _str = 'V{}?'.format(self.channel)
        ret = self._instQuery(_str)

        # Pull out words from response
        match = re.match('^([^\s0-9]+)([0-9]+)\s+([0-9.+-]+)',ret)
        if (match == None):
            raise RuntimeError('Unexpected response: "{}"'.format(ret))
        else:
            # break out the words from the response
            words = match.groups()
            if (len(words) != 3):
                raise RuntimeError('Unexpected number of words in response: "{}"'.format(ret))
            elif(words[0] != 'V' or int(words[1]) != self.channel):
                raise ValueError('Unexpected response format: "{}"'.format(ret))
            else:
                # response checks out so return the fixed point response as a float()
                return float(words[2])
    
    def queryCurrent(self, channel=None):
        
        if channel is not None:
            self.channel = channel
                    
        _str = 'I{}?'.format(self.channel)
        ret = self._instQuery(_str)

        # Pull out words from response
        match = re.match('^([^\s0-9]+)([0-9]+)\s+([0-9.+-]+)',ret)
        if (match == None):
            raise RuntimeError('Unexpected response: "{}"'.format(ret))
        else:
            # break out the words from the response
            words = match.groups()
            if (len(words) != 3):
                raise RuntimeError('Unexpected number of words in response: "{}"'.format(ret))
            elif(words[0] != 'I' or int(words[1]) != self.channel):
                raise ValueError('Unexpected response format: "{}"'.format(ret))
            else:
                # response checks out so return the fixed point response as a float()
                return float(words[2])
    
    def measureVoltage(self, channel=None):
        
        if channel is not None:
            self.channel = channel
                    
        _str = 'V{}O?'.format(self.channel)
        ret = self._instQuery(_str)
        # Pull out words from response
        match = re.match('^([0-9.+-]+)([^\s]+)',ret)
        if (match == None):
            raise RuntimeError('Unexpected response: "{}"'.format(ret))
        else:
            # break out the words from the response
            words = match.groups()
            if (len(words) != 2):
                raise RuntimeError('Unexpected number of words in response: "{}"'.format(ret))
            elif(words[1] != 'V'):
                raise ValueError('Unexpected response format: "{}"'.format(ret))
            else:
                # response checks out so return the fixed point response as a float()
                return float(words[0])
    
    def measureCurrent(self, channel=None):
        
        if channel is not None:
            self.channel = channel
            
        _str = 'I{}O?'.format(self.channel)
        ret = self._instQuery(_str)

        # Pull out words from response
        match = re.match('^([0-9.+-]+)([^\s]+)',ret)
        if (match == None):
            raise RuntimeError('Unexpected response: "{}"'.format(ret))
        else:
            # break out the words from the response
            words = match.groups()
            if (len(words) != 2):
                raise RuntimeError('Unexpected number of words in response: "{}"'.format(ret))
            elif(words[1] != 'A'):
                raise ValueError('Unexpected response format: "{}"'.format(ret))
            else:
                # response checks out so return the fixed point response as a float()
                return float(words[0])

