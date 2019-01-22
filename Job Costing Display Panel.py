# -*- coding: utf-8 -*-

#DP
#started 22012019
#Job Costing Display Panel to show staff on jobs.
#similar project to ADP, uses ADP.ini file for options and database.ini from ifaceserver.

APPNAME = "JCDP"

#lastname, firstname , employee_id, LAst Swipe Time, Last Swipe Date,stop_time, Job No, Job Description, op description x 2
#4 columns required after employee id = 0
#DATA_LIST = [['None','None','0','None','None','None','None','None', 'None'],['None','None','0','None','None','None','None','None', 'None']]

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

GRID_COL_LN = 1
GRID_COL_FN = 2
GRID_COL_START_DATE = 3
GRID_COL_START_TIME = 4
GRID_COL_CODE = 5
GRID_COL_DESC = 6
GRID_COL_OP = 7



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

        self.timer = QtCore.QTimer.singleShot(1000, self.refreshTable)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        self.setWindowIcon(QtGui.QIcon('python_small.ico'))
        MainWindow.resize(1300, 800)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 1300, 800))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(23)
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

                ret = "SELECT top 1 format(twork_job.start_time,'dd/mm/yyyy')as start_date, format(twork_job.start_time,'HH:mm')as start_date, twork_job.stop_time,tjob.code, tjob.description, toperation.description AS Expr1"\
                                    " FROM"\
                                    " twork INNER JOIN"\
                                    ' twork_job ON twork.work_id = twork_job.work_id INNER JOIN'\
                                    ' tjob ON twork_job.job_id = tjob.job_id INNER JOIN'\
                                    ' toperation ON twork_job.operation_id = toperation.operation_id'\
                                    ' WHERE twork.employee_id = ' + str(DATA_LIST[n][2]) + \
                                    ' order by date_and_time desc'
                print(ret)

                ret = sqlconns.sql_select_into_list(ret)
                if ret != -1 and len(ret) > 0:
                    print('heres ret', ret[0])
                    DATA_LIST[n][SQL_COL_START_DATE] = ret[0][0]
                    DATA_LIST[n][SQL_COL_START_TIME] = str(ret[0][1])
                    if ret[0][2] != None:
                        DATA_LIST[n][SQL_COL_STOP_TIME] = ret[0][2]
                    else:
                        DATA_LIST[n][SQL_COL_STOP_TIME] = ''
                    DATA_LIST[n][SQL_COL_CODE] = ret[0][3]
                    DATA_LIST[n][SQL_COL_DESC] = ret[0][4]
                    DATA_LIST[n][SQL_COL_OP] = ret[0][5]
                print("----------", DATA_LIST[n])


#************************************************************
        #Colum NAMES
        self.tableWidget.verticalHeader().setVisible(False)

#TODO can this move so it shows as the table is built?
        self.tableWidget.setHorizontalHeaderLabels([' LastName               ',' FirstName              ',' Last Swipe Time      ',' Swipe Date  ',' Job No      ', ' Job Description     ',' Operation Description     ',
                                                    ' ',
                                                    ' LastName               ', ' FirstName              ',
                                                    ' Last Swipe Time      ',' Swipe Date  ',' Job No      ', ' Job Description     ',' Operation Description     '])
        for n in range(12):#was 22
            self.tableWidget.horizontalHeaderItem(n).setTextAlignment(Qt.AlignLeft)

        #rowcount = 0
        if len(DATA_LIST) == 1:
            rowcount = 1
        else:
            rowcount = int((len(DATA_LIST)+1)/2)

        self.tableWidget.setRowCount(rowcount)

        for n in range(len(DATA_LIST)):
            row_number = int((n)/2)
            if n %2 ==0:
                column ='left'
            else:
                column = 'right'

            if column == 'left':
                col_mod = 0
            else:
                col_mod = 8

#list all the column mapping here
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

            #green
            r=OUT_RED
            g=OUT_GREEN
            b=OUT_BLUE
            if DATA_LIST[n][5] == None:#
                # orange
                r = IN_RED
                g = IN_GREEN
                b = IN_BLUE

            #TODO remove this section not needed as we have no total
            #get total hours for display if there are clockings
            '''if swipes_count > 0:
                display_emp_total = self.get_total_time(n,DATA_LIST)
                if column == 'left':
                    self.tableWidget.setItem(row_number, 10, QTableWidgetItem(display_emp_total))
                else:
                   self.tableWidget.setItem(row_number, 22, QTableWidgetItem(display_emp_total))
            else:
                null_time = '0:00'
                if column == 'left':
                    self.tableWidget.setItem(row_number, 10, QTableWidgetItem(null_time))
                else:
                   self.tableWidget.setItem(row_number, 22, QTableWidgetItem(null_time))'''

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
#TODO delete later
              #  sql_get_swipes_tx = 'SELECT TOP (8) twork_swipe.date_and_time from twork INNER JOIN twork_swipe ON twork.work_id = twork_swipe.work_id ' \
               #                     ' WHERE twork.employee_id = ' + str(
                #    DATA_LIST[n][2]) + ' AND twork.[type] = 1000 and twork.date_and_time = ' + f.get_sql_date(
                 #   datetime.now(), "yyyy-mm-dd") + ' ORDER BY twork_swipe.date_and_time ASC'

                sql_get_swipes_tx = "SELECT top 1 format(twork_job.start_time,'dd/mm/yyyy')as start_date, format(twork_job.start_time,'HH:mm')as start_date, twork_job.stop_time,tjob.code, tjob.description, toperation.description AS Expr1"\
                                    "FROM"\
                                    ' twork INNER JOIN'\
                                    ' twork_job ON twork.work_id = twork_job.work_id INNER JOIN'\
                                    ' tjob ON twork_job.job_id = tjob.job_id INNER JOIN'\
                                    ' toperation ON twork_job.operation_id = toperation.operation_id'\
                                    ' WHERE twork.employee_id = ' + str(DATA_LIST[n][2]) + \
                                    ' order by date_and_time desc'

                ret = sqlconns.sql_select_into_list(sql_get_swipes_tx)
                print('heres ret',ret)
                if ret != -1 and len(ret) > 0:
                    DATA_LIST[n][SQL_COL_START_DATE] = ret[0]
                    DATA_LIST[n][SQL_COL_START_TIME] = ret[1]
                    DATA_LIST[n][SQL_COL_STOP_TIME] = ret[2]
                    DATA_LIST[n][SQL_COL_CODE] = ret[3]
                    DATA_LIST[n][SQL_COL_DESC] = ret[4]
                    DATA_LIST[n][SQL_COL_OP] = ret[5]
                print("----------",DATA_LIST[n])
        #return [['None', 'None', '0', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']] #TODO cane we remove this?

        return DATA_LIST

 #class TerminalX(QtCore.QThread):
#    def __init__(self,parent=None):
#        QtCore.QThread.__init__(self,parent)
#        self.test=''

 #   def run(self):
  #      x = ''
   #     print("in run")
    #    while self.COUNT_COMMANDS == 1:
     #       self.get_employee_details()
      #      #time.sleep(10)
#

#def get_total_time(row_number):
#    mins = 0
#    y = 3
#    for n in range(4):
#        mins += work_out_pairs(DATA_LIST[row_number][y], DATA_LIST[row_number][y+1])
#        y+=2#

 #   hours = str(int(mins / 60)) + "h "
  #  mins = mins % 60
 #   if len(str(mins)) == 1: mins = "0" + str(mins)
 #   hours += str(mins) + 'm'
 #   return hours

#TODO delete this when working
#def get_employee_details():
#    #global DATA_LIST
#    tx = "SELECT "
#    if SQL_TOP != '': tx += SQL_TOP + ' '
#    tx += "last_name, first_name, employee_id from temployee "
#    tx += EMPLOYEE_SQL
   # ret = sqlconns.sql_select_into_list(tx)
#    if ret == -1:
#        self.DATA_LIST = [['None', 'None','0', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']]
#    else:
#        self.DATA_LIST = [x for x in ret]
#        for n in range(len(DATA_LIST)):
#            DATA_LIST[n] = DATA_LIST[n] = [x for x in DATA_LIST[n]]
#            for y in range(8):
#                DATA_LIST[n].append('')#
#
#        for n in range(len(DATA_LIST)):#
 #           for y in range(8):
 #               DATA_LIST[n][y+3] = ''##
#
#            sql_get_swipes_tx = 'SELECT TOP (8) twork_swipe.date_and_time from twork INNER JOIN twork_swipe ON twork.work_id = twork_swipe.work_id ' \
 #                                   ' WHERE twork.employee_id = ' + str(DATA_LIST[n][2]) + ' AND twork.[type] = 1000 and twork.date_and_time = ' + f.get_sql_date(datetime.now(),"yyyy-mm-dd") + ' ORDER BY twork_swipe.date_and_time ASC'
  #          swipes = sqlconns.sql_select_into_list(sql_get_swipes_tx)
   #         if swipes != -1 and len(swipes) > 0:
    #            for y in range(len(swipes)):
     #               DATA_LIST[n][y+3] = swipes[y][0]

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
    path = str.replace(gl.SCRIPT_ROOT,'jcdp.exe','')
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
