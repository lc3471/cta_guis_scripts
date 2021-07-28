# Laurel Carpenter
# 07/28/2021

import visa
from time import sleep


class SiglentSDS1202XE(object):
    def __init__(self,resource,wait=0.5,max_channels=2,
            read_termination='',write_termination='/r/n',
            chunk_size=20*1024**2,timeout=30000):


        self.resource=resource
        self.wait=wait
        self.max_channels=max_channels
        self.read_termination=read_termination
        self.write_termination=write_termination
        self.chunk_size=chunk_size
        self.timeout=timeout

    def open_inst(self):
        rm=visa.ResourceManager()
        self.inst=rm.open_resource(self.resource,chunk_size=self.chunk_size,timeout=self.timeout)

    def close_inst(self):
        self.inst.close()

    def chdr_off(self):
        self.inst.write("CHDR OFF")


    def msiz_14m(self):
        if self.inst.query("MSIZ?") != "14M\n":
            self.inst.write("MSIZ 14M")

    def query_ofst(self,channel):
        ret=self.inst.query(("C{}:OFST?").format(channel))
        return float(ret)

    def query_vdiv(self,channel):
        ret=self.inst.query(("C{}:VDIV?").format(channel))
        return float(ret)

    def query_tdiv(self):
        ret=self.inst.query("TDIV?")
        return float(ret)

    def query_sara(self):
        ret=self.inst.query("SARA?")
        return float(ret)

    def query_trdl(self):
        ret=self.inst.query("TRDL?")
        return float(ret)

    def set_vdiv(self,channel,vdiv,wait=None):
        # possible VDIV:
        # 500 UV (micro)
        # 1,2,5,10,20,50,100,200,500 MV
        # 1,2,5,10 V
        if vdiv=="500 \u03BCV":
            vdiv="500UV" # change unicode mu to letter u
        vdiv.replace(' ','') # get rid of space in '10 mV'
        vdiv=vdiv.upper() # set unit uppercase
        self.inst.write(("C{}:VDIV {}").format(channel,vdiv))
        if wait is None:
            wait=self.wait
        sleep(wait)

    def set_ofst(self,channel,ofst,unit,wait=None):
        # can be anything in UV/MV/V ?
        if unit=="\u03BCV":
            unit="UV" # change unicode mu to letter u
        unit=unit.upper() # set unit uppercase
        self.inst.write(("C{}:OFST {}{}").format(channel,ofst,unit))
        if wait is None:
            wait=self.wait
        sleep(wait)

    def set_tdiv(self,tdiv,unit,wait=None):
        # possible TDIV:
        # 1,2,5,10,20,50,100,200,500 NS
        # 1,2,5,10,20,50,100,200,500 US (micro)
        # 1,2,5,10,20,50,100,200,500 MS
        # 1,2,5,10,20,50,100 S
        if unit=="\u03BCs":
            unit="US" # change unicode mu to letter u
        elif (unit=='s') and ((tdiv=='200') or (tdiv=='500')):
            tdiv='100' # can't set tdiv to 200 or 500 S, so set to max (100 S)
        unit=unit.upper() # set unit uppercase
        self.inst.write(("TDIV {}{}").format(tdiv,unit))
        if wait is None:
            wait=self.wait
        sleep(wait)

    def set_trdl(self,trdl,unit,wait=None):
        if unit=='ns':
            mult=10**-9
        elif unit=='\u03BCs':
            mult=10**-6
            unit="US"
        elif unit=='ms':
            mult=10**-3
        else:
            mult=1

        if (trdl*mult)<=(self.tdiv*10):
            unit=unit.upper()
            self.inst.write(("TRDL {}{}").format(trdl,unit))
            if wait is None:
                wait=self.wait
            sleep(wait)

    def getWaveform(self,channel):
        self.inst.write(("C{}:WF? DAT2").format(channel))
        ret=list(self.inst.read_raw())[15:]
        ret.pop() # remove last two items (message end bits)
        ret.pop()
        ret.pop(0)
        vdiv=self.query_vdiv(channel)
        ofst=self.query_ofst(channel)

        vlist=[]

        for v in ret:
            if v>127:
                v=v-255
            v=(v/25*vdiv-ofst)
            vlist.append(v)

        tdiv=self.tdiv
        sara=self.sara

        tlist=[]

        for i in range(len(vlist)):
            t=-tdiv*7+i/sara
            tlist.append(t)

        return tlist,vlist

    def waveformSetup(self, FP=None, NP=None, SP=None, wait=None):
        #FP: First point
        # address of first data point to be sent
        # index starts at 0
        #NP: Number of points
        # how many points should be transmitted
        # 0: send all
        # 1: send 1
        # 500: send <= 500
        #SP: Sparsing
        # interval between data points
        # 0: send all
        # 1: send all
        # 2: send every other
        # 5: send every 5th

        if FP is None:
            FP=self.querySetup()[0]
        if NP is None:
            NP=self.querySetup()[1]
        elif NP.lower()=='all':
            NP='0'
        if SP is None:
            SP=self.querySetup()[2]

        self.inst.write(("WFSU? FP,{},NP,{},SP,{}").format(FP,NP,SP))
        # default: FP=0,NP=1000,SP=4
        if wait is None:
            wait=self.wait
        sleep(wait)

    def querySetup(self):
        ret=self.inst.query("WFSU?")
        ret=ret.strip("'")
        lst=ret.split(',')
        return [float(lst[1]),float(lst[3]),float(lst[5])]
        # format: [FP,NP,SP]

    def startAcq(self,wait=None):
        self.inst.write("TRMD AUTO")
        if wait is None:
            wait=self.wait
        sleep(wait)

    def stopAcq(self,wait=None):
        self.inst.write("STOP")
        if wait is None:
            wait=self.wait
        sleep(wait)

    def isAcq(self):
        ret=self.inst.query("TRMD?")
        if ret=="STOP\n":
            return False
        else:
            return True

