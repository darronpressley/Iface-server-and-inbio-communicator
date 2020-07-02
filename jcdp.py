# -*- coding: utf-8 -*-

#DP
#started 22012019
#Job Costing Display Panel to show staff on jobs.
#similar project to ADP, uses ADP.ini file for options and database.ini from ifaceserver.

APPNAME = "JCDP"

#lastname, firstname , employee_id, LAst Swipe Time, Last Swipe Date,stop_time, Job No, Job Description, op description x 2
#4 columns required after employee id = 0
#DATA_LIST = [['None','None','0','None','None','None','None','None', 'None'],['None','None','0','None','None','None','None','None', 'None']]

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


#Columns for Datalist
SQL_COL_LN = 0
SQL_COL_FN = 1
SQL_COL_ID = 2
SQL_COL_START_DATE = 3
SQL_COL_START_TIME = 4
SQL_COL_STOP_TIME = 5
SQL_COL_CODE = 6
SQL_COL_DESC = 7
SQL_COL_OP = 8

GRID_COL_LN = 0
GRID_COL_FN = 1
GRID_COL_START_DATE = 2
GRID_COL_START_TIME = 3
GRID_COL_CODE = 4
GRID_COL_DESC = 5
GRID_COL_OP = 6



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
        # TODO can this move so it shows as the table is built?
        self.tableWidget.setHorizontalHeaderLabels(
            [' LastName               ', ' FirstName              ', ' Swipe Date      ', ' Last Swipe Time  ',
             ' Job No      ', ' Job Description     ', ' Operation Description     ',
             ' ',
             ' LastName               ', ' FirstName              ',
             ' Last Swipe Time      ', ' Swipe Date  ', ' Job No      ', ' Job Description     ',
             ' Operation Description     '])
        self.tableWidget.verticalHeader().setVisible(False)
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

    def refreshTable(self):
        #global DATA_LIST
        # lastname, firstname , employee_id, LAst Swipe Time, Last Swipe Date,stop_time Job No, Job Description x 2
        DATA_LIST = [['None', 'None', '0', 'None', 'None', 'None', 'None', 'None', 'None'],
                          ['None', 'None', '0', 'None', 'None', 'None', 'None', 'None','None',]]

#**********************************************************
        tx = "SELECT "
        if SQL_TOP != '': tx += SQL_TOP + ' '
        tx += "last_name, first_name, employee_id from temployee "
        tx += EMPLOYEE_SQL
        ret = sqlconns.sql_select_into_list(tx)
        # lastname, firstname , employee_id, LAst Swipe Time, Last Swipe Date, Job No, Job Description
        if ret == -1:
            DATA_LIST = [['None', 'None', '0', 'None', 'None', 'None', 'None', 'None', 'None']]
        else:
            DATA_LIST = [x for x in ret]
            for n in range(len(DATA_LIST)):
                DATA_LIST[n] = DATA_LIST[n] = [x for x in DATA_LIST[n]]
                for y in range(6):# was 8 for 8 swipes now 6 for 6 fields in the select query
                    DATA_LIST[n].append('')
            for n in range(len(DATA_LIST)):
                for y in range(6):
                    DATA_LIST[n][y + 3] = ''

                ret = "SELECT top 1 format(twork_job.start_time,'dd/MM/yyyy')as start_date, format(twork_job.start_time,'HH:mm')as start_date, twork_job.stop_time,tjob.code, tjob.description, toperation.description AS Expr1"\
                                    " FROM"\
                                    " twork INNER JOIN"\
                                    ' twork_job ON twork.work_id = twork_job.work_id INNER JOIN'\
                                    ' tjob ON twork_job.job_id = tjob.job_id INNER JOIN'\
                                    ' toperation ON twork_job.operation_id = toperation.operation_id'\
                                    ' WHERE twork.employee_id = ' + str(DATA_LIST[n][2]) + \
                                    ' order by date_and_time desc'

                ret = sqlconns.sql_select_into_list(ret)
                if ret != -1 and len(ret) > 0:
                    DATA_LIST[n][SQL_COL_START_DATE] = ret[0][0]
                    DATA_LIST[n][SQL_COL_START_TIME] = str(ret[0][1])
                    if ret[0][2] != None:
                        DATA_LIST[n][SQL_COL_STOP_TIME] = ret[0][2]
                    else:
                        DATA_LIST[n][SQL_COL_STOP_TIME] = ''
                    DATA_LIST[n][SQL_COL_CODE] = ret[0][3]
                    DATA_LIST[n][SQL_COL_DESC] = ret[0][4]
                    DATA_LIST[n][SQL_COL_OP] = ret[0][5]




        for n in range(15):#was 22
            self.tableWidget.horizontalHeaderItem(n).setTextAlignment(Qt.AlignLeft)

        #rowcount = 0
        if len(DATA_LIST) == 1:
            rowcount = 1
        else:
            rowcount = int((len(DATA_LIST)+1)/2)

        self.tableWidget.setRowCount(rowcount)

        for n in range(len(DATA_LIST)):
            row_number = int((n)/2)
            if n %2 == 0:
                column ='left'
            else:
                column = 'right'

            if column == 'left':
                col_mod = 0
            else:
                col_mod = 8

#list all the column mapping here
            field = DATA_LIST[n][SQL_COL_LN]
            self.tableWidget.setItem(row_number, GRID_COL_LN + col_mod, QTableWidgetItem(field))
            field = DATA_LIST[n][SQL_COL_FN]
            self.tableWidget.setItem(row_number, GRID_COL_FN + col_mod, QTableWidgetItem(field))
            field = DATA_LIST[n][SQL_COL_START_DATE]
            self.tableWidget.setItem(row_number, GRID_COL_START_DATE + col_mod, QTableWidgetItem(field))
            field = DATA_LIST[n][SQL_COL_START_TIME]
            self.tableWidget.setItem(row_number, GRID_COL_START_TIME + col_mod, QTableWidgetItem(field))
            field = DATA_LIST[n][SQL_COL_CODE]
            self.tableWidget.setItem(row_number, GRID_COL_CODE + col_mod, QTableWidgetItem(field))
            field = DATA_LIST[n][SQL_COL_DESC]
            self.tableWidget.setItem(row_number, GRID_COL_DESC + col_mod, QTableWidgetItem(field))
            field = DATA_LIST[n][SQL_COL_OP]
            self.tableWidget.setItem(row_number, GRID_COL_OP + col_mod, QTableWidgetItem(field))

            #go green and then if no start time go red
            #if there is a stop_time go red
            r=OUT_RED
            g=OUT_GREEN
            b=OUT_BLUE
            if DATA_LIST[n][SQL_COL_START_DATE] == None or DATA_LIST[n][SQL_COL_START_DATE] != '':
                # orange
                r = IN_RED
                g = IN_GREEN
                b = IN_BLUE

            for col in range(7):#was 11
                actual_col = col
                if column=='right': actual_col+=8 #was 12
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
            DATA_LIST = [['None', 'None', '0', 'None', 'None', 'None', 'None', 'None']]
        else:
            DATA_LIST = [x for x in ret]
            for n in range(len(DATA_LIST)):
                DATA_LIST[n] = DATA_LIST[n] = [x for x in DATA_LIST[n]]
                for y in range(8):
                    DATA_LIST[n].append('')

            for n in range(len(DATA_LIST)):
                for y in range(8):
                    DATA_LIST[n][y + 3] = ''

                sql_get_swipes_tx = "SELECT top 1 format(twork_job.start_time,'dd/MM/yyyy')as start_date, format(twork_job.start_time,'HH:mm')as start_date, twork_job.stop_time,tjob.code, tjob.description, toperation.description AS Expr1"\
                                    "FROM"\
                                    ' twork INNER JOIN'\
                                    ' twork_job ON twork.work_id = twork_job.work_id INNER JOIN'\
                                    ' tjob ON twork_job.job_id = tjob.job_id INNER JOIN'\
                                    ' toperation ON twork_job.operation_id = toperation.operation_id'\
                                    ' WHERE twork.employee_id = ' + str(DATA_LIST[n][2]) + \
                                    ' order by date_and_time desc'

                ret = sqlconns.sql_select_into_list(sql_get_swipes_tx)
                if ret != -1 and len(ret) > 0:
                    DATA_LIST[n][SQL_COL_START_DATE] = ret[0]
                    DATA_LIST[n][SQL_COL_START_TIME] = ret[1]
                    DATA_LIST[n][SQL_COL_STOP_TIME] = ret[2]
                    DATA_LIST[n][SQL_COL_CODE] = ret[3]
                    DATA_LIST[n][SQL_COL_DESC] = ret[4]
                    DATA_LIST[n][SQL_COL_OP] = ret[5]

        return DATA_LIST

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

    path = str.replace(gl.SCRIPT_ROOT,'Job Costing Display Panel.exe','')
    path = str.replace(gl.SCRIPT_ROOT, 'JCDP.exe', '')
    if os.path.isfile(path + 'database.ini'):
        if sqlconns.readsql_connection_timeware_main_6() == 0:
            showdialog('Error connecting to database!!!! ' + path)
            return False
        elif sqlconns.readsql_connection_timeware_main_6() == 1:
            test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
            if test_comms == 0:
                    showdialog('Error connecting to database!!!! ' + path)
            else:
                if os.path.isfile(gl.ADP_INI):
                    fob=open(gl.ADP_INI, "r")
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
        sip.setdestroyonexit(False)
        sys.exit(app.exec())
