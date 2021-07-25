#!/usr/env/bin python
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 14:06:41 2019

@author: Laurel Carpenter

"""


from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber,
        QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QMessageBox)
#import serial
#import time
import sys
import argparse

from dcps import RigolDG5000

import struct
import functools

from datetime import datetime

from math import inf

parser=argparse.ArgumentParser()
parser.add_argument('--dry_run',
                        type=bool,
                        default=False,
                        help='Run without controlling the flasher (default=False)')
args = parser.parse_args()

chr = functools.partial(struct.pack,'B')

windows_system = False
dry_run = args.dry_run

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        # start a timer ?? 
        self.qTimer = QTimer()
        self.qTimer.setInterval(500)
        self.qTimer.start()
        
        self.qTimer.timeout.connect(self.check_output)
        self.qTimer.timeout.connect(self.check_pulse)
        self.qTimer.timeout.connect(self.check_polarity)
        self.qTimer.timeout.connect(self.check_impedance)
        self.qTimer.timeout.connect(self.check_sync)
        self.qTimer.timeout.connect(self.check_syncPol)
        self.qTimer.timeout.connect(self.check_duty)
        self.qTimer.timeout.connect(self.check_pd)
        self.qTimer.timeout.connect(self.check_width)
        self.qTimer.timeout.connect(self.check_hold)
        self.qTimer.timeout.connect(self.check_lead)
        self.qTimer.timeout.connect(self.check_trail)
        
        # whether to check channel 1 and channel 2 or not
        self.check1=True
        self.check2=False

        # start with a grid layout
        mainLayout = QGridLayout()
        
        # build a PSUBox
        #### some renaming in this function may be necessary as we build the GUI up to include other elements
        
        self.create_pulser_box()
        mainLayout.addWidget(self.pulser_box,0,0)

        # set the layout of the widget gallery to mainLayout
        self.setLayout(mainLayout)

    def create_pulser_box(self):
        
        # connect to pulser
        self.Rigol=RigolDG5000('USB0::6833::1600::DG5T220100004\x00::0::INSTR')

        self.pulser_box=QGroupBox("Rigol Pulser")
        self.pulser_layout=QGridLayout()
        self.pulser_box.setLayout(self.pulser_layout)
        
        # 2 boxes for 2 channels
        self.create_box1()
        self.pulser_layout.addWidget(self.box1,0,0)
        self.create_box2()
        self.pulser_layout.addWidget(self.box2,0,1)

    def create_box1(self):

        self.box1=QGroupBox("Channel 1")
        self.box1layout=QGridLayout()
        self.box1.setLayout(self.box1layout)
        
        self.check1button=QPushButton("Toggle Using Channel 1")
        self.check1button.clicked.connect(self.toggle_check1)
        self.check1disp=QLabel("Channel 1 In Use") # display whether communicating w channel 1
        self.check1disp.setAlignment(Qt.AlignCenter)
        self.check1disp.setFrameShape(QFrame.StyledPanel)
        self.check1disp.setStyleSheet("background:limegreen")

        self.box1layout.addWidget(self.check1disp,0,0)
        self.box1layout.addWidget(self.check1button,0,1)

        # box for output and pulse
        self.create_Obox1()
        self.create_Pbox1()

        self.box1layout.addWidget(self.Obox1,1,0)
        self.box1layout.addWidget(self.Pbox1,1,1)

    def create_box2(self):

        self.box2=QGroupBox("Channel 2")
        self.box2layout=QGridLayout()
        self.box2.setLayout(self.box2layout)
        
        self.check2button=QPushButton("Toggle Using Channel 2")
        self.check2button.clicked.connect(self.toggle_check2)
        self.check2disp=QLabel("Channel 2 Not In Use") # display whether communicating w channel 2
        self.check2disp.setAlignment(Qt.AlignCenter)
        self.check2disp.setFrameShape(QFrame.StyledPanel)
        self.check2disp.setStyleSheet("background:red")
        
        self.box2layout.addWidget(self.check2disp,0,0)
        self.box2layout.addWidget(self.check2button,0,1)

        # output and pulse
        self.create_Obox2()
        self.create_Pbox2()

        self.box2layout.addWidget(self.Obox2,1,0)
        self.box2layout.addWidget(self.Pbox2,1,1)

    def create_Obox1(self):

        # box for output-related controls
        # controls that use the ':OUTP' command
        self.Obox1=QGroupBox("Output")
        self.Olayout1=QVBoxLayout()
        self.Obox1.setLayout(self.Olayout1)

        self.create_outBox1() # toggle/display output on/off
        self.create_polBox1() # toggle/display polarity
        self.create_impBox1() # toggle/display impedance
        self.create_syncBox1() # toggle/display sync on/off
        self.create_syncPolBox1() # toggle/display sync polarity

        self.Olayout1.addWidget(self.outBox1)
        self.Olayout1.addWidget(self.polBox1)
        self.Olayout1.addWidget(self.impBox1)
        self.Olayout1.addWidget(self.syncBox1)
        self.Olayout1.addWidget(self.syncPolBox1)

    def create_Obox2(self):

        self.Obox2=QGroupBox("Output")
        self.Olayout2=QVBoxLayout()
        self.Obox2.setLayout(self.Olayout2)

        self.create_outBox2() # output on/off
        self.create_polBox2() # polarity
        self.create_impBox2() # impedance
        self.create_syncBox2() # sync
        self.create_syncPolBox2() # sync polarity

        self.Olayout2.addWidget(self.outBox2)
        self.Olayout2.addWidget(self.polBox2)
        self.Olayout2.addWidget(self.impBox2)
        self.Olayout2.addWidget(self.syncBox2)
        self.Olayout2.addWidget(self.syncPolBox2)

    def create_outBox1(self):

        self.outBox1=QGroupBox("On/Off")
        self.outLayout1=QVBoxLayout()
        self.outBox1.setLayout(self.outLayout1)

        self.Obutton1=QPushButton("Toggle Output") # click button to change output
        self.Obutton1.clicked.connect(lambda: self.toggle_output(1))

        self.Odisplay1=QLabel() # display on or off

        self.Odisplay1.setAlignment(Qt.AlignCenter)
        self.Odisplay1.setFrameShape(QFrame.StyledPanel)

        self.was_on1=self.Rigol.isOutputOn(1) # checking output
        # was_on is used later to determine previous state of output
        # here it acts as the initial state of output

        if self.was_on1: # green if on
            self.Odisplay1.setText("Output 1 is On")
            self.Odisplay1.setStyleSheet("background:limegreen")
        else: # red if off
            self.Odisplay1.setText("Output 1 is Off")
            self.Odisplay1.setStyleSheet("background:red")

        self.outLayout1.addWidget(self.Odisplay1)
        self.outLayout1.addWidget(self.Obutton1)

    def create_outBox2(self):

        self.outBox2=QGroupBox("On/Off")
        self.outLayout2=QVBoxLayout()
        self.outBox2.setLayout(self.outLayout2)

        self.Obutton2=QPushButton("Toggle Output") # click button to change output
        self.Obutton2.clicked.connect(lambda: self.toggle_output(2))

        self.Odisplay2=QLabel() # display on or off

        self.Odisplay2.setAlignment(Qt.AlignCenter)
        self.Odisplay2.setFrameShape(QFrame.StyledPanel)

        self.was_on2=self.Rigol.isOutputOn(2) # checking output

        if self.was_on2: # green if on
            self.Odisplay2.setText("Output 2 is On")
            self.Odisplay2.setStyleSheet("background:limegreen")
        else: # red if off
            self.Odisplay2.setText("Output 2 is Off")
            self.Odisplay2.setStyleSheet("background:red")

        self.outLayout2.addWidget(self.Odisplay2)
        self.outLayout2.addWidget(self.Obutton2)

    def create_polBox1(self):
        
        # essentially same deal as output toggle/display
        self.polBox1=QGroupBox("Polarity")
        self.polLayout1=QVBoxLayout()
        self.polBox1.setLayout(self.polLayout1)

        self.polButton1=QPushButton("Toggle Polarity") 
        self.polButton1.clicked.connect(lambda: self.toggle_polarity(1))

        self.polDisplay1=QLabel()

        self.polDisplay1.setAlignment(Qt.AlignCenter)
        self.polDisplay1.setFrameShape(QFrame.StyledPanel)

        self.was_norm1=self.Rigol.isNorm(1)

        if self.was_norm1: # green if normal
            self.polDisplay1.setText("Normal")
            self.polDisplay1.setStyleSheet("background:limegreen")
        else: # red if inverted
            self.polDisplay1.setText("Inverted")
            self.polDisplay1.setStyleSheet("background:red")
        
        self.polLayout1.addWidget(self.polDisplay1)
        self.polLayout1.addWidget(self.polButton1)

    def create_polBox2(self):

        self.polBox2=QGroupBox("Polarity")
        self.polLayout2=QVBoxLayout()
        self.polBox2.setLayout(self.polLayout2)

        self.polButton2=QPushButton("Toggle Polarity")
        self.polButton2.clicked.connect(lambda: self.toggle_polarity(2))

        self.polDisplay2=QLabel()

        self.polDisplay2.setAlignment(Qt.AlignCenter)
        self.polDisplay2.setFrameShape(QFrame.StyledPanel)

        self.was_norm2=self.Rigol.isNorm(2)

        if self.was_norm2: # green if normal
            self.polDisplay2.setText("Normal")
            self.polDisplay2.setStyleSheet("background:limegreen")
        else: # red if inverted
            self.polDisplay2.setText("Inverted")
            self.polDisplay2.setStyleSheet("background:red")

        self.polLayout2.addWidget(self.polDisplay2)
        self.polLayout2.addWidget(self.polButton2)

    def create_impBox1(self):

        self.impBox1=QGroupBox("Impedance [Ohms]")
        self.imp1layout=QVBoxLayout()
        self.impBox1.setLayout(self.imp1layout)

        self.imp1disp=QLCDNumber() # display impedance as LCD number
        self.imp1disp.setSegmentStyle(QLCDNumber.Flat)

        self.imp1button=QPushButton("Toggle Impedance")
        self.imp1button.clicked.connect(lambda: self.toggle_impedance(1))

        self.imp1layout.addWidget(self.imp1disp)
        self.imp1layout.addWidget(self.imp1button)

    def create_impBox2(self):

        self.impBox2=QGroupBox("Impedance [Ohms]")
        self.imp2layout=QVBoxLayout()
        self.impBox2.setLayout(self.imp2layout)

        self.imp2disp=QLCDNumber()
        self.imp2disp.setSegmentStyle(QLCDNumber.Flat)

        self.imp2button=QPushButton("Toggle Impedance")
        self.imp2button.clicked.connect(lambda: self.toggle_impedance(2))

        self.imp2layout.addWidget(self.imp2disp)
        self.imp2layout.addWidget(self.imp2button)

    def create_syncBox1(self):

        self.syncBox1=QGroupBox("Sync")
        self.sync1layout=QVBoxLayout()
        self.syncBox1.setLayout(self.sync1layout)

        self.sync1button=QPushButton("Toggle Sync") # turn sync on/off
        self.sync1button.clicked.connect(lambda: self.toggle_sync(1))

        self.sync1display=QLabel()

        self.sync1display.setAlignment(Qt.AlignCenter)
        self.sync1display.setFrameShape(QFrame.StyledPanel)

        self.was_sync1=self.Rigol.isSyncOn(1) # like was_on

        if self.was_sync1: # green if on
            self.sync1display.setText("Sync is On")
            self.sync1display.setStyleSheet("background:limegreen")
        else: # red if off
            self.sync1display.setText("Sync is Off")
            self.sync1display.setStyleSheet("background:red")

        self.sync1layout.addWidget(self.sync1display)
        self.sync1layout.addWidget(self.sync1button)

    def create_syncPolBox1(self):

        self.syncPolBox1=QGroupBox("Sync Polarity")
        self.syncPol1layout=QVBoxLayout()
        self.syncPolBox1.setLayout(self.syncPol1layout)

        self.syncPolButton1=QPushButton("Toggle Sync Polarity") # set sync polarity pos/neg
        self.syncPolButton1.clicked.connect(lambda: self.toggle_syncPol(1))
        
        self.syncPolDisplay1=QLabel()

        self.syncPolDisplay1.setAlignment(Qt.AlignCenter)
        self.syncPolDisplay1.setFrameShape(QFrame.StyledPanel)

        self.was_syncPol1=self.Rigol.isSyncPolPos(1) # like was_on and was_sync

        if self.was_syncPol1: # green if positive
            self.syncPolDisplay1.setText("Positive")
            self.syncPolDisplay1.setStyleSheet("background:limegreen")
        else: # red if negative
            self.syncPolDisplay1.setText("Negative")
            self.syncPolDisplay1.setStyleSheet("background:red")

        self.syncPol1layout.addWidget(self.syncPolDisplay1)
        self.syncPol1layout.addWidget(self.syncPolButton1)

    def create_syncBox2(self):

        self.syncBox2=QGroupBox("Sync")
        self.sync2layout=QVBoxLayout()
        self.syncBox2.setLayout(self.sync2layout)

        self.sync2button=QPushButton("Toggle Sync") #on/off
        self.sync2button.clicked.connect(lambda: self.toggle_sync(2))

        self.sync2display=QLabel()

        self.sync2display.setAlignment(Qt.AlignCenter)
        self.sync2display.setFrameShape(QFrame.StyledPanel)

        self.was_sync2=self.Rigol.isSyncOn(2)

        if self.was_sync2: # green if on
            self.sync2display.setText("Sync is On")
            self.sync2display.setStyleSheet("background:limegreen")
        else: # red if off
            self.sync2display.setText("Sync is Off")
            self.sync2display.setStyleSheet("background:red")

        self.sync2layout.addWidget(self.sync2display)
        self.sync2layout.addWidget(self.sync2button)

    def create_syncPolBox2(self):

        self.syncPolBox2=QGroupBox("Sync Polarity")
        self.syncPol2layout=QVBoxLayout()
        self.syncPolBox2.setLayout(self.syncPol2layout)

        self.syncPolButton2=QPushButton("Toggle Sync Polarity")
        self.syncPolButton2.clicked.connect(lambda: self.toggle_syncPol(2)) # pos/neg

        self.syncPolDisplay2=QLabel()

        self.syncPolDisplay2.setAlignment(Qt.AlignCenter)
        self.syncPolDisplay2.setFrameShape(QFrame.StyledPanel)

        self.was_syncPol2=self.Rigol.isSyncPolPos(2)

        if self.was_syncPol2: # green if on
            self.syncPolDisplay2.setText("Positive")
            self.syncPolDisplay2.setStyleSheet("background:limegreen")
        else: # red if off
            self.syncPolDisplay2.setText("Negative")
            self.syncPolDisplay2.setStyleSheet("background:red")

        self.syncPol2layout.addWidget(self.syncPolDisplay2)
        self.syncPol2layout.addWidget(self.syncPolButton2)

    def create_Pbox1(self):

        self.Pbox1=QGroupBox("Pulse")
        self.Playout1=QGridLayout()
        self.Pbox1.setLayout(self.Playout1)

        self.create_freq1box() #frequency
        self.create_amp1box() # amplitude
        self.create_os1box() # offset
        self.create_delay1box() # delay

        self.create_duty1box() # duty cycle
        self.create_pd1box() # pulse delay
        self.create_hold1box() # toggle holding (width/duty)
        self.create_width1box() # pulse width
        self.create_lead1box() # transition leading
        self.create_trail1box() # transition trailing

        self.pulse1button=QPushButton("Send Pulse")
        self.pulse1button.clicked.connect(self.on_pulse1_clicked)

        self.Playout1.addWidget(self.freq1box,0,0)
        self.Playout1.addWidget(self.amp1box,0,1)
        self.Playout1.addWidget(self.os1box,1,0)
        self.Playout1.addWidget(self.delay1box,1,1)
        self.Playout1.addWidget(self.pulse1button,2,0,1,2)
        self.Playout1.addWidget(self.duty1box,3,0)
        self.Playout1.addWidget(self.pd1box,4,1)
        self.Playout1.addWidget(self.width1box,3,1)
        self.Playout1.addWidget(self.hold1box,4,0)
        self.Playout1.addWidget(self.lead1box,5,0)
        self.Playout1.addWidget(self.trail1box,5,1)


    def create_Pbox2(self):

        self.Pbox2=QGroupBox("Pulse")
        self.Playout2=QGridLayout()
        self.Pbox2.setLayout(self.Playout2)

        self.create_freq2box() # frequency
        self.create_amp2box() # amplitude
        self.create_os2box() # offset
        self.create_delay2box() # delay

        self.create_duty2box() # duty cycle
        self.create_pd2box() # pulse delay
        self.create_hold2box() # toggle holding (width/duty)
        self.create_width2box() # pulse width
        self.create_lead2box() # transition leading
        self.create_trail2box() # transition trailing

        self.pulse2button=QPushButton("Send Pulse")
        self.pulse2button.clicked.connect(self.on_pulse2_clicked)

        self.Playout2.addWidget(self.freq2box,0,0)
        self.Playout2.addWidget(self.amp2box,0,1)
        self.Playout2.addWidget(self.os2box,1,0)
        self.Playout2.addWidget(self.delay2box,1,1)
        self.Playout2.addWidget(self.pulse2button,2,0,1,2)
        self.Playout2.addWidget(self.duty2box,3,0)
        self.Playout2.addWidget(self.pd2box,4,1)
        self.Playout2.addWidget(self.width2box,3,1)
        self.Playout2.addWidget(self.hold2box,4,0)
        self.Playout2.addWidget(self.lead2box,5,0)
        self.Playout2.addWidget(self.trail2box,5,1)

    def create_freq1box(self):
        self.freq1box=QGroupBox("Frequency [Hz]")
        self.freq1layout=QVBoxLayout()
        self.freq1box.setLayout(self.freq1layout)

        self.freq1disp=QLCDNumber() # display freq as LCD number
        self.freq1disp.setSegmentStyle(QLCDNumber.Flat)
        
        self.freq1setLabel=QLabel("Set Frequency")
        self.freq1set=QLineEdit() # input new freq

        self.freq1layout.addWidget(self.freq1disp)
        self.freq1layout.addWidget(self.freq1setLabel)
        self.freq1layout.addWidget(self.freq1set)

    def create_amp1box(self):
        self.amp1box=QGroupBox("Amplitude [Vpp]")
        self.amp1layout=QVBoxLayout()
        self.amp1box.setLayout(self.amp1layout)

        self.amp1disp=QLCDNumber() # display
        self.amp1disp.setSegmentStyle(QLCDNumber.Flat)
        
        self.amp1setLabel=QLabel("Set Amplitude")
        self.amp1set=QLineEdit() # input

        self.amp1layout.addWidget(self.amp1disp)
        self.amp1layout.addWidget(self.amp1setLabel)
        self.amp1layout.addWidget(self.amp1set)

    def create_os1box(self):
        self.os1box=QGroupBox("Offset [Vdc]")
        self.os1layout=QVBoxLayout()
        self.os1box.setLayout(self.os1layout)

        self.os1disp=QLCDNumber() # display
        self.os1disp.setSegmentStyle(QLCDNumber.Flat)
        
        self.os1setLabel=QLabel("Set Offset")
        self.os1set=QLineEdit() # input

        self.os1layout.addWidget(self.os1disp)
        self.os1layout.addWidget(self.os1setLabel)
        self.os1layout.addWidget(self.os1set)

    def create_delay1box(self):
        self.delay1box=QGroupBox("Delay [s]")
        self.delay1layout=QVBoxLayout()
        self.delay1box.setLayout(self.delay1layout)

        self.delay1disp=QLCDNumber() # display
        self.delay1disp.setSegmentStyle(QLCDNumber.Flat)
        
        self.delay1setLabel=QLabel("Set Delay")
        self.delay1set=QLineEdit() # input

        self.delay1layout.addWidget(self.delay1disp)
        self.delay1layout.addWidget(self.delay1setLabel)
        self.delay1layout.addWidget(self.delay1set)

    def create_freq2box(self):
        self.freq2box=QGroupBox("Frequency [Hz]")
        self.freq2layout=QVBoxLayout()
        self.freq2box.setLayout(self.freq2layout)

        self.freq2disp=QLCDNumber() # display
        self.freq2disp.setSegmentStyle(QLCDNumber.Flat)

        self.freq2setLabel=QLabel("Set Frequency")
        self.freq2set=QLineEdit() # input

        self.freq2layout.addWidget(self.freq2disp)
        self.freq2layout.addWidget(self.freq2setLabel)
        self.freq2layout.addWidget(self.freq2set)

    def create_amp2box(self):
        self.amp2box=QGroupBox("Amplitude [Vpp]")
        self.amp2layout=QVBoxLayout()
        self.amp2box.setLayout(self.amp2layout)

        self.amp2disp=QLCDNumber() # display
        self.amp2disp.setSegmentStyle(QLCDNumber.Flat)

        self.amp2setLabel=QLabel("Set Amplitude")
        self.amp2set=QLineEdit() # input

        self.amp2layout.addWidget(self.amp2disp)
        self.amp2layout.addWidget(self.amp2setLabel)
        self.amp2layout.addWidget(self.amp2set)

    def create_os2box(self):
        self.os2box=QGroupBox("Offset [Vdc]")
        self.os2layout=QVBoxLayout()
        self.os2box.setLayout(self.os2layout)

        self.os2disp=QLCDNumber() # display
        self.os2disp.setSegmentStyle(QLCDNumber.Flat)

        self.os2setLabel=QLabel("Set Offset")
        self.os2set=QLineEdit() # input

        self.os2layout.addWidget(self.os2disp)
        self.os2layout.addWidget(self.os2setLabel)
        self.os2layout.addWidget(self.os2set)

    def create_delay2box(self):
        self.delay2box=QGroupBox("Delay [s]")
        self.delay2layout=QVBoxLayout()
        self.delay2box.setLayout(self.delay2layout)

        self.delay2disp=QLCDNumber() # display
        self.delay2disp.setSegmentStyle(QLCDNumber.Flat)

        self.delay2setLabel=QLabel("Set Delay")
        self.delay2set=QLineEdit() # input

        self.delay2layout.addWidget(self.delay2disp)
        self.delay2layout.addWidget(self.delay2setLabel)
        self.delay2layout.addWidget(self.delay2set)

    def create_duty1box(self):
        self.duty1box=QGroupBox("Duty Cycle [%]")
        self.duty1layout=QVBoxLayout()
        self.duty1box.setLayout(self.duty1layout)

        self.duty1disp=QLCDNumber() # display
        self.duty1disp.setSegmentStyle(QLCDNumber.Flat)

        self.duty1set=QLineEdit() # input
        self.duty1button=QPushButton("Set Duty Cycle")
        self.duty1button.clicked.connect(self.on_duty1_clicked) # apply input

        self.duty1layout.addWidget(self.duty1disp)
        self.duty1layout.addWidget(self.duty1set)
        self.duty1layout.addWidget(self.duty1button)

    def create_pd1box(self):
        self.pd1box=QGroupBox("Pulse Delay [s]")
        self.pd1layout=QVBoxLayout()
        self.pd1box.setLayout(self.pd1layout)

        self.pd1disp=QLCDNumber() # display
        self.pd1disp.setSegmentStyle(QLCDNumber.Flat)

        self.pd1set=QLineEdit() # input
        self.pd1button=QPushButton("Set Pulse Delay")
        self.pd1button.clicked.connect(self.on_pd1_clicked) # apply

        self.pd1layout.addWidget(self.pd1disp)
        self.pd1layout.addWidget(self.pd1set)
        self.pd1layout.addWidget(self.pd1button)

    def create_hold1box(self):
        self.hold1box=QGroupBox("Hold Width/Duty")
        self.hold1layout=QVBoxLayout()
        self.hold1box.setLayout(self.hold1layout)

        self.hold1button=QPushButton("Toggle Hold") # toggle
        self.hold1button.clicked.connect(lambda: self.toggle_hold(1))

        self.hold1disp=QLabel() # display

        self.hold1disp.setAlignment(Qt.AlignCenter)
        self.hold1disp.setFrameShape(QFrame.StyledPanel)

        self.was_width1=self.Rigol.isWidth(1) # like was_on, was_sync, etc

        if self.was_width1: # yellow if holding width
            self.hold1disp.setText("Holding Width")
            self.hold1disp.setStyleSheet("background:yellow")
        else: # blue if holding duty cycle
            self.hold1disp.setText("Holding Duty")
            self.hold1disp.setStyleSheet("background:cyan")
        
        self.hold1layout.addWidget(self.hold1disp)
        self.hold1layout.addWidget(self.hold1button)

    def create_width1box(self):
        self.width1box=QGroupBox("Pulse Width [s]")
        self.width1layout=QVBoxLayout()
        self.width1box.setLayout(self.width1layout)

        self.width1disp=QLCDNumber() # display
        self.width1disp.setSegmentStyle(QLCDNumber.Flat)

        self.width1set=QLineEdit() # input
        self.width1button=QPushButton("Set Pulse Width")
        self.width1button.clicked.connect(self.on_width1_clicked) # apply

        self.width1layout.addWidget(self.width1disp)
        self.width1layout.addWidget(self.width1set)
        self.width1layout.addWidget(self.width1button)

    def create_lead1box(self):
        self.lead1box=QGroupBox("Transition Leading [s]")
        self.lead1layout=QVBoxLayout()
        self.lead1box.setLayout(self.lead1layout)

        self.lead1disp=QLCDNumber() # display
        self.lead1disp.setSegmentStyle(QLCDNumber.Flat)

        self.lead1set=QLineEdit() # input
        self.lead1button=QPushButton("Set Transition Leading")
        self.lead1button.clicked.connect(self.on_lead1_clicked) # apply

        self.lead1layout.addWidget(self.lead1disp)
        self.lead1layout.addWidget(self.lead1set)
        self.lead1layout.addWidget(self.lead1button)

    def create_trail1box(self):
        self.trail1box=QGroupBox("Transition Trailing [s]")
        self.trail1layout=QVBoxLayout()
        self.trail1box.setLayout(self.trail1layout)

        self.trail1disp=QLCDNumber() # display
        self.trail1disp.setSegmentStyle(QLCDNumber.Flat)

        self.trail1set=QLineEdit() # input
        self.trail1button=QPushButton("Set Transition Trailing")
        self.trail1button.clicked.connect(self.on_trail1_clicked) # apply

        self.trail1layout.addWidget(self.trail1disp)
        self.trail1layout.addWidget(self.trail1set)
        self.trail1layout.addWidget(self.trail1button)

    def create_duty2box(self):
        self.duty2box=QGroupBox("Duty Cycle [%]")
        self.duty2layout=QVBoxLayout()
        self.duty2box.setLayout(self.duty2layout)

        self.duty2disp=QLCDNumber() # display
        self.duty2disp.setSegmentStyle(QLCDNumber.Flat)

        self.duty2set=QLineEdit() # input
        self.duty2button=QPushButton("Set Duty Cycle")
        self.duty2button.clicked.connect(self.on_duty2_clicked) # apply

        self.duty2layout.addWidget(self.duty2disp)
        self.duty2layout.addWidget(self.duty2set)
        self.duty2layout.addWidget(self.duty2button)

    def create_pd2box(self):
        self.pd2box=QGroupBox("Pulse Delay [s]")
        self.pd2layout=QVBoxLayout()
        self.pd2box.setLayout(self.pd2layout)

        self.pd2disp=QLCDNumber() # display
        self.pd2disp.setSegmentStyle(QLCDNumber.Flat)

        self.pd2set=QLineEdit() # input
        self.pd2button=QPushButton("Set Pulse Delay")
        self.pd2button.clicked.connect(self.on_pd2_clicked) # apply

        self.pd2layout.addWidget(self.pd2disp)
        self.pd2layout.addWidget(self.pd2set)
        self.pd2layout.addWidget(self.pd2button)

    def create_hold2box(self):
        self.hold2box=QGroupBox("Hold Width/Duty")
        self.hold2layout=QVBoxLayout()
        self.hold2box.setLayout(self.hold2layout)

        self.hold2button=QPushButton("Toggle Hold") # toggle
        self.hold2button.clicked.connect(lambda: self.toggle_hold(2))

        self.hold2disp=QLabel() # display

        self.hold2disp.setAlignment(Qt.AlignCenter)
        self.hold2disp.setFrameShape(QFrame.StyledPanel)

        self.was_width2=self.Rigol.isWidth(2) # like was_on

        if self.was_width2: # yellow if holding width
            self.hold2disp.setText("Holding Width")
            self.hold2disp.setStyleSheet("background:yellow")
        else: # blue if holding duty
            self.hold2disp.setText("Holding Duty")
            self.hold2disp.setStyleSheet("background:cyan")

        self.hold2layout.addWidget(self.hold2disp)
        self.hold2layout.addWidget(self.hold2button)

    def create_width2box(self):
        self.width2box=QGroupBox("Pulse Width [s]")
        self.width2layout=QVBoxLayout()
        self.width2box.setLayout(self.width2layout)

        self.width2disp=QLCDNumber() # display
        self.width2disp.setSegmentStyle(QLCDNumber.Flat)

        self.width2set=QLineEdit() # input
        self.width2button=QPushButton("Set Pulse Width")
        self.width2button.clicked.connect(self.on_width2_clicked) # apply

        self.width2layout.addWidget(self.width2disp)
        self.width2layout.addWidget(self.width2set)
        self.width2layout.addWidget(self.width2button)

    def create_lead2box(self):
        self.lead2box=QGroupBox("Transition Leading [s]")
        self.lead2layout=QVBoxLayout()
        self.lead2box.setLayout(self.lead2layout)

        self.lead2disp=QLCDNumber() # display
        self.lead2disp.setSegmentStyle(QLCDNumber.Flat)

        self.lead2set=QLineEdit() # input
        self.lead2button=QPushButton("Set Transition Leading")
        self.lead2button.clicked.connect(self.on_lead2_clicked) # apply

        self.lead2layout.addWidget(self.lead2disp)
        self.lead2layout.addWidget(self.lead2set)
        self.lead2layout.addWidget(self.lead2button)

    def create_trail2box(self):
        self.trail2box=QGroupBox("Transition Trailing [s]")
        self.trail2layout=QVBoxLayout()
        self.trail2box.setLayout(self.trail2layout)

        self.trail2disp=QLCDNumber() # display
        self.trail2disp.setSegmentStyle(QLCDNumber.Flat)

        self.trail2set=QLineEdit() # input
        self.trail2button=QPushButton("Set Transition Trailing")
        self.trail2button.clicked.connect(self.on_trail2_clicked) # apply

        self.trail2layout.addWidget(self.trail2disp)
        self.trail2layout.addWidget(self.trail2set)
        self.trail2layout.addWidget(self.trail2button)



    def toggle_output(self, channel=1):
        if not dry_run: # don't want to actually turn on if dry run
            if (channel==1) and not self.check1:
                self.toggle_check1()
            if (channel==2) and not self.check2:
                self.toggle_check2()

            if self.Rigol.isOutputOn(channel): # if on
                self.Rigol.outputOff(channel) # turn off
            else: # if off
                self.Rigol.outputOn(channel) # turn on
        else: 
            print("Pranked! dry run :)")

    def check_output(self): # checks both outputs at the same time
        if self.check1:
            if self.was_on1 != self.Rigol.isOutputOn(1): # if current state is not equal to previous state
                # this check is here so that if nothing has changed,
                # we don't have to 'reset' the text and color
                # of the display every half second to the same thing
                self.was_on1=self.Rigol.isOutputOn(1) # set new 'previous state'
                if self.was_on1: # green if on
                    self.Odisplay1.setText("Output 1 is On")
                    self.Odisplay1.setStyleSheet("background:limegreen")
                else: # red if off
                    self.Odisplay1.setText("Output 1 is Off")
                    self.Odisplay1.setStyleSheet("background:red")
        if self.check2:
            if self.was_on2 != self.Rigol.isOutputOn(2): # same as above
                self.was_on2=self.Rigol.isOutputOn(2)
                if self.was_on2:
                    self.Odisplay2.setText("Output 2 is On")
                    self.Odisplay2.setStyleSheet("background:limegreen")
                else:
                    self.Odisplay2.setText("Output 2 is Off")
                    self.Odisplay2.setStyleSheet("background:red")

    def toggle_polarity(self, channel=1):
        if not dry_run: # don't want to actually change if dry run
            if (channel==1) and not self.check1:
                self.toggle_check1()
            if (channel==2) and not self.check2:
                self.toggle_check2()

            if self.Rigol.isNorm(channel):
                self.Rigol.polarityInv(channel)
            else:
                self.Rigol.polarityNorm(channel)
        else:
            print("Pranked! dry run :)")

    def check_polarity(self): # checks both at same time, same concept as check_output
        if self.check1:
            if self.was_norm1 != self.Rigol.isNorm(1):
                self.was_norm1=self.Rigol.isNorm(1)
                if self.was_norm1: # green if normal
                    self.polDisplay1.setText("Normal")
                    self.polDisplay1.setStyleSheet("background:limegreen")
                else: # red if inverted
                    self.polDisplay1.setText("Inverted")
                    self.polDisplay1.setStyleSheet("background:red")

        if self.check2:
            if self.was_norm2 != self.Rigol.isNorm(2):
                self.was_norm2=self.Rigol.isNorm(2)
                if self.was_norm2: # green if normal
                    self.polDisplay2.setText("Normal")
                    self.polDisplay2.setStyleSheet("background:limegreen")
                else: # red if inverted
                    self.polDisplay2.setText("Inverted")
                    self.polDisplay2.setStyleSheet("background:red")

    def toggle_sync(self, channel=1):
        if not dry_run: # don't want to actually change if dry run
            if (channel==1) and not self.check1:
                self.toggle_check1()
            if (channel==2) and not self.check2:
                self.toggle_check2()

            if self.Rigol.isSyncOn(channel):
                self.Rigol.syncOff(channel)
            else:
                self.Rigol.syncOn(channel)
        else:
            print("Pranked! dry run :)")

    def toggle_syncPol(self, channel=1): 
        if not dry_run: # don't want to actually change if dry run
            if (channel==1) and not self.check1:
                self.toggle_check1()
            if (channel==2) and not self.check2:
                self.toggle_check2()

            if self.Rigol.isSyncPolPos(channel):
                self.Rigol.syncPolNeg(channel)
            else:
                self.Rigol.syncPolPos(channel)
        else:
            print("Pranked! dry run :)")

    def check_sync(self): # checks both channels at same time, same as check_output
        if self.check1:
            if self.was_sync1 != self.Rigol.isSyncOn(1):
                self.was_sync1=self.Rigol.isSyncOn(1)
                if self.was_sync1: # green if on
                    self.sync1display.setText("Sync is On")
                    self.sync1display.setStyleSheet("background:limegreen")
                else: # red if off
                    self.sync1display.setText("Sync is Off")
                    self.sync1display.setStyleSheet("background:red")

        if self.check2:
            if self.was_sync2 != self.Rigol.isSyncOn(2):
                self.was_sync2=self.Rigol.isSyncOn(2)
                if self.was_sync2: # green if on
                    self.sync2display.setText("Sync is On")
                    self.sync2display.setStyleSheet("background:limegreen")
                else: # red if off
                    self.sync2display.setText("Sync is Off")
                    self.sync2display.setStyleSheet("background:red")

    def check_syncPol(self): # same as above
        if self.check1:
            if self.was_syncPol1 != self.Rigol.isSyncPolPos(1):
                self.was_syncPol1=self.Rigol.isSyncPolPos(1)
                if self.was_syncPol1: # green if positive
                    self.syncPolDisplay1.setText("Positive")
                    self.syncPolDisplay1.setStyleSheet("background:limegreen")
                else: # red if negative
                    self.syncPolDisplay1.setText("Negative")
                    self.syncPolDisplay1.setStyleSheet("background:red")

        if self.check2:
            if self.was_syncPol2 != self.Rigol.isSyncPolPos(2):
                self.was_syncPol2=self.Rigol.isSyncPolPos(2)
                if self.was_syncPol2: # green if positive
                    self.syncPolDisplay2.setText("Positive")
                    self.syncPolDisplay2.setStyleSheet("background:limegreen")
                else: # red if negative
                    self.syncPolDisplay2.setText("Negative")
                    self.syncPolDisplay2.setStyleSheet("background:red")

    def toggle_impedance(self, channel=1):
        if not dry_run: # don't want to actually change if dry run
            if (channel==1) and not self.check1:
                self.toggle_check1()
            if (channel==2) and not self.check2:
                self.toggle_check2()

            if self.Rigol.isImpInf(channel): # if infinite
                self.Rigol.setImpedance(50,channel) # set to 50 ohms
            else: # if 50 ohms (or something else?)
                self.Rigol.setImpedance(inf,channel) # set infinite
        else:
            print("Pranked! dry run :^)")

    def on_pulse1_clicked(self):
        if not dry_run:
            if not self.check1:
                self.toggle_check1()
            # take frequency, amplitude, offset, and delay from QLineEdit boxes
            freq=self.freq1set.text() 
            amp=self.amp1set.text()
            offset=self.os1set.text()
            delay=self.delay1set.text()
            channel=1

            self.Rigol.applyPulse(freq, amp, offset, delay, channel)
        else:
            print("dry run")

    def on_pulse2_clicked(self):
        if not dry_run:
            if not self.check2:
                self.toggle_check2()
            # take frequency, amplitude, offset, and delay from QLineEdit boxes
            freq=self.freq2set.text()
            amp=self.amp2set.text()
            offset=self.os2set.text()
            delay=self.delay2set.text()
            channel=2

            self.Rigol.applyPulse(freq, amp, offset, delay, channel)
        else:
            print("dry run")

    def on_duty1_clicked(self):
        if not dry_run:
            if not self.check1:
                self.toggle_check1()
            duty=self.duty1set.text() # take duty cycle from QLineEdit box
            self.Rigol.dutyCycle(duty,1)
        else:
            print("dry run")

    def on_duty2_clicked(self):
        if not dry_run:
            if not self.check2:
                self.toggle_check2()
            duty=self.duty2set.text() # take duty cycle from QLineEdit box
            self.Rigol.dutyCycle(duty,2)
        else:
            print("dry run")

    def on_pd1_clicked(self):
        if not dry_run:
            if not self.check1:
                self.toggle_check1()
            pd=self.pd1set.text()
            self.Rigol.pulseDelay(pd,1)
        else:
            print("dry run")

    def on_pd2_clicked(self):
        if not dry_run:
            if not self.check2:
                self.toggle_check2()
            pd=self.pd2set.text()
            self.Rigol.pulseDelay(pd,2)
        else:
            print("dry run")

    def toggle_hold(self, channel=1):
        if not dry_run:
            if (channel==1) and not self.check1:
                self.toggle_check1()
            if (channel==2) and not self.check2:
                self.toggle_check2()

            if self.Rigol.isWidth(channel): # if holding width
                self.Rigol.holdDuty(channel) # hold duty
            else: # if holding duty
                self.Rigol.holdWidth(channel) # hold width
        else:
            print("Pranked! dry run :)")

    def on_lead1_clicked(self):
        if not dry_run:
            if not self.check1:
                self.toggle_check1()
            lead=self.lead1set.text()
            self.Rigol.transitionLeading(lead,1)
        else:
            print("dry run")

    def on_lead2_clicked(self):
        if not dry_run:
            if not self.check2:
                self.toggle_check2()
            lead=self.lead2set.text()
            self.Rigol.transitionLeading(lead,2)
        else:
            print("dry run")

    def on_trail1_clicked(self):
        if not dry_run:
            if not self.check1:
                self.toggle_check1()
            trail=self.trail1set.text()
            self.Rigol.transitionTrailing(trail,1)
        else:
            print("dry run")

    def on_trail2_clicked(self):
        if not dry_run:
            if not self.check2:
                self.toggle_check2()
            trail=self.trail2set.text()
            self.Rigol.transitionTrailing(trail,2)
        else:
            print('dry run')

    def on_width1_clicked(self):
        if not dry_run:
            if not self.check1:
                self.toggle_check1()
            width=self.width1set.text()
            self.Rigol.pulseWidth(width,1)
        else:
            print('dry run')

    def on_width2_clicked(self):
        if not dry_run:
            if not self.check2:
                self.toggle_check2()
            width=self.width2set.text()
            self.Rigol.pulseWidth(width,2)
        else:
            print(dry_run)

    def check_impedance(self):
        if self.check1:
            imp1=self.Rigol.queryImpedance(1)
            if imp1==inf:
                self.imp1disp.display("h19h") # "high" in LCD display
            else:
                self.imp1disp.display(f"{imp1:.2f}")
        if self.check2:
            imp2=self.Rigol.queryImpedance(2)
            if imp2==inf:
                self.imp2disp.display("h19h") # "high" in LCD display
            else:
                self.imp2disp.display(f"{imp2:.2f}")

    def check_pulse(self):
        if self.check1:
            # queryApply returns list [waveform name, frequency, amplitude, offset, delay]
            lst1=self.Rigol.queryApply(1)
            # lst[0] is ignored since we don't need waveform name here--we know it's a pulse
            self.freq1disp.display(lst1[1])
            self.amp1disp.display(f"{lst1[2]:.2f}")
            self.os1disp.display(f"{lst1[3]:.2f}")
            self.delay1disp.display(f"{lst1[4]:.2f}")
        
        if self.check2: # if we want to check channel 2 as well
            lst2=self.Rigol.queryApply(2)
            self.freq2disp.display(lst2[1])
            self.amp2disp.display(f"{lst2[2]:.2f}")
            self.os2disp.display(f"{lst2[3]:.2f}")
            self.delay2disp.display(f"{lst2[4]:.2f}")

    def check_hold(self):
        if self.check1:
            if self.was_width1 != self.Rigol.isWidth(1): # like was_on 
                self.was_width1=self.Rigol.isWidth(1)
                if self.was_width1: # yellow if holding width
                    self.hold1disp.setText("Holding Width")
                    self.hold1disp.setStyleSheet("background:yellow")
                else: # blue if holding duty
                    self.hold1disp.setText("Holding Duty")
                    self.hold1disp.setStyleSheet("background:cyan")
        if self.check2:
            if self.was_width2 != self.Rigol.isWidth(2):
                self.was_width2=self.Rigol.isWidth(2)
                if self.was_width2: # yellow if holding width
                    self.hold2disp.setText("Holding Width")
                    self.hold2disp.setStyleSheet("background:yellow")
                else: # blue if holding duty
                    self.hold2disp.setText("Holding Duty")
                    self.hold2disp.setStyleSheet("background:cyan")

    def check_duty(self):
        if self.check1:
            duty1=self.Rigol.queryDutyCycle(1) # ask for duty cycle on ch1
            self.duty1disp.display(duty1) # set ch1 display
        if self.check2:
            duty2=self.Rigol.queryDutyCycle(2) # ask for duty cycle on ch2
            self.duty2disp.display(duty2) # set ch2 display

    def check_pd(self): # same as above
        if self.check1:
            pd1=self.Rigol.queryDelay(1)
            self.pd1disp.display(pd1)
        if self.check2:
            pd2=self.Rigol.queryDelay(2)
            self.pd2disp.display(pd2)

    def check_lead(self): # same as above
        if self.check1:
            lead1=self.Rigol.queryTransLead(1)
            self.lead1disp.display(lead1)
        if self.check2:
            lead2=self.Rigol.queryTransLead(2)
            self.lead2disp.display(lead2)

    def check_trail(self): # same as above
        if self.check1:
            trail1=self.Rigol.queryTransTrail(1)
            self.trail1disp.display(trail1)
        if self.check2:
            trail2=self.Rigol.queryTransTrail(2)
            self.trail2disp.display(trail2)

    def check_width(self): # same as above
        if self.check1:
            width1=self.Rigol.queryWidth(1)
            self.width1disp.display(width1)
        if self.check2:
            width2=self.Rigol.queryWidth(2)
            self.width2disp.display(width2)

    def toggle_check1(self):
        if self.check1:
            self.check1=False
            self.check1disp.setText("Channel 1 Not In Use")
            self.check1disp.setStyleSheet("background:red")
        else:
            self.check1=True
            self.check1disp.setText("Channel 1 In Use")
            self.check1disp.setStyleSheet("background:limegreen")

    def toggle_check2(self):
        if self.check2:
            self.check2=False
            self.check2disp.setText("Channel 2 Not In Use")
            self.check2disp.setStyleSheet("background:red")
        else:
            self.check2=True
            self.check2disp.setText("Channel 2 In Use")
            self.check2disp.setStyleSheet("background:limegreen")

    def closeEvent(self, event): # turn off outputs upon closing gui
        self.Rigol.outputOff(1,wait=0)
        self.Rigol.outputOff(2,wait=0)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wg=WidgetGallery()
    wg.show()
    sys.exit(app.exec_())

