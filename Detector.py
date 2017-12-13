from __future__ import unicode_literals
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.pyplot import psd
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import sys
import rtlsdr
import peakutils
matplotlib.use('Qt5Agg')

coordinate = 0
port = rtlsdr.RtlSdr()
sr = 2.4                                     # sample rate in maga Hz
port.sample_rate = sr * 10**6
cf = 1                                       # central freq in mega Hz
k = cf
port.center_freq = cf * 10 ** 6
freq_cor = 1000                             # frequency correction
port.freq_correction = freq_cor
port.gain = 'auto'
num = 5      # 2**num work as overlapping constant

start = 0	 # Zooming constant
end = 6
div = 1024/6


class MyMplCanvas(FigureCanvas):         # made a canvas

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        global fig
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyDynamicMplCanvas(MyMplCanvas):                # canvas for graph

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)                    # timer for dynamic graph
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        data = port.read_samples(1024 * 2 ** num)

    def update_figure(self):                            # dynamic graph
        data = port.read_samples(1024 * 2 ** num)
        y, x = matplotlib.pyplot.psd(data, NFFT=1024, Fs=sr, Fc=k)               # psd of incoming data
        self.axes.cla()
        self.axes.set_xlabel('Central Frequency = '+str('%.3f' % k)+' MHz')
        self.axes.set_ylabel('Power  Spectrum Value')
        self.axes.plot(x[int(start*div):int(end*div)], y[int(start*div):int(end*div)], 'r')        # plot the data
        ind = peakutils.indexes(y[int(start*div):int(end*div)], thres=0.5, min_dist=30)       # find the peak
        xx = []
        yy = []
        x1 = x[int(start*div):int(end*div)]
        y1 = y[int(start*div):int(end*div)]
        for aa in ind:               # for peak
            xx.append(x1[aa])
            yy.append(y1[aa])
        self.axes.plot(xx, yy, '*')  # plot a pick

        def onclick(event):
            global ty
            ty = event.xdata
        self.draw()

        def on_move(event):
            x, y = event.x, event.y     # get the x and y pixel coords

            if event.inaxes:
                ax = event.inaxes       # the axes instance
                global xd
                global yd
                global coordinate
                xd = event.xdata
                yd = event.ydata
                coordinate = 'x = ' + str(xd) + '  : y = ' + str(yd)


        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        binding_id = fig.canvas.mpl_connect('motion_notify_event', on_move)
        self.draw()


class ApplicationWindow(QtWidgets.QMainWindow):                 # main gui window
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.changePosition)
        self.timer.start(1)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("RADIO ASTRONOMY PROJECT")

        self.file_menu = QtWidgets.QMenu('&File', self)         # make a menu bar
        self.file_menu.addAction('&Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.viewMenu = QtWidgets.QMenu('&View', self)
        viewStatAct = QAction('Zoom', self, checkable=True)
        viewStatAct.setStatusTip('Zoom')
        viewStatAct.setChecked(False)
        viewStatAct.triggered.connect(self.ckbox)
        self.viewMenu.addAction(viewStatAct)
        self.menuBar().addMenu(self.viewMenu)

        self.editmenu = QtWidgets.QMenu('&Edit', self)
        self.menuBar().addMenu(self.editmenu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&Zoom', self.infozoom)
        self.help_menu.addAction('&About', self.about)

        cent_freq = QLabel('Central Frequency')          # input for center frequency
        self.cent_freqEdit = QLineEdit()
        ebtn = QPushButton('Enter', self)
        ebtn.clicked.connect(self.clickMethod)

        self.slbl = QLabel('start')
        self.zstart = QLineEdit()
        self.elbl = QLabel('End')
        self.zend = QLineEdit()
        self.zbtn = QPushButton('Zoom')
        self.zbtn.clicked.connect(self.zoomr)
        self.reset = QPushButton('Reset')
        self.reset.clicked.connect(self.resetr)

        sld = QSlider(Qt.Horizontal, self)           # slider for change the value
        sld.setGeometry(10, 650, 1500, 30)
        sld.valueChanged.connect(self.scroll)
        self.pos = QLabel('Position')
        self.shortcut = QShortcut(QKeySequence("Enter"), self)
        self.shortcut.activated.connect(self.on_open)

        self.main_widget = QtWidgets.QWidget(self)

        self.main_Vlayout = QtWidgets.QVBoxLayout(self.main_widget)  # put widget
        sub1_Hlayout = QtWidgets.QHBoxLayout(self.main_widget)
        sub1_Hlayout.addWidget(self.cent_freqEdit)
        sub1_Hlayout.addWidget(ebtn)

        self.sub2_Hlayout = QtWidgets.QHBoxLayout(self.main_widget)
        self.sub2_Hlayout.addWidget(self.slbl)
        self.sub2_Hlayout.addWidget(self.zstart)
        self.sub2_Hlayout.addWidget(self.elbl)
        self.sub2_Hlayout.addWidget(self.zend)
        self.sub2_Hlayout.addWidget(self.zbtn)
        self.sub2_Hlayout.addWidget(self.reset)
        self.slbl.hide()
        self.zstart.hide()
        self.elbl.hide()
        self.zend.hide()
        self.reset.hide()
        self.zbtn.hide()

        dc = MyDynamicMplCanvas(self.main_widget, width=5, height=3, dpi=100)

        self.main_Vlayout.addWidget(cent_freq)
        self.main_Vlayout.addLayout(sub1_Hlayout)
        self.main_Vlayout.addWidget(sld)
        self.main_Vlayout.addLayout(self.sub2_Hlayout)
        self.main_Vlayout.addWidget(dc)
        self.main_Vlayout.addWidget(self.pos)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def ckbox(self, state):
        if state:
            self.slbl.show()
            self.zstart.show()
            self.elbl.show()
            self.zend.show()
            self.reset.show()
            self.zbtn.show()
        else:
            self.slbl.hide()
            self.zstart.hide()
            self.elbl.hide()
            self.zend.hide()
            self.reset.hide()
            self.zbtn.hide()


    def scroll(self, value):
        global k
        global h
        try:                                           # exception catcher and remover block
            global c
            c = h
        except NameError:
            h = 0
        else:
            port.center_freq = (0.1*value + h) * 10 ** 6
            k = value + h
        finally:
            port.center_freq = (0.1*value + h) * 10 ** 6
            k = 0.1*value + h

    def clickMethod(self):
        global h
        global cf
        global k
        try:                                           # exception catcher and remover block
            cc = float(self.cent_freqEdit.text())                            # for press enter with null value
        except ValueError:
            cc = 0
        else:
            cc = float(self.cent_freqEdit.text())
        finally:
            h = cc
        cf = h
        k = cf

    def zoomr(self):
        global end
        global start

        end = float(self.zend.text())
        start = float(self.zstart.text())

    def resetr(self):
        global end
        global start
        start = 0
        end = 10

    def on_open(self):
        global h
        global cf
        global k
        try:                                          # exception catcher and remover block
            cc = float(self.cent_freqEdit.text())                   # for press enter with null value
        except ValueError:
            cc = 0
        else:
            cc = float(self.cent_freqEdit.text())
        finally:
            h = cc

        cf = h
        k = cf

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About", """     Welcome to Simple Rtl-Sdr Software Made by <u><b>Mehul Sutariya</b></u> <br>
                                                        For <i>Radio Astronomy Project</i> for<br> 
                                                        <b>Sardar Vallabhbhai National Institute of Technology</b>,Surat <br>
                                                        <b><i> Aim:Detection of 21cm Hydrogen Line</i></b>
                                                        <br>Made in Python With RtlSdr,MatPlotLib,PeakUtils and PyQt5""")

    def infozoom(self):
        QtWidgets.QMessageBox.about(self, "About",""" Divide X-Axes into total 6 Part Which start From 0
        (X-axes has total 6 part) and than Enter 
        The Start and End value and press Zoom button
          for REMOVE zoom press RESET""")
    def changePosition(self):
        self.pos.setText(str(coordinate))


qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle('Radio Astronomy Project')
aw.show()
sys.exit(qApp.exec_())
