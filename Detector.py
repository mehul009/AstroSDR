from __future__ import unicode_literals
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import sys
import rtlsdr
import peakutils
import pandas as pd
import time
import os

port = rtlsdr.RtlSdr()              # configuration of devise
sr = 2.4                                     # sample rate in mega Hz
port.sample_rate = sr * 10**6
cf = 1                                       # central freq in mega Hz
k = cf
port.center_freq = cf * 10 ** 6
freq_cor = 1000                             # frequency correction
port.freq_correction = freq_cor
port.gain = 'auto'

num = 5      # 2**num work as overlapping constant

data = port.read_samples(1024 * 2 ** num)   # data

start = 0	 # Zooming constant
end = 6
div = 1024/6

coordinate = 0   # coordinate constant

save = 'no'  # save constant


class MyMplCanvas(FigureCanvas):         # made a canvas

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        global fig
        fig = Figure(figsize=(width, height), dpi=dpi)       # make figure
        self.axes = fig.add_subplot(111)                      # subplot in this figure

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyDynamicMplCanvas(MyMplCanvas):                # canvas for graph

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QTimer(self)                    # timer for dynamic graph
        timer.timeout.connect(self.update_figure)
        timer.start(200)

    def compute_initial_figure(self):
        data = port.read_samples(1024 * 2 ** num)

    def update_figure(self):   # dynamic graph
        global data
        data = port.read_samples(1024 * 2 ** num)
        global x
        global y
        y, x = plt.psd(data, NFFT=1024, Fs=sr, Fc=k)               # psd of incoming data
        self.axes.cla()
        self.axes.set_xlabel('Central Frequency = ' + str('%.3f' % k) + ' MHz')
        self.axes.set_ylabel('Power  Spectrum Value')
        self.axes.plot(x[int(start*div):int(end*div)], y[int(start*div):int(end*div)], 'r')        # plot the data
        ind = peakutils.indexes(y[int(start*div):int(end*div)], thres=0.5, min_dist=30)       # find the peak
        global xx
        global yy
        xx = []
        yy = []
        x1 = x[int(start*div):int(end*div)]
        y1 = y[int(start*div):int(end*div)]
        for aa in ind:               # for peak
            xx.append(x1[aa])
            yy.append(y1[aa])
        self.axes.plot(xx, yy, '*')  # plot a pick

        if save == 'yes':
            year, month, day, hour, min, sec, wday, yday, isdst = time.localtime()  # time for save file

        # if not exist than make directory path for save file
            if not os.path.exists(
                'astronomy/' + 'year ' + str(year) + '/' + 'month ' + str(month) + '/' + 'day '
                                           + str(day) + '/' + 'hour ' + str(hour) + '/'):
                os.makedirs('astronomy/' + 'year ' + str(year) + '/' + 'month ' + str(month) + '/'
                            + 'day ' + str(day) + '/' + 'hour ' + str(hour) + '/')

            raws = pd.Series(data)  # make a series
            ssr = pd.Series([sr])
            scf = pd.Series([k])
            ssam = pd.Series([1024 * 2 ** num])
            second = pd.Series([sec])

        # make a frame
            frame = {'data': raws, 'samplerate': ssr, 'centralfreq': scf, 'sample': ssam, 'second': second}
            data_frame = pd.DataFrame(frame)  # make data frame

        # save file in h5 formate for highspeed and high compression
            data_frame.to_hdf('astronomy/' + 'year ' + str(year) + '/' + 'month ' + str(month) + '/' +
                              'day ' + str(day) + '/' + 'hour ' + str(hour) + '/' + 'minute ' + str(min) + '.h5',
                              key='int', mode='a', formate='table(t)', append=True, complevel=1, fletcher32=True)


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


class ApplicationWindow(QMainWindow):                 # main gui window
    def __init__(self):
        QMainWindow.__init__(self)
        if os.path.isfile('logo.png'):
            self.setWindowIcon(QIcon('logo.png'))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.changePosition)
        self.timer.start(1)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("RADIO ASTRONOMY PROJECT")

        self.file_menu = QMenu('&File', self)         # make a menu bar
        self.file_menu.addAction('&Screen Shot', self.savefig, Qt.CTRL + Qt.Key_S)
        savedt = QAction('Save Data', self, checkable=True)
        savedt.setStatusTip('Save Data')
        savedt.setChecked(False)
        savedt.triggered.connect(self.savedata)
        self.file_menu.addAction(savedt)
        self.file_menu.addAction('&Quit', self.fileQuit, Qt.CTRL + Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.viewMenu = QMenu('&View', self)
        viewStatAct = QAction('Zoom', self, checkable=True)
        viewStatAct.setStatusTip('Zoom')
        viewStatAct.setChecked(False)
        viewStatAct.triggered.connect(self.ckbox)
        self.viewMenu.addAction(viewStatAct)
        self.menuBar().addMenu(self.viewMenu)

        self.editmenu = QMenu('&Edit', self)
        self.editmenu.addAction('&Sample Rate', self.ChangeSampleRate)
        self.editmenu.addAction('&Over Lap', self.OverLap)
        self.menuBar().addMenu(self.editmenu)

        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&Zoom', self.infozoom)
        self.help_menu.addAction('&Overlap', self.infoOverLap)
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

        self.shortcut = QShortcut(QKeySequence("Enter"), self)      # connect enter btn to input tab
        self.shortcut.activated.connect(self.on_open)

        self.main_widget = QWidget(self)

        self.main_Vlayout = QVBoxLayout(self.main_widget)  # put widget
        sub1_Hlayout = QHBoxLayout(self.main_widget)
        sub1_Hlayout.addWidget(self.cent_freqEdit)
        sub1_Hlayout.addWidget(ebtn)

        self.sub2_Hlayout = QHBoxLayout(self.main_widget)
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

    def savedata(self, state):
        global save
        if state:
            save = 'yes'
        else:
            save = 'no'

    def savefig(self):
        plt.figure(1)
        plt.cla()
        plt.xlabel('Central Frequency = '+str('%.3f' % k)+' MHz')
        plt.ylabel('Power Spectrum Value')
        plt.plot(x[int(start*div):int(end*div)], y[int(start*div):int(end*div)], 'r')
        xt, zz = plt.xticks()
        yt, zz = plt.yticks()
        plt.plot(xx, yy, '*')
        ln = len(xx)
        sf = 0
        txt = 'peak X:Y'
        while sf < ln:
            xx1 = xx[sf]
            yy1 = yy[sf]
            ax = str('%.2f' % xx1) + ' : ' + str('%.5f' % yy1)
            txt = txt + '\n' + str(ax)
            sf = sf+1
        plt.text(xt[-3], yt[-3], txt, fontsize=8)
        plt.savefig('psd of central frequency "' + str(k) + '" MHz.svg')
        plt.close()

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def ChangeSampleRate(self):               # for change in sample rate
        i, okPressed = QInputDialog.getDouble(self, "Select Sample Rate", "Sample Rate:", 2.4)
        if okPressed:
            global sr
            sr = i
            port.sample_rate = sr * 10 ** 6

    def OverLap(self):                     # for change in over lapping constant
        j, okPressed = QInputDialog.getDouble(self, "Select Over Lap", "Select Number :", 5)
        if okPressed:
            global num
            num = j

    def about(self):                     # information of software
        QMessageBox.about(self, "About", """     Welcome to Simple Rtl-Sdr Software Made by <u><b>Mehul Sutariya</b></u> <br>
                                                        For <i>Radio Astronomy Project</i> for<br> 
                                                        <b>Sardar Vallabhbhai National Institute of Technology</b>,Surat <br>
                                                        <b><i> Aim:Detection of 21cm Hydrogen Line</i></b>
                                                        <br>Made in Python With RtlSdr,MatPlotLib,PeakUtils and PyQt5<br>
                                                        Thanks to Ankit Virani""")

    def infozoom(self):           # information of Zoom
        QMessageBox.about(self, "Zoom", """ Divide X-Axes into total 6 Part Which start From 0
        (X-axes has total 6 part) and than Enter 
        The Start and End value and press Zoom button
          for REMOVE zoom press RESET""")

    def infoOverLap(self):                    # information of the overlap
        QMessageBox.about(self, "Over Lap", """ Total Over Lapping in 2 Power Selected_Number 
        i.e : Selected_Number = 5 Then OverLapping is 32 Time """)

    def changePosition(self):                    # show coordinate
        self.pos.setText(str(coordinate))


qApp = QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle('Radio Astronomy Project')
aw.show()
sys.exit(qApp.exec_())
