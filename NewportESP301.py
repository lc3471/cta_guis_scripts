import visa 

from time import sleep

class ESP301(object):
    def __init__(self,resource,wait=0.5,max_axes=2,
            read_termination='',write_termination='/r/n',
            baud_rate=19200,timeout=2000):

        
        self.resource=resource
        self.wait=wait
        self.max_axes=max_axes
        self.read_termination=read_termination
        self.write_termination=write_termination
        self.timeout=timeout
        self.baud_rate=baud_rate

    def open_inst(self):
        rm=visa.ResourceManager()
        self.inst=rm.open_resource(self.resource,baud_rate=self.baud_rate,timeout=self.timeout)

    def close_inst(self):
        self.inst.close()

    def get_baud(self):
        return self.inst.baud_rate

    # linear compensation?
    # data acquisition?
    # define label?
    # group stuff

    # units
    def set_units(self,axis,unit):
        # unit settings:
        # 0: encoder count   1: motor step       2: milli-meter
        # 3: micro-meter     4: inch             5: milli-inch
        # 6: micro-inch      7: degree           8: gradian
        # 9: radian         10: milli-radian    11: micro-radian

        if axis<=self.max_axes:
            if type(unit)==str:
                unit=unit.lower().replace(" ","")
                retdict={"encoder count":0,"motor step":1,"mm":2,"um":3,"in":4,"min":5,"uin":6,
                        "deg":7,"grad":8,"rad":9,"mrad":10,"urad":11}
                if unit in retdict.keys():
                    unit=retdict[unit]

            self.inst.write(("{}SN{}").format(axis,unit))

    def get_units(self,axis):
        if axis<=self.max_axes:
            ret=int(self.inst.query(("{}SN?").format(axis)))
            retlist=["encoder count","motor step","mm","um","in","min","uin",
                    "deg","grad","rad","mrad","urad"]
            if ret<len(retlist):
                return retlist[ret]

    def set_res(self,axis,res):
        if axis<=self.max_axes:
            """elif not self.enc_fdbk: pass""" # set encoder feedback on with ZB command
            if res<2*10**-9:
                res=2*10**-9
            elif res>2*10**9:
                res=2*10**9
            self.inst.write(("{}SU{}").format(axis,res))

    def get_res(self,axis):
        if axis<=self.max_axes:
            ret=self.inst.query(("{}SU?").format(axis))
            return float(ret)

    def update_motor(self,axis):
        if axis<=self.max_axes:
            if not self.is_motion_done(axis):
                self.wait_motion_stop(axis)
            self.inst.write(("{}QD").format(axis))
                

            

    # device address
    def set_dev_addr(self,addr):
        # sets device address as 'addr'
        self.inst.write(("SA{}").format(addr))

    def get_dev_addr(self):
        # returns device address
        ret=self.inst.query("SA?")
        return ret

    # memory
    def get_avail_mem(self):
        # returns amount of available memory
        ret=self.inst.query("XM")
        # units: bytes
        return float(ret)


    # motor
    def motor_off(self,axis):
        # turns motor off on axis 'axis'
        if axis<=self.max_axes:
            self.inst.write(("{}MF").format(axis))

    def motor_on(self,axis):
        # turns motor on on axis 'axis'
        if axis<=self.max_axes:
            self.inst.write(("{}MO").format(axis))

    def is_motor_on(self,axis):
        # returns True if motor is on on axis 'axis', False if motor is off
        if axis<=self.max_axes:
            ret=self.inst.query(("{}MO?").format(axis))
            if ret=='0\r\n':
                return False
            else:
                return True


    # motion
    def abort_motion(self): # EMERGENCY STOP
        # stops all motion
        self.inst.write("AB")

    def is_motion_done(self,axis):
        # returns True if motion is done on axis 'axis', False if still moving
        if axis<=self.max_axes:
            ret=self.inst.query(("{}MD?").format(axis))
            if ret=='0\r\n':
                return False
            else:
                return True

    def stop_motion(self,axis):
        # stops motion on axis 'axis'
        if axis<=self.max_axes:
            self.inst.write(("{}ST").format(axis))

    def move_indef_pos(self,axis):
        # moves indefinitely in positive direction on axis 'axis'
        if axis<=self.max_axes:
            self.inst.write(("{}MV+").format(axis))

    def move_indef_neg(self,axis):
        # moves indefinitely in negative direction on axis 'axis'
        if axis<=self.max_axes:
            self.inst.write(("{}MV-").format(axis))

    def move_index_pos(self,axis):
        # moves to nearest index in positive direction on axis 'axis'
        if axis<=self.max_axes:
            self.inst.write(("{}MZ+").format(axis))

    def move_index_neg(self,axis):
        # moves to nearest index in negative direction on axis 'axis'
        if axis<=self.max_axes:
            self.inst.write(("{}MZ-").format(axis))


    # program

    def enter_prog_mode(self,p):
        # enters program mode for program number 'p'
        if p<=100:
            self.inst.write(("{}EP").format(p))

    def quit_prog_mode(self):
        # quits program mode
        self.inst.write("QP")

    def list_prog(self,p):
        # returns contents of program number 'p'
        if p<=100:
            ret=self.inst.query(("{}LP").format(p))
            return ret

    def exec_prog(self,p,n=1):
        # executes program number 'p', to repeat 'n' times
        if p<=100:
            self.inst.write(("{}EX{}").format(p,n))
       
    def erase_prog(self,p):
        # erases program number 'p'
        if p<=100:
            self.inst.write(("{}XX").format(p))

    def abort_prog(self): # WILL NOT STOP MOVE IN PROGRESS
        # aborts current program
        self.inst.write("AP")


    # position

    def get_des_pos(self,axis):
        # returns desired position on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}DP?").format(axis))
            # predef. units
            return float(ret)

    def get_act_pos(self,axis):
        # returns actual position on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}TP").format(axis))
            # predef. units
            return float(ret)

    def move_abs_pos(self,axis,pos):
        # moves to absolute position 'pos' on axis 'axis'
        if axis<=self.max_axes:
            """pos=float(pos)
            if pos < self.get_left_lim(axis):
                pos=self.get_left_lim(axis)
            elif pos > self.get_right_lim(axis):
                pos=self.get_right_lim(axis)"""
            self.inst.write(("{}PA{}").format(axis,pos))
            # predef. units

    def move_rel_pos(self,axis,disp=0):
        # moves by relative displacement 'disp' on axis 'axis'
        if axis<=self.max_axes:
            """disp=float(disp)
            if self.get_act_pos(axis)+self.disp<self.get_left_lim(axis):
                self.move_abs_pos(self.get_left_lim(axis),axis)
            elif self.get_act_pos(axis)+self.disp>self.get_right_lim(axis):
                self.move_abs_pos(self.get_right_lim(axis),axis)"""
            self.inst.write(("{}PR{}").format(axis,disp))
            # predef. units


    # velocity

    def get_des_vel(self,axis):
        # returns desired velocity on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}DV?").format(axis))
            # units: predef. units per s
            return float(ret)

    def get_act_vel(self,axis):
        # returns actual velocity on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}TV").format(axis))
            # units: predef. units per s
            return float(ret)

    def set_vel(self,axis,vel=0):
        # sets velocity 'vel' on axis 'axis'
        if axis<=self.max_axes:
            """vel=float(vel)
            if vel>self.get_max_vel(axis):
                vel=self.get_max_vel(axis)"""
            self.inst.write(("{}VA{}").format(axis,vel))
            # units: predef. units per s

    def set_max_vel(self,axis,max_):
        # sets maximum velocity to 'max_' on axis 'axis'
        if axis<=self.max_axes:
            max_=float(max_)
            if max_>2*10**9:
                max_=2*10**9
            self.inst.write(("{}VU{}").format(axis,max_))
            # units: predef. units per s

    def get_max_vel(self,axis):
        # returns maximum velocity on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}VU?").format(axis))
            # units = predef. units per s
            return float(ret)

    # accel/decel

    def set_accel(self,axis,accel=0):
        # sets acceleration to 'accel' on axis 'axis'
        if axis<=self.max_axes:
            """accel=float(accel)
            if accel>self.get_max_accel(axis):
                accel=self.get_max_accel(axis)"""
            self.inst.write(("{}AC{}").format(axis,accel))
            # units: predef. units per s^2

    def get_accel(self,axis):
        # returns acceleration on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}AC?").format(axis))
            # units: predef. units per s^2
            return float(ret)

    def set_decel(self,axis,decel=0):
        # sets deceleration to 'decel' on axis 'axis'
        if axis<self.max_axes:
            """decel=float(decel)
            if decel>self.get_max_decel(axis):
                decel=self.get_max_decel(axis)"""
            self.inst.write(("{}AG{}").format(axis,decel))
            # units: predef. units per s^2

    def get_decel(self,axis):
        # returns deceleration on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}AG?").format(axis))
            # units: predef. units per s^2
            return float(ret)

    def set_max_accel(self,axis,max_):
        # sets maximum acceleration/deceleration to 'max_' on axis 'axis'
        if axis<self.max_axes:
            max_=float(max_)
            if max_>2*10**9:
                max_=2*10**9
            self.inst.write(("{}AU{}").format(axis,max_))
            # units: predef. units per s^2

    def get_max_accel(self,axis):
        # returns maximum acceleration/deceleration on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}AU?").format(axis))
            # units: predef. units per s^2
            return float(ret)


    # limits

    def set_left_lim(self,axis,lim):
        # sets left limit to 'lim' on axis 'axis'
        if axis<=self.max_axes:
            """lim=float(lim)
            if lim<(2*10**9 * self.get_res(axis)):
                lim=2*10**9 * self.get_res(axis)"""
            self.inst.write(("{}SL{}").format(axis,lim))
            # predef. units

    def get_left_lim(self,axis):
        # returns left limit on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}SL?").format(axis))
            # predef. units
            return float(ret)

    def set_right_lim(self,axis,lim):
        # sets right limit to 'lim' on axis 'axis'
        if axis>self.max_axes:
            """lim=float(lim)
            if lim>(2*10**9 * self.get_res(axis)):
                lim=2*10**9 * self.get_res(axis)"""
            self.inst.write(("{}RL{}").format(axis,lim))
            # predef. units

    def get_right_lim(self,axis):
        # returns right limit on axis 'axis'
        if axis<=self.max_axes:
            ret=self.inst.query(("{}RL?").format(axis))
            # predef. units
            return float(ret)


    # wait

    def wait_pos(self,axis,pos):
        # waits until reaches position 'pos' on axis 'axis'
        if axis<=self.max_axes:
            self.inst.write(("{}WP{}").format(axis,pos))
            # predef. units

    def wait_motion_stop(self,axis,delay=0):
        # waits for motion to stop on axis 'axis', delays by amount 'delay'
        if axis<=self.max_axes:
            if delay>60000:
                delay=60000
            self.inst.write(("{}WS{}").format(axis,delay))
            # units: ms

    def wait_time(self,delay=0):
        # waits for amount of time 'delay'
        if delay>60000:
            delay=60000    
        self.inst.write(("WT{}").format(delay))
            # units: ms


    # home
    def define_home(self,axis,home=0):
        # defines home as 'home' on axis 'axis'
        if axis<=self.max_axes:
            """elif home<self.get_right_lim(axis) and home>self.get_left_lim(axis):
            pass"""
            self.inst.write(("{}DH{}").format(axis,home))
            # predef. units

