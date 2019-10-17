# -*- coding: utf-8 -*-
#single columnt, 12 bookings

# Form implementation generated from reading ui file 'iface analyser.ui'
#
# Created: Tue Apr  5 19:54:20 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

APPNAME = "ADP"

'this is 10 seconds'
ADP_REFRESH = 10000

#screen defaults
#Orig 1500,900
SCREEN_SIZE_X=1500
SCREEN_SIZE_Y=1500

#grid defaults
#orig 10, 10, 1500, 900
GRID_POS_X=10
GRID_POS_Y=10
GRID_SIZE_X=1500
GRID_SIZE_Y=900

#COUNT_COMMANDS = 1
SQL_TOP = ""
EMPLOYEE_SQL = ""

#default colours
IN_RED=255
IN_GREEN=179
IN_BLUE=71
OUT_RED=137
OUT_GREEN=232
OUT_BLUE=148

import functions as f
from PyQt4 import QtCore,QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from datetime import datetime
import sip
import time
import gc

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


        self.COUNT_COMMANDS = 1

        super(Ui_MainWindow,self).__init__()
        self.setupUi(self)
        #self.timer  = QtCore.QTimer(self)

        #self.timer.start(100)

        #self.timer.timeout.connect(self.refreshTable)

        self.timer = QtCore.QTimer.singleShot(ADP_REFRESH, self.refreshTable)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        self.setWindowIcon(QtGui.QIcon('python_small.ico'))
        MainWindow.resize(SCREEN_SIZE_X, SCREEN_SIZE_Y)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(GRID_POS_X, GRID_POS_Y, GRID_SIZE_X, GRID_SIZE_Y))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(15)
        self.tableItem= QTableWidgetItem()
        #self.refreshTable()
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
        MainWindow.setWindowTitle(_translate("MainWindow", "Attendance Panel", None))
        self.menuFile.setTitle(_translate("MainWindow", "&File", None))
        self.actionExit.setText(_translate("MainWindow", "&Quit",None))

    def close_application(self):
        #global COUNT_COMMANDS
        self.COUNT_COMMANDS = 0
        #self.DataCollector.terminate()
        sip.setdestroyonexit(False)
        sys.exit()

    def closeEvent(self, event):
        #global COUNT_COMMANDS
        self.COUNT_COMMANDS = 0
        #self.DataCollector.terminate()
        sip.setdestroyonexit(False)
        sys.exit()

    #@QtCore.pyqtSlot()
    def refreshTable(self):
        #global DATA_LIST
        DATA_LIST = ['None', 'None', '0', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']


#        DATA_LIST = self.get_employee_details()
#**********************************************************
        tx = "SELECT "
        if SQL_TOP != '': tx += SQL_TOP + ' '
        tx += "last_name, first_name, employee_id from temployee "
        tx += EMPLOYEE_SQL
        ret = sqlconns.sql_select_into_list(tx)
        if ret == -1:
            DATA_LIST = ['None', 'None', '0', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
        else:
            DATA_LIST = [x for x in ret]
            for n in range(len(DATA_LIST)):
                DATA_LIST[n] = DATA_LIST[n] = [x for x in DATA_LIST[n]]
                for y in range(12):
                    DATA_LIST[n].append('')

            for n in range(len(DATA_LIST)):
                for y in range(12):
                    DATA_LIST[n][y + 3] = ''

                sql_get_swipes_tx = 'SELECT TOP (12) twork_swipe.date_and_time from twork INNER JOIN twork_swipe ON twork.work_id = twork_swipe.work_id ' \
                                    ' WHERE twork.employee_id = ' + str(
                    DATA_LIST[n][2]) + ' AND twork.[type] = 1000 and twork.date_and_time = ' + f.get_sql_date(
                    datetime.now(), "yyyy-mm-dd") + ' ORDER BY twork_swipe.date_and_time ASC'
                swipes = sqlconns.sql_select_into_list(sql_get_swipes_tx)
                if swipes != -1 and len(swipes) > 0:
                    for y in range(len(swipes)):
                        DATA_LIST[n][y + 3] = swipes[y][0]
#************************************************************
        self.tableWidget.verticalHeader().setVisible(False)

        self.tableWidget.setHorizontalHeaderLabels([' LastName               ',' FirstName              ',' IN      ',' OUT  ',' IN      ', ' OUT  ',' IN       ',' OUT  ',' IN      ',' OUT   ',
                                                    ' IN       ', ' OUT  ', ' IN      ', ' OUT   ',
                                                    ' Total      '
                                                    ])
        for n in range(15):
            self.tableWidget.horizontalHeaderItem(n).setTextAlignment(Qt.AlignLeft)

        rowcount = 0
        if len(DATA_LIST) == 1:
            rowcount = 1
        else:
            rowcount = int((len(DATA_LIST)+1))

        self.tableWidget.setRowCount(rowcount)

        for n in range(len(DATA_LIST)):
            row_number = int((n))
            if n %2 ==0:
                column ='left'
            else:
                column = 'left'

            swipes_count = 0

            for y in range(15):
                yy=y
                if yy>2: yy -= 1
                if y != 2 :
                    if y >2 and DATA_LIST[n][y] != 'None' and DATA_LIST[n][y] != '':
                        field = f.convert_sql_date(DATA_LIST[n][y],"hh:mm")
                        swipes_count+=1
                    else:
                        field = str(DATA_LIST[n][y])

                self.tableWidget.setItem(row_number, yy, QTableWidgetItem(field))

            #green
            r=OUT_RED
            g=OUT_GREEN
            b=OUT_BLUE
            if swipes_count % 2 !=0:
                # orange
                r = IN_RED
                g = IN_GREEN
                b = IN_BLUE

            #get total hours for display if there are clockings
            if swipes_count > 0:
                display_emp_total = self.get_total_time(n,DATA_LIST)
                self.tableWidget.setItem(row_number, 14, QTableWidgetItem(display_emp_total))
            else:
                null_time = '0:00'
                self.tableWidget.setItem(row_number, 14, QTableWidgetItem(null_time))


            for col in range(15):
                actual_col = col
                if self.tableWidget.item(row_number, actual_col)!=None: self.tableWidget.item(row_number, actual_col).setBackground(QtGui.QColor(r,g,b))


        stylesheet = "QHeaderView::section{Background-color:rgb(117,146,156);\
                               border-radius:40px;}"
        self.tableWidget.setStyleSheet(stylesheet)
        self.tableWidget.resizeColumnsToContents()
        del DATA_LIST
        self.restart()

    def restart(self):
        del self.timer
        self.timer = QtCore.QTimer.singleShot(1000, self.refreshTable)

    def start(self):
        #self.timer.start()
        v = 0

    def stop(self):
        self.timer.stop()

    def get_employee_details(self):

        # global DATA_LIST
        tx = "SELECT "
        if SQL_TOP != '': tx += SQL_TOP + ' '
        tx += "last_name, first_name, employee_id from temployee "
        tx += EMPLOYEE_SQL
        ret = sqlconns.sql_select_into_list(tx)
        if ret == -1:
            DATA_LIST = [['None', 'None', '0', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']]
        else:
            DATA_LIST = [x for x in ret]
            for n in range(len(DATA_LIST)):
                DATA_LIST[n] = DATA_LIST[n] = [x for x in DATA_LIST[n]]
                for y in range(12):
                    DATA_LIST[n].append('')

            for n in range(len(DATA_LIST)):
                for y in range(8):
                    DATA_LIST[n][y + 3] = ''

                sql_get_swipes_tx = 'SELECT TOP (8) twork_swipe.date_and_time from twork INNER JOIN twork_swipe ON twork.work_id = twork_swipe.work_id ' \
                                    ' WHERE twork.employee_id = ' + str(
                    DATA_LIST[n][2]) + ' AND twork.[type] = 1000 and twork.date_and_time = ' + f.get_sql_date(
                    datetime.now(), "yyyy-mm-dd") + ' ORDER BY twork_swipe.date_and_time ASC'
                swipes = sqlconns.sql_select_into_list(sql_get_swipes_tx)
                if swipes != -1 and len(swipes) > 0:
                    for y in range(len(swipes)):
                        DATA_LIST[n][y + 3] = swipes[y][0]
        #return [['None', 'None', '0', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']]

        return DATA_LIST

    def get_total_time(self,row_number,DATA_LIST):
        mins = 0
        y = 3
        for n in range(6):
            mins += work_out_pairs(DATA_LIST[row_number][y], DATA_LIST[row_number][y+1])
            y+=2
        hours = str(int(mins / 60)) + "h "
        mins = mins % 60
        if len(str(mins)) == 1: mins = "0" + str(mins)
        hours += str(mins) + 'm'
        return hours

def work_out_pairs(time1,time2):

    if time1 == None or time1== ' ' or time1 == '': return 0
    time1 = str(f.convert_sql_date(time1,"hh:mm"))
    if time2 == None or time2== ' ' or time2=='':
        time2 = str(f.convert_sql_date(datetime.now(),"hh:mm"))
    else:
        time2 = str(f.convert_sql_date(time2,"hh:mm"))
    try:
        h1 = str(time1).split(':')
        h2 = str(time2).split(':')
        if int(h1[0]) > 23: return 0
        if int(h2[0]) > 23: return 0
        if int(h1[1]) > 59: return 0
        if int(h2[1]) > 59: return 0
        mins1 = (int(h1[0]) * 60) + int(h1[1])
        mins2 = (int(h2[0]) * 60) + int(h2[1])
        if mins2 < mins1: mins2 += (24*60)
        mins1 = mins2-mins1
        return mins1
    except:
        return 0

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
    result = QMessageBox.warning(w, 'ADP Error', warning, QMessageBox.Ok)
    if result == QMessageBox.Ok:
        sys.exit(a.exit())
    w.show()

    sys.exit(a.exec_())

def set_env():
    global EMPLOYEE_SQL
    global SQL_TOP
    global IN_RED
    global IN_GREEN
    global IN_BLUE
    global OUT_RED
    global OUT_GREEN
    global OUT_BLUE
    global SCREEN_SIZE_X
    global SCREEN_SIZE_Y
    global GRID_POS_X
    global GRID_POS_Y
    global GRID_SIZE_X
    global GRID_SIZE_Y
    global ADP_REFRESH

    path = str.replace(gl.SCRIPT_ROOT,'adp.exe','')
    if os.path.isfile(path + 'database.ini'):
        if sqlconns.readsql_connection_timeware_main_6() == 0:
            showdialog('Error connecting to database!!!! ' + path)
            return False
        elif sqlconns.readsql_connection_timeware_main_6() == 1:
            test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
            if test_comms == 0:
                    showdialog('Error connecting to database!!!! ' + path)
            else:
                if os.path.isfile(gl.ADP2_INI):
                    fob=open(gl.ADP2_INI, "r")
                    listme = fob.readlines()
                    fob.close()
                else:
                    showdialog('Error reading adp.ini file!!!!')
                    return False
                try:
                    for index in range(len(listme)):
                        if "'" in listme[index]: continue
                        if 'employee_sql' in listme[index]:
                            EMPLOYEE_SQL = str.split(listme[index],'=')[1]
                        if 'top_sql' in listme[index]:
                            SQL_TOP = str.split(listme[index],'=')[1]
                        if 'IN_RED' in listme[index]:
                            IN_RED = int(str.split(listme[index],'=')[1])
                        if 'IN_GREEN' in listme[index]:
                            IN_GREEN = int(str.split(listme[index], '=')[1])
                        if 'IN_BLUE' in listme[index]:
                            IN_BLUE = int(str.split(listme[index], '=')[1])
                        if 'OUT_RED' in listme[index]:
                            OUT_RED = int(str.split(listme[index], '=')[1])
                        if 'OUT_GREEN' in listme[index]:
                            OUT_GREEN = int(str.split(listme[index], '=')[1])
                        if 'OUT_BLUE' in listme[index]:
                            OUT_BLUE = int(str.split(listme[index], '=')[1])
                        if 'SCREEN_SIZE_X' in listme[index]:
                            SCREEN_SIZE_X = int(str.split(listme[index], '=')[1])
                        if 'SCREEN_SIZE_Y' in listme[index]:
                            SCREEN_SIZE_Y = int(str.split(listme[index], '=')[1])
                        if 'GRID_POS_X' in listme[index]:
                            GRID_POS_X = int(str.split(listme[index], '=')[1])
                        if 'GRID_POS_Y' in listme[index]:
                            GRID_POS_Y = int(str.split(listme[index], '=')[1])
                        if 'GRID_SIZE_X' in listme[index]:
                            GRID_SIZE_X = int(str.split(listme[index], '=')[1])
                        if 'GRID_SIZE_Y' in listme[index]:
                            GRID_SIZE_Y = int(str.split(listme[index], '=')[1])
                        if 'ADP_REFRESH' in listme[index]:
                            ADP_REFRESH = int(str.split(listme[index], '=')[1])


                except Exception as e:
                    return False
                return True
    else:
        showdialog('Error connecting to database!!!! ' + path)
        return False

if __name__ == '__main__':
    if set_env() == True:
        app=QtGui.QApplication(sys.argv)
        ex = Ui_MainWindow()
        ex.show()
        #ex.start()
        sip.setdestroyonexit(False)
        sys.exit(app.exec())
