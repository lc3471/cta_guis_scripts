#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Laurel Carpenter

try:
    from . import SCPI
except ValueError:
    from SCPI import SCPI
    
from time import sleep
import pyvisa as visa
import re
from math import inf

class RigolDG5000(SCPI):
    def __init__(self, resource, wait=1.0):
        super(RigolDG5000, self).__init__(resource, max_chan=2, wait=wait,
                cmd_prefix='',
                read_termination='',
                write_termination='\r\n')
        self.open()

    def isOutputOn(self, channel=None):
        _str = (':OUTP{}?').format(channel)
        ret = self._instQuery(_str)
        
        if (ret=="ON\n\n"):
            return True
        else:
            return False
    
    def outputOn(self, channel=None, wait=None):
        if wait is None:
            wait = self._wait
        str_ = (':OUTP{} ON').format(channel)
        self._instWrite(str_)
        sleep(wait)             # give some time for PS to respond
    
    def outputOff(self, channel=None, wait=None):
        if wait is None:
            wait = self._wait
        str_ = (':OUTP{} OFF').format(channel)
        self._instWrite(str_)
        sleep(wait)             # give some time for PS to respond


    # pulse
    def applyPulse(self, freq=1000, amp=5, offset=None, delay=None, channel=None, wait=None):
        # freq: unit=Hz, 1 micro-Hz to 50 MHz
        # amp: unit=Vpp
        # offset: unit=Vdc
        # delay: unit=s
        if wait is None:
            wait=self._wait

        str_=(":SOUR{}:APPL:PULS {},{},{},{}").format(channel,freq,amp,offset,delay)
        self._instWrite(str_)
        sleep(wait)
    
    def queryApply(self, channel=None):
        str_=(":SOUR{}:APPL?").format(channel)
        ret=self._instQuery(str_)
        ret=ret[:(len(ret)-2)] # remove '\n' from end of string
        ret=ret.strip('"') # remove quotes from beginning and end of string
        lst=ret.split(",") # split string into variables
        
        for i in range(1,len(lst)): # range(1,len(lst)) s.t. not converting waveform name to float
            if lst[i]=="DEF":
                lst[i]=0
            else:
                lst[i]=float(lst[i])
        # lst='waveform name', 'freq', 'amp', 'offset', 'phase/delay'
        return lst

    def dutyCycle(self, pct=None, channel=None, wait=None, Min=False, Max=False):
        if wait is None: 
            wait=self._wait

        if Min: # set to minimum duty cycle
            str_=(":SOUR{}:PULS:DCYC MIN").format(channel) 
        elif Max: # set to maximum duty cycle
            str_=(":SOUR{}:PULS:DCYC MAX").format(channel)
        else: # set duty cycle as percentage
            str_=(":SOUR{}:PULS:DCYC {}").format(channel, pct)
        
        self._instWrite(str_)
        sleep(wait)

    def queryDutyCycle(self, channel=None):
        # ask for duty cycle as percentage
        str_=(":SOUR{}:PULS:DCYC?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)
        return ret

    def pulseDelay(self, delay=None, channel=None, wait=None, Min=False, Max=False):
        if wait is None:
            wait=self._wait

        if Min: # set minimum pulse delay
            str_=(":SOUR{}:PULS:DEL MIN").format(channel)
        elif Max: # set maximum pulse delay
            str_=(":SOUR{}:PULS:DEL MAX").format(channel)
        else: # set pulse delay in seconds
            str_=(":SOUR{}:PULS:DEL {}").format(channel, delay)

        self._instWrite(str_)
        sleep(wait)

    def queryDelay(self, channel=None):
        # ask for pulse delay in seconds
        str_=(":SOUR{}:PULS:DEL?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)
        return ret

    def holdWidth(self, channel=None, wait=None):
        # hold pulse width (instead of duty cycle)
        if wait is None:
            wait=self._wait
        str_=(":SOUR{}:PULS:HOLD WIDT").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def holdDuty(self, channel=None, wait=None):
        # hold duty cycle (instead of pulse width)
        if wait is None:
            wait=self._wait
        str_=(":SOUR{}:PULS:HOLD DUTY").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def isWidth(self, channel=None):
        #if not WIDT, DUTY
        # ask if holding pulse width or duty cycle
        str_=(":SOUR{}:PULS:HOLD?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')

        if ret=="WIDT\n":
            return True
        else:
            return False

    def transitionLeading(self, seconds=None, channel=None, wait=None, Min=False, Max=False):
        if wait is None:
            wait=self._wait

        if Min: # set transition leading to minimum
            str_=(":SOUR{}:PULS:TRAN MIN").format(channel)
        elif Max: # set transition leading to maximum
            str_=(":SOUR{}:PULS:TRAN MAX").format(channel)
        else: # set transition leading in seconds
            str_=(":SOUR{}:PULS:TRAN {}").format(channel, seconds)

        self._instWrite(str_)
        sleep(wait)

    def queryTransLead(self, channel=None):
        # ask for transition leading in seconds
        str_=(":SOUR{}:PULS:TRAN?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)
        return ret

    def transitionTrailing(self, seconds=None, channel=None, wait=None, Min=False, Max=False):
        if wait is None:
            wait=self._wait

        if Min: # set transition trailing to minimum
            str_=(":SOUR{}:PULS:TRAN:TRA MIN").format(channel)
        elif Max: # set transition trailing to maximum
            str_=(":SOUR{}:PULS:TRAN:TRA MAX").format(channel)
        else: # set transition trailing in seconds
            str_=(":SOUR{}:PULS:TRAN:TRA {}").format(channel, seconds)

        self._instWrite(str_)
        sleep(wait)

    def queryTransTrail(self, channel=None):
        # ask for transition trailing in seconds
        str_=(":SOUR{}:PULS:TRAN:TRA?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)
        return ret

    def pulseWidth(self, seconds=None, channel=None, wait=None, Min=False, Max=False):
        if wait is None:
            wait=self._wait

        if Min: # set pulse width to minimum
            str_=(":SOUR{}:PULS:WIDT MIN").format(channel)
        elif Max: # set pulse width to maximum
            str_=(":SOUR{}:PULS:WIDT MAX").format(channel)
        else: # set pulse width in seconds
            str_=(":SOUR{}:PULS:WIDT {}").format(channel, seconds)

        self._instWrite(str_)
        sleep(wait)

    def queryWidth(self, channel=None):
        # ask for pulse width in seconds
        str_=(":SOUR{}:PULS:WIDT?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)
        return ret

    def setImpedance(self, ohms=None, channel=None, wait=None, inf=False, Min=False, Max=False):
        if wait is None:
            wait=self._wait

        if inf: # set high Z (infinite impedance)
            str_=(":OUTP{}:IMP INF").format(channel)
        elif Min: # set minimum impedance
            str_=(":OUTP{}:IMP MIN").format(channel)
        elif Max: # set maximum impedance
            str_=(":OUTP{}:IMP MAX").format(channel)
        else: # set impedance in ohms
            str_=(":OUTP{}:IMP {}").format(channel, ohms)

        self._instWrite(str_)
        sleep(wait)
        
    def queryImpedance(self, channel=None):
        # ask for impedance in ohms
        str_=(":OUTP{}:IMP?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)
        return ret

    def isImpInf(self, channel=None):
        # ask if impedance is infinite
        str_=(":OUTP{}:IMP?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)
        
        if ret==inf:
            return True
        else:
            return False

    def polarityNorm(self, channel=None, wait=None):
        # set polarity to normal
        if wait is None:
            wait=self._wait
        str_=(":OUTP{}:POL NORM").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def polarityInv(self, channel=None, wait=None):
        # set polarity to inverted
        if wait is None:
            wait=self._wait
        str_=(":OUTP{}:POL INV").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def isNorm(self, channel=None):
        # if not NORM, INV
        # ask if polarity is normal or inverted
        str_=(":OUTP{}:POL?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')

        if ret == "NORMAL\n\n":
            return True
        else:
            return False

    def syncOn(self, channel=None, wait=None):
        # turn sync on
        if wait is None:
            wait=self._wait
        str_=(":OUTP{}:SYNC ON").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def syncOff(self, channel=None, wait=None):
        # turn sync off
        if wait is None:
            wait=self._wait
        str_=(":OUTP{}:SYNC OFF").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def isSyncOn(self, channel=None):
        # ask if sync is on or off
        str_=(":OUTP{}:SYNC?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')

        if ret=="ON\n":
            return True
        else:
            return False

    def syncPolPos(self, channel=None, wait=None):
        # set sync polarity to positive
        if wait is None:
            wait=self._wait
        str_=(":OUTP{}:SYNC:POL POS").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def syncPolNeg(self, channel=None, wait=None):
        # set sync polarity to negative
        if wait is None:
            wait=self._wait
        str_=(":OUTP{}:SYNC:POL NEG").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def isSyncPolPos(self, channel=None):
        # if not POS, NEG
        # ask if sync polarity is positive or negative
        str_=(":OUTP{}:SYNC:POL?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        
        if ret=="POS\n":
            return True
        else: 
            return False

    def saverOn(self, wait=None):
        # screensaver
        if wait is None:
            wait=self._wait
        str_=":DISP:SAV ON"
        self._instWrite(str_)
        sleep(wait)

    def saverOff(self, wait=None):
        # screensaver
        if wait is None:
            wait=self._wait
        str_=":DISP:SAV OFF"
        self._instWrite(str_)
        sleep(wait)

    def isSaverOn(self):
        # screensaver
        str_=":DISP:SAV?"
        ret=self._instQuery(str_)
        ret=ret.strip('"')

        if ret=="ON\n":
            return True
        else:
            return False

    def saverImm(self, wait=None):
        # screensaver
        if wait is None:
            wait=self._wait
        str_=":DISP:SAV:IMM"
        self._instWrite(str_)
        sleep(wait)
