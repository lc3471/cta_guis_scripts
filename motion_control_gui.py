# author: Laurel Carpenter
# date 07/22/2021

from dcps import NewportESP301

from PyQt5.QtChart import QChartView, QChart, QLineSeries, QSplineSeries, QValueAxis
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber,
        QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QMessageBox)

import sys
from time import sleep

wait=100

class WidgetGallery(QDialog):
    def __init__(self,parent=None):
        super(WidgetGallery,self).__init__(parent)

        self.open_newport('ASRL/dev/ttyUSB0::INSTR')
        
        self.qTimer=QTimer()
        self.qTimer.setInterval(1000)
        self.qTimer.start()

        self.qTimer.timeout.connect(self.check_motor1)
        self.qTimer.timeout.connect(self.check_motor2)
        self.qTimer.timeout.connect(self.check_pos1)
        self.qTimer.timeout.connect(self.check_pos2)

        mainLayout=QGridLayout()
        self.create_control_box()
        mainLayout.addWidget(self.control_box)
        self.setLayout(mainLayout)


    def open_newport(self,path):
        self.newport=NewportESP301(path)
        self.newport.open_inst()

    def create_control_box(self):
        self.control_box=QGroupBox()
        self.control_layout=QHBoxLayout()
        self.control_box.setLayout(self.control_layout)

        self.create_indef_box()
        self.create_motion1box()
        self.create_motion2box()
        self.create_side_box()

        self.control_layout.addWidget(self.indef_box)
        self.control_layout.addWidget(self.side_box)
        self.control_layout.addWidget(self.motion1box)
        self.control_layout.addWidget(self.motion2box)

    def create_indef_box(self):
        self.indef_box=QGroupBox("Move by increment")
        self.indef_layout=QGridLayout()
        self.indef_box.setLayout(self.indef_layout)

        self.inclist=QComboBox()
        self.inclist.addItem('1 mm')
        self.inclist.addItem('100 \u03BCm')
        self.inclist.addItem('10 \u03BCm')
        self.inclist.addItem('1 \u03BCm')
        self.inclist.addItem('100 nm')
        self.inclist.addItem('10 nm')

        

        self.upbutton=QPushButton('^')
        self.downbutton=QPushButton('v')
        self.leftbutton=QPushButton('<')
        self.rightbutton=QPushButton('>')

        self.upbutton.clicked.connect(self.on_up_clicked)
        self.downbutton.clicked.connect(self.on_down_clicked)
        self.leftbutton.clicked.connect(self.on_left_clicked)
        self.rightbutton.clicked.connect(self.on_right_clicked)

        self.indef_layout.addWidget(self.upbutton,0,1)
        self.indef_layout.addWidget(self.downbutton,2,1)
        self.indef_layout.addWidget(self.leftbutton,1,0)
        self.indef_layout.addWidget(self.rightbutton,1,2)

    def create_side_box(self):
        self.side_box=QGroupBox()
        self.side_layout=QVBoxLayout()
        self.side_box.setLayout(self.side_layout)

        self.abort_button=QPushButton("Abort Motion")
        self.abort_button.clicked.connect(self.on_abort_clicked)

        self.abort_prog_button=QPushButton("Abort Program")
        self.abort_prog_button.clicked.connect(self.newport.abort_prog)

        self.quit_prog_button=QPushButton("Quit Programming Mode")
        self.quit_prog_button.clicked.connect(self.newport.quit_prog_mode)

        self.wait_label=QLabel("Set Wait Time [ms]")
        self.wait_edit=QLineEdit()
        self.wait_button=QPushButton("Wait")
        self.wait_button.clicked.connect(self.on_wait_clicked)
        
        self.unitmenu=QComboBox()
        self.unitmenu.addItem('encoder count')
        self.unitmenu.addItem('motor step')
        self.unitmenu.addItem('mm')
        self.unitmenu.addItem('\u03BCm')
        self.unitmenu.addItem('in')
        self.unitmenu.addItem('mIn')
        self.unitmenu.addItem('\u03BCIn')
        self.unitmenu.addItem('deg')
        self.unitmenu.addItem('grad')
        self.unitmenu.addItem('rad')
        self.unitmenu.addItem('mRad')
        self.unitmenu.addItem('\u03BCRad')

        self.newport.set_units(1,'mm')
        self.newport.set_units(2,'mm')
        self.unitlabel=QLabel('units: mm')

        self.unitbutton=QPushButton("Set Unit")
        self.unitbutton.clicked.connect(self.on_unit_clicked)

        self.side_layout.addWidget(self.abort_button)
        self.side_layout.addWidget(self.abort_prog_button)
        self.side_layout.addWidget(self.quit_prog_button)
        self.side_layout.addWidget(self.wait_label)
        self.side_layout.addWidget(self.wait_edit)
        self.side_layout.addWidget(self.wait_button)
        self.side_layout.addWidget(self.unitlabel)
        self.side_layout.addWidget(self.unitmenu)
        self.side_layout.addWidget(self.unitbutton)

    def create_motion1box(self):
        self.motion1box=QGroupBox("Control Axis 1 (Left/Right)")
        self.motion1layout=QVBoxLayout()
        self.motion1box.setLayout(self.motion1layout)

        self.create_motor1box()
        self.create_pos1box()

        self.motion1layout.addWidget(self.motor1box)
        self.motion1layout.addWidget(self.pos1box)

    def create_motor1box(self):
        self.motor1box=QGroupBox()
        self.motor1layout=QVBoxLayout()
        self.motor1box.setLayout(self.motor1layout)

        self.motor1disp=QLabel()
        self.motor1disp.setAlignment(Qt.AlignCenter)
        self.motor1disp.setFrameShape(QFrame.StyledPanel)

        try:
            self.motor1on=self.newport.is_motor_on(1)
            self.newport.wait_time(wait)
        except:
            self.motor1on=False

        if self.motor1on:
            self.motor1disp.setText("Motor is On")
            self.motor1disp.setStyleSheet('background:limegreen')
        else:
            self.motor1disp.setText("Motor is Off")
            self.motor1disp.setStyleSheet('background:red')

        self.motor1button=QPushButton("Toggle Motor On/Off")
        self.motor1button.clicked.connect(self.toggle_motor1)

        self.motor1layout.addWidget(self.motor1disp)
        self.motor1layout.addWidget(self.motor1button)

    """def create_indef1box(self):
        self.indef1box=QGroupBox()
        self.indef1layout=QGridLayout()
        self.indef1box.setLayout(self.indef1layout)

        self.leftbutton=QPushButton("Move Left")
        self.leftbutton.clicked.connect(self.on_left_clicked)
        self.rightbutton=QPushButton("Move Right")
        self.rightbutton.clicked.connect(self.on_right_clicked)

        self.stop1button=QPushButton("Stop Motion")
        self.stop1button.clicked.connect(lambda: self.newport.stop_motion(1))
        
        self.indef1layout.addWidget(self.leftbutton,0,0)
        self.indef1layout.addWidget(self.rightbutton,0,1)
        self.indef1layout.addWidget(self.stop1button,1,0,1,2)"""

    def create_pos1box(self):
        self.pos1box=QGroupBox()
        self.pos1layout=QGridLayout()
        self.pos1box.setLayout(self.pos1layout)

        self.despos1label=QLabel("Desired Position")
        self.despos1disp=QLCDNumber()
        self.despos1=0
        self.despos1disp.display(self.despos1)

        self.actpos1label=QLabel("Actual Position")
        self.actpos1disp=QLCDNumber()
        try:
            self.actpos1=self.newport.get_act_pos(1)
            self.newport.wait_time(wait)
        except:
            self.actpos1=0
        self.actpos1disp.display(self.actpos1)

        self.abs1edit=QLineEdit()
        self.abs1button=QPushButton("Set Absolute Position")
        self.abs1button.clicked.connect(self.on_abs1_clicked)

        self.rel1edit=QLineEdit()
        self.rel1button=QPushButton("Move (Relative)")
        self.rel1button.clicked.connect(self.on_rel1_clicked)

        self.ll1disp=QLCDNumber()
        self.ll1edit=QLineEdit()
        self.ll1button=QPushButton("Set Left Limit")
        self.ll1button.clicked.connect(self.on_ll1_clicked)
        self.rl1disp=QLCDNumber()
        self.rl1edit=QLineEdit()
        self.rl1button=QPushButton("Set Right Limit")
        self.rl1button.clicked.connect(self.on_rl1_clicked)

        self.pos1layout.addWidget(self.despos1label,0,0)
        self.pos1layout.addWidget(self.despos1disp,1,0)
        self.pos1layout.addWidget(self.actpos1label,0,1)
        self.pos1layout.addWidget(self.actpos1disp,1,1)
        self.pos1layout.addWidget(self.abs1edit,2,0)
        self.pos1layout.addWidget(self.abs1button,3,0)
        self.pos1layout.addWidget(self.rel1edit,2,1)
        self.pos1layout.addWidget(self.rel1button,3,1)
        self.pos1layout.addWidget(self.ll1disp,4,0)
        self.pos1layout.addWidget(self.rl1disp,4,1)
        self.pos1layout.addWidget(self.ll1edit,5,0)
        self.pos1layout.addWidget(self.rl1edit,5,1)
        self.pos1layout.addWidget(self.ll1button,6,0)
        self.pos1layout.addWidget(self.rl1button,6,1)

    def create_motion2box(self):
        self.motion2box=QGroupBox("Control Axis 2 (Up/Down)")
        self.motion2layout=QVBoxLayout()
        self.motion2box.setLayout(self.motion2layout)

        self.create_motor2box()
        self.create_pos2box()

        self.motion2layout.addWidget(self.motor2box)
        self.motion2layout.addWidget(self.pos2box)

    def create_motor2box(self):
        self.motor2box=QGroupBox()
        self.motor2layout=QVBoxLayout()
        self.motor2box.setLayout(self.motor2layout)

        self.motor2disp=QLabel()
        self.motor2disp.setAlignment(Qt.AlignCenter)
        self.motor2disp.setFrameShape(QFrame.StyledPanel)

        try:
            self.motor2on=self.newport.is_motor_on(2)
            self.newport.wait_time(wait)
        except:
            self.motor2on=False

        if self.motor2on:
            self.motor2disp.setText("Motor is On")
            self.motor2disp.setStyleSheet('background:limegreen')
        else:
            self.motor2disp.setText("Motor is Off")
            self.motor2disp.setStyleSheet('background:red')

        self.motor2button=QPushButton("Toggle Motor On/Off")
        self.motor2button.clicked.connect(self.toggle_motor2)

        self.motor2layout.addWidget(self.motor2disp)
        self.motor2layout.addWidget(self.motor2button)

        """
    def create_indef2box(self):
        self.indef2box=QGroupBox()
        self.indef2layout=QGridLayout()
        self.indef2box.setLayout(self.indef2layout)

        self.downbutton=QPushButton("Move Down")
        self.downbutton.clicked.connect(self.on_down_clicked)
        self.upbutton=QPushButton("Move Up")
        self.upbutton.clicked.connect(self.on_up_clicked)

        self.stop2button=QPushButton("Stop Motion")
        self.stop2button.clicked.connect(lambda: self.newport.stop_motion(2))

        self.indef2layout.addWidget(self.downbutton,0,0)
        self.indef2layout.addWidget(self.upbutton,0,1)
        self.indef2layout.addWidget(self.stop2button,1,0,1,2)"""

    def create_pos2box(self):
        self.pos2box=QGroupBox()
        self.pos2layout=QGridLayout()
        self.pos2box.setLayout(self.pos2layout)

        self.despos2label=QLabel("Desired Position")
        self.despos2disp=QLCDNumber()
        self.despos2=0
        self.despos2disp.display(self.despos2)

        self.actpos2label=QLabel("Actual Position")
        self.actpos2disp=QLCDNumber()
        try:
            self.actpos2=self.newport.get_act_pos(2)
            self.newport.wait_time(wait)
        except:
            self.actpos2=0
        self.actpos2disp.display(self.actpos2)

        self.abs2edit=QLineEdit()
        self.abs2button=QPushButton("Set Absolute Position")
        self.abs2button.clicked.connect(self.on_abs2_clicked)

        self.rel2edit=QLineEdit()
        self.rel2button=QPushButton("Move (Relative)")
        self.rel2button.clicked.connect(self.on_rel2_clicked)

        self.ll2disp=QLCDNumber()
        self.ll2edit=QLineEdit()
        self.ll2button=QPushButton("Set Lower Limit")
        self.ll2button.clicked.connect(self.on_ll2_clicked)
        self.rl2disp=QLCDNumber()
        self.rl2edit=QLineEdit()
        self.rl2button=QPushButton("Set Upper Limit")
        self.rl2button.clicked.connect(self.on_rl2_clicked)

        self.pos2layout.addWidget(self.despos2label,0,0)
        self.pos2layout.addWidget(self.despos2disp,1,0)
        self.pos2layout.addWidget(self.actpos2label,0,1)
        self.pos2layout.addWidget(self.actpos2disp,1,1)
        self.pos2layout.addWidget(self.abs2edit,2,0)
        self.pos2layout.addWidget(self.abs2button,3,0)
        self.pos2layout.addWidget(self.rel2edit,2,1)
        self.pos2layout.addWidget(self.rel2button,3,1)
        self.pos2layout.addWidget(self.ll2disp,4,0)
        self.pos2layout.addWidget(self.rl2disp,4,1)
        self.pos2layout.addWidget(self.ll2edit,5,0)
        self.pos2layout.addWidget(self.rl2edit,5,1)
        self.pos2layout.addWidget(self.ll2button,6,0)
        self.pos2layout.addWidget(self.rl2button,6,1)


    def check_motor1(self):
        try:
            self.motor1on=self.newport.is_motor_on(1)
            self.newport.wait_time(wait)
            if self.motor1on:
                self.motor1disp.setText("Motor is On")
                self.motor1disp.setStyleSheet('background:limegreen')
            else:
                self.motor1disp.setText("Motor is Off")
                self.motor1disp.setStyleSheet('background:red')
        except:
            pass

    def check_pos1(self):
        try:
            self.actpos1=self.newport.get_act_pos(1)
            self.actpos1disp.display(self.actpos1)
            self.newport.wait_time(wait)
        except:
            pass

    def check_motor2(self):
        try:
            self.motor2on=self.newport.is_motor_on(2)
            self.newport.wait_time(wait)
            if self.motor2on:
                self.motor2disp.setText("Motor is On")
                self.motor2disp.setStyleSheet('background:limegreen')
            else:
                self.motor2disp.setText("Motor is Off")
                self.motor2disp.setStyleSheet('background:red')
        except:
            pass

    def check_pos2(self):
        try:
            self.actpos2=self.newport.get_act_pos(2)
            self.actpos2disp.display(self.actpos2)
            self.newport.wait_time(wait)
        except:
            pass

    def on_abort_clicked(self):
        # some sort of alert/check?
        self.newport.abort_motion()
        self.newport.wait_time(wait)

    def on_wait_clicked(self):
        try:
            w=self.wait_edit.text()
            self.newport.wait_time(w)
        except:
            pass

    def toggle_motor1(self):
        try:
            if self.newport.is_motor_on(1):
                self.newport.wait_time(wait)
                self.newport.motor_off(1)
                self.motor1disp.setText("Motor is Off")
                self.motor1disp.setStyleSheet('background:red')
            else: 
                self.newport.wait_time(wait)
                self.newport.motor_on(1)
                self.motor1disp.setText("Motor is On")
                self.motor1disp.setStyleSheet('background:limegreen')
            self.newport.wait_time(wait)
        except:
            pass

    def on_unit_clicked(self):
        try:
            unit=self.unitmenu.currentText()
            if unit[0]=="\u03BC":
                unit=unit.replace("\u03BC","u")
            self.newport.set_units(1,unit)
            self.newport.set_units(2,unit)
        except:
            pass

    def toggle_motor2(self):
        try:
            if self.newport.is_motor_on(2):
                self.newport.wait_time(wait)
                self.newport.motor_off(2)
                self.motor2disp.setText("Motor is Off")
                self.motor2disp.setStyleSheet('background:red')
            else:
                self.newport.wait_time(wait)
                self.newport.motor_on(2)
                self.motor2disp.setText("Motor is On")
                self.motor2disp.setStyleSheet('background:limegreen')
            self.newport.wait_time(wait)
        except:
            pass

    def on_left_clicked(self):
        try:
            self.newport.move_rel_pos(1,-1)
        except:
            pass

    def on_right_clicked(self):
        try:
            self.newport.move_indef_pos(1)
        except:
            pass

    def on_down_clicked(self):
        try:
            self.newport.move_indef_neg(2)
        except:
            pass

    def on_up_clicked(self):
        try:
            self.newport.move_indef_pos(2)
        except:
            pass

    def on_abs1_clicked(self):
        pos=float(self.abs1edit.text())
        if pos>self.llim1 and pos<self.rlim1:
            try:
                self.newport.move_abs_pos(1,pos)
                self.newport.wait_time(wait)
                self.despos1=pos
                self.despos1disp.display(self.despos1)
            except:
                pass
            
    def on_rel1_clicked(self):
        try:
            disp=float(self.rel1edit.text())
            pos=self.newport.get_abs_pos(1)
            self.newport.wait_time(wait)
            if pos+disp>self.llim1 and pos+disp<self.rlim1:
                self.newport.move_rel_pos(1,disp)
                self.newport.wait_time(wait)
                self.despos1=pos+disp
                self.despos1disp.display(self.despos1)
        except:
            pass

    def on_ll1_clicked(self):
        self.llim1=float(self.ll1edit.text())
        self.ll1disp.display(self.llim1)

    def on_rl1_clicked(self):
        self.rlim1=float(self.rl1edit.text())
        self.rl1disp.display(self.rlim1)

    def on_abs2_clicked(self):
        pos=float(self.abs2edit.text())
        if pos>self.llim2 and pos<self.rlim2:
            try:
                self.newport.move_abs_pos(2,pos)
                self.newport.wait_time(wait)
                self.despos2=pos
                self.despos2disp.display(self.despos2)
            except:
                pass

    def on_rel2_clicked(self):
        try:
            disp=float(self.rel2edit.text())
            pos=self.newport.get_abs_pos(2)
            self.newport.wait_time(wait)
            if pos+disp>self.llim2 and pos+disp<self.rlim2:
                self.newport.move_rel_pos(2,disp)
                self.newport.wait_time(wait)
                self.despos2=pos+disp
                self.despos2disp.display(self.despos2)
        except:
            pass

    def on_ll2_clicked(self):
        self.llim2=float(self.ll2edit.text())
        self.ll2disp.display(self.llim2)

    def on_rl2_clicked(self):
        self.rlim2=float(self.rl2edit.text())
        self.rl2disp.display(self.rlim2)


if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyle('Fusion')
    wg=WidgetGallery()
    wg.show()
    sys.exit(app.exec_())

