# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'iface analyser.ui'
#
# Created: Tue Apr  5 19:54:20 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

ATTENDANCE_TERMINALS = 10
ACCESS_TERMINALS = 4
DATA_LIST = [['None','None','None','None','None','None','None','None','None','None']]
COMMAND_LIST = []
TERMINAL_LIST=[]
COUNT_COMMANDS = 1

import time
import functions as f
from PyQt4 import QtCore,QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from datetime import datetime
import time

import sys,os
import sqlconns
import gl


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow,self).__init__()
        self.setupUi(self)
        self.timer  = QtCore.QTimer(self)
        self.timer.setInterval(1000)          # Throw event timeout with an interval of 1000 milliseconds
        #self.start()
        self.timer.timeout.connect(self.refreshTable)
        self.DataCollector = TerminalX(self)
        self.DataCollector.start()
        #self.refreshTable()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        self.setWindowIcon(QtGui.QIcon('python_small.ico'))
        MainWindow.resize(1000, 650)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 955, 600))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(10)
        self.tableItem= QTableWidgetItem()
        self.refreshTable()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 850, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionExit.setShortcut("Ctrl+Q")
        self.actionExit.triggered.connect(self.close_application)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "iface analyser", None))
        self.menuFile.setTitle(_translate("MainWindow", "&File", None))
        self.actionExit.setText(_translate("MainWindow", "&Quit",None))

    def close_application(self):
        global COUNT_COMMANDS
        COUNT_COMMANDS = 0
        self.DataCollector.terminate()
        sys.exit()

    def closeEvent(self, event):
        global COUNT_COMMANDS
        COUNT_COMMANDS = 0
        self.DataCollector.terminate()
        sys.exit()

    @QtCore.pyqtSlot()
    def refreshTable(self):
        global DATA_LIST
        self.tableWidget.verticalHeader().setVisible(False)

        self.tableWidget.setHorizontalHeaderLabels(['  id  ','  Description                                                    ','  Number  ','                   SN                   ',  ' Poll Success  ','  Unsent  ','  In Transit  ','  Complete  ',' Att Stamp ',' Op Stamp '])
        for n in range(10):
            self.tableWidget.horizontalHeaderItem(n).setTextAlignment(Qt.AlignLeft)
        self.tableWidget.setRowCount(len(DATA_LIST))
        for n in range(len(DATA_LIST)):
            for y in range(5):
                if DATA_LIST[n][y] == None:
                    field = "None"
                else:
                    if y == 4:
                        field = f.get_sql_date(DATA_LIST[n][y],"dd/mm/yyyy hh:mm:ss")
                    else:
                        field = str(DATA_LIST[n][y])
                self.tableWidget.setItem(n,y, QTableWidgetItem(field))
        stylesheet = "QHeaderView::section{Background-color:rgb(117,146,156);\
                               border-radius:40px;}"
        self.tableWidget.setStyleSheet(stylesheet)
        self.tableWidget.resizeColumnsToContents()

        self.show_ids()

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def show_ids(self):
        sent = 0
        complete = 0
        for n in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(n,0)
            for y in range(len(TERMINAL_LIST)):
                if str(item.text()) == TERMINAL_LIST[y][0]:
                    field = str(TERMINAL_LIST[y][1])
                    self.tableWidget.setItem(n,5, QTableWidgetItem(field))
                    field = str(TERMINAL_LIST[y][2])
                    self.tableWidget.setItem(n,6, QTableWidgetItem(field))
                    field = str(TERMINAL_LIST[y][3])
                    self.tableWidget.setItem(n,7, QTableWidgetItem(field))
                    field = str(TERMINAL_LIST[y][4])
                    self.tableWidget.setItem(n,4, QTableWidgetItem(field))
                    field = str(TERMINAL_LIST[y][5])
                    self.tableWidget.setItem(n,8, QTableWidgetItem(field))
                    field = str(TERMINAL_LIST[y][6])
                    self.tableWidget.setItem(n,9, QTableWidgetItem(field))
            for y in range(10):
                #white = '248,248,255'
                #orange = '255,179,71'
                #yellow = '253,253,150'
                #green = '137,232,148'
                try:
                    item1 = self.tableWidget.item(n,5).text()
                    sent = int(item1)
                except:
                    sent = 0
                try:
                    complete = int(self.tableWidget.item(n,7).text())
                except:
                    complete = 0
                if self.tableWidget.item(n,4).text() != "None":
                    if validate_poll_success(self.tableWidget.item(n,4).text()) == False:
                        self.tableWidget.item(n, y).setBackground(QtGui.QColor(255,0,0))
                    else:
                        if sent > 0 and complete > 0: self.tableWidget.item(n, y).setBackground(QtGui.QColor(253,253,150))
                        if sent == 0 and complete > 0: self.tableWidget.item(n, y).setBackground(QtGui.QColor(137,232,148))
                        if sent > 0 and complete == 0: self.tableWidget.item(n, y).setBackground(QtGui.QColor(255,179,71))

class TerminalX(QtCore.QThread):
    def __init__(self,parent=None):
        QtCore.QThread.__init__(self,parent)
        self.test=''

    def run(self):
        x = ''
        while COUNT_COMMANDS == 1:
            get_command_info()
            time.sleep(10)

def validate_poll_success(tm):
    #if poll success more than 1 hour ago highlight
    if tm == 'None': return False
    dte = datetime.strptime(tm, "%d/%m/%Y %H:%M:%S")
    d1_ts = time.mktime(dte.timetuple())
    d2_ts = time.mktime(datetime.now().timetuple())
    if (int(d2_ts-d1_ts) / 60) > 60:
        return False
    else:
        return True


def get_terminal_details():
    global DATA_LIST
    global TERMINAL_LIST
    tx = "SELECT terminal_id, description, number, ip_address,poll_success FROM tterminal WHERE configuration in ("+str(ATTENDANCE_TERMINALS)+","+str(ACCESS_TERMINALS)+") AND number < 1000 and ip_address not like '%.%' ORDER BY number"
    ret = sqlconns.sql_select_into_list(tx)
    if ret==-1:
        DATA_LIST = [['None','None','None','None','None','None','None','None','None','None']]
    else:
        DATA_LIST = ret
        TERMINAL_LIST = []
        for n in range(len(DATA_LIST)):
            TERMINAL_LIST.append([(str(DATA_LIST[n][0])),"0","0","0","None","None","None"])


def database_connections():
    if os.path.isfile(gl.SCRIPT_ROOT + 'database.ini'):
        if sqlconns.readsql_connection_timeware_main_6() == 0:
            showdialog()
            return -1
        elif sqlconns.readsql_connection_timeware_main_6() == 1:
            test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
            if test_comms == 0:
                showdialog('Error connecting to database!!!!')
                return -1
            else: return
    else:
        showdialog()
        return -1

def showdialog(warning):
    a = QApplication(sys.argv)
    w = QWidget()

    w.setWindowIcon(QIcon("python_small.ico"))
    result = QMessageBox.warning(w, 'Iface Analyser Error', warning, QMessageBox.Ok)
    if result == QMessageBox.Ok:
        sys.exit(a.exit())
    w.show()

    sys.exit(a.exec_())

def set_env():
    global ATTENDANCE_TERMINALS
    global ACCESS_TERMINALS
    path = str.replace(gl.SCRIPT_ROOT,'iface analyser.exe','')
    if os.path.isfile(path + 'database.ini'):
        if sqlconns.readsql_connection_timeware_main_6() == 0:
            showdialog('Error connecting to database!!!! ' + path)
            return False
        elif sqlconns.readsql_connection_timeware_main_6() == 1:
            test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
            if test_comms == 0:
                    showdialog('Error connecting to database!!!! ' + path)
            else:
                if os.path.isfile(gl.GENERAL_INI):
                    fob=open(gl.GENERAL_INI, "r")
                    listme = fob.readlines()
                    fob.close()
                else:
                    showdialog('Error reading general.ini file!!!!')
                    return False
                try:
                    for index in range(len(listme)):
                        if "'" in listme[index]: continue
                        if "access_terminal" in listme[index]:
                            ACCESS_TERMINALS = int(listme[index].split("=")[1])
                        if "attendance_terminal" in listme[index]:
                            ATTENDANCE_TERMINALS = int(listme[index].split("=")[1])
                except Exception as e:
                    return False
                return True
    else:
        showdialog('Error connecting to database!!!! ' + path)
        return False

def get_command_info():
    global TERMINAL_LIST
    for n in range(len(TERMINAL_LIST)):
        tx = "SELECT COUNT(*) AS FOO FROM d_iface_commands WHERE sent <> 1 AND terminal_id=" + str(TERMINAL_LIST[n][0])
        the_sum = sqlconns.sql_select_single_field(tx)
        if the_sum==-1: continue
        TERMINAL_LIST[n][1] = str(the_sum)
        tx = "SELECT COUNT(*) AS FOO FROM d_iface_commands WHERE sent = 1 AND completed_flag <> 1 and terminal_id=" + str(TERMINAL_LIST[n][0])
        the_sum = sqlconns.sql_select_single_field(tx)
        if the_sum==-1: continue
        TERMINAL_LIST[n][2] = str(the_sum)
        tx = "SELECT COUNT(*) AS FOO FROM d_iface_commands WHERE completed_flag = 1 AND terminal_id=" + str(TERMINAL_LIST[n][0])
        the_sum = sqlconns.sql_select_single_field(tx)
        if the_sum==-1: continue
        TERMINAL_LIST[n][3] = str(the_sum)
        tx = "SELECT poll_success FROM tterminal WHERE terminal_id=" + str(TERMINAL_LIST[n][0])
        the_sum = sqlconns.sql_select_into_list(tx)
        if the_sum==-1: continue
        if the_sum[0][0] == None:
            the_sum = "None"
        elif the_sum[0][0] != None:
            the_sum = str.replace(f.get_sql_date(the_sum[0][0],"dd/mm/yyyy hh:mm:ss"),"'","")
        TERMINAL_LIST[n][4] = str(the_sum)
        tx = "SELECT TOP 1 stamp FROM d_iface_stamps WHERE table_name like 'att_stamp' and terminal_id = " + str(TERMINAL_LIST[n][0])
        listy = sqlconns.sql_select(tx)
        if listy==-1: continue
        if len(listy) == 0:
            att = 'None'
        elif listy[0][0] == None:
            att = "None"
        else:
            att = str(listy[0][0])
        tx = "SELECT TOP 1 stamp FROM d_iface_stamps WHERE table_name like 'op_stamp' and terminal_id = " + str(TERMINAL_LIST[n][0])

        listy = sqlconns.sql_select(tx)

        if listy==-1: continue
        if len(listy) == 0:
            op = 'None'
        elif listy[0][0] == None:
            op = "None"
        else:
            op = str(listy[0][0])
        TERMINAL_LIST[n][5] = att
        TERMINAL_LIST[n][6] = op

if __name__ == '__main__':
    if set_env() == True:
        get_terminal_details()
        jobs = []
        app=QtGui.QApplication(sys.argv)
        ex = Ui_MainWindow()
        ex.show()
        ex.start()
        sys.exit(app.exec())

