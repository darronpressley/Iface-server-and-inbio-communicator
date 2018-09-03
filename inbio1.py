#there is a lot of commented out code in this project
#this is to allow quickish switching between running this as a service and running as a application
# commented out unused packages...remove if code still works without them.
import inspect
import decimal
import sys
import functions as f
import sqlconns
import os
import gl
import time
import datetime
from ctypes import *
#import servicemanager
import win32serviceutil
import win32service
import win32event
import threading
import asyncore


APPNAME = "Inbio Communicator"
# log file names
COMM_ERROR = "communications_log"
ERROR_LOG =  "error_log"

#set this to 0 when finished
SPOOL_TRANSACTION = 1


class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "Inbio Communicator"
    _svc_display_name_ = "Inbio Communicator"
    _svc_description_ = "Inbio Communicator from North Time and Data"

    def __init__(self,args):
         win32serviceutil.ServiceFramework.__init__(self, args)
         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        asyncoreThread = threading.Thread(target=asyncore.loop, kwargs={'timeout': 1})
        asyncoreThread.start()
        myStatusThread = threading.Thread(target=win32event.WaitForSingleObject,
                                          args=(self.hWaitStop, win32event.INFINITE))
        myStatusThread.start()

        log_initialise()
        while True:
            if myStatusThread.isAlive():
            #if True:
                #dte = str(datetime.datetime.now())
                #e = open("c:/temp/1log.txt", 'a')
                #e.write(dte + """\n""")
                #e.write(gl.ERROR_LOG + "\n")
                #e.close()
                main_function()
            else:
                self.server.close()
                self.asyncoreThread.join()
                break
            time.sleep(1)


def log_initialise():
    f.error_logging(APPNAME, "Service started.", "error_log","")


def main_function():
    if os.path.isfile(gl.SCRIPT_ROOT + 'database.ini'):
        if sqlconns.readsql_connection_timeware_main_6() == 0:
            f.error_logging(APPNAME, "Error reading database.ini file.", "error_log","")
            return -1
        elif sqlconns.readsql_connection_timeware_main_6() == 1:
            test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
            if test_comms == 0:
                    f.error_logging(APPNAME, "Error connecting to SQL server.", "error_log","")
                    return -1
            else:
                test_pause = inbio_started()
                if test_pause == -1:
                    f.error_logging(APPNAME,
                                                "Main Loop aborted due to error (check sql connection).",
                                                "error_log", "")
                    return -1
                if test_pause == True:
                    ret = inbio_communicate()
                    if ret == -1:
                        f.error_logging(APPNAME, "Main Loop aborted due to error (check sql connection).",
                                            "error_log", "")
                        return -1
                else: return
    else:
        f.error_logging(APPNAME, "Error reading database.ini file.", "error_log","")
        return -1



def inbio_communicate():
    #reset inbio_events
    ret = sqlconns.sql_command("update d_inbio_events SET completed = 0")
    if ret == -1: return -1
    sql_text = "SELECT terminal_id,number,description,ip_address FROM tterminal WHERE number >= 1000 AND configuration = " + gl.access_terminal_configuration + \
                       " ORDER BY number"
    terminal_list = sqlconns.sql_select_into_list(sql_text)
    if terminal_list == -1: return -1
    for index in range(len(terminal_list)):
        if terminal_list[index][1] % 100 == 1:
            ret = poll_inbio(terminal_list[index][3], terminal_list[index][0])
            if ret == -1: return -1
    ret = do_inbio_events(terminal_list)
    if ret == -1: return -1
    return


def poll_inbio(ip_address, terminal_id):
    function = inspect.stack()[0][3]
    constr = create_string_buffer(
        str.encode('protocol=TCP,ipaddress=' + ip_address + ',port=4370,timeout=' + str(gl.COMM_TIMEOUT) + ',passwd='))
    commpro = windll.LoadLibrary("plcommpro.dll")
    hcommpro = commpro.Connect(constr)
    if hcommpro == 0:
        no_connection_error(ip_address)
        ret = comm_failure_date_time(terminal_id)
        if ret == -1: return -1
        return 0
    ret = comm_success_date_time(terminal_id)
    if ret == -1:
        commpro.Disconnect(hcommpro)
        return -1
    table = create_string_buffer(str.encode("transaction"))
    fieldname = create_string_buffer(str.encode("*"))
    pfilter = create_string_buffer(str.encode(""))
    options = create_string_buffer(str.encode(""))
    buffer = create_string_buffer(4 * 1024 * 1024)
    ret = commpro.GetDeviceData(hcommpro, buffer, 4 * 1024 * 1024, table, fieldname, pfilter, options)
    if ret < 0:
        commpro.Disconnect(hcommpro)
        ret_error(ip_address, ret)
        return 0
    else:
        polled = str(buffer.raw)
        polled = polled.replace("b'", "")
        polled = polled[:-1]
        polled = polled.replace("\\x00", "")
        #first line is headers like headers of a csv
        #last line is empty
        poll_list = polled.split("""\\r\\n""")
        test_insert_transactions = insert_transactions(poll_list, terminal_id)
        if test_insert_transactions == -1: return -1
        #at some point you want to delete transactions table but not yet
        if test_insert_transactions:
            p_table = create_string_buffer(str.encode("transaction"))
            p_data = create_string_buffer(str.encode(""))
            ret = commpro.DeleteDeviceData(hcommpro,p_table,p_data,"")
            if ret < 0:
                ret_error(ip_address, ret, function)
            return 0
        #set time
        p_items = create_string_buffer(str.encode("DateTime=" + str(f.convert_now_to_int())))
        ret = commpro.SetDeviceParam(hcommpro, p_items)
        if ret < 0:
            ret_error(ip_address, ret, function)
            return 0

    commpro.Disconnect(hcommpro)
    return 0


def do_inbio_events(terminal_list):
    function = inspect.stack()[0][3]
    #first of all get the events, if dont need to do this then dont
    event_list = inbio_events_into_list()
    if event_list == -1: return -1
    if event_list == 0: return 0
    if len(event_list) == 0: return 0  #dont need to do any comms if here
    for index in range(len(terminal_list)):
        if terminal_list[index][1] % 100 == 1:
            ret = send_events(terminal_list[index][0], terminal_list[index][3], event_list)
            if ret == -1: return -1
        #delete all events still at 0 as there were no errors
    #swap these when ready
    sqltxt = "DELETE from d_inbio_events WHERE completed = 0"
    #swap below line with line above if more testing is required.
    #this means all events will be reset as requiring updating to hardware again and not deleted
    #sqltxt = "UPDATE d_inbio_events SET completed = 0"
    ret = sqlconns.sql_command(sqltxt)
    if ret == -1:
        f.error_logging(APPNAME, "sql error", "sql", function)
        return -1
    return 0


def send_events(terminal_id, ip_address, event_list):
    function = inspect.stack()[0][3]
    #send each command seperately in case we have hundreds, you wil be connecting to this terminal, if comms error set completed to 2 on all events
    constr = create_string_buffer(
        str.encode('protocol=TCP,ipaddress=' + ip_address + ',port=4370,timeout=' + str(gl.COMM_TIMEOUT) + ',passwd='))
    commpro = windll.LoadLibrary("plcommpro.dll")
    hcommpro = commpro.Connect(constr)
    if hcommpro == 0:
        no_connection_error(ip_address)
        ret = completed_failure("")
        if ret == -1: return -1
        return 0
    #do timezone build
    timezone_string = f.fetch_timezone_string()
    if timezone_string == -1:
        commpro.Disconnect(hcommpro)
        return -1
    p_table = create_string_buffer(str.encode("timezone"))
    for index in range(len(timezone_string)):
        ret = commpro.SetDeviceData(hcommpro, p_table, create_string_buffer(str.encode(timezone_string[index])), "")
        if ret < 0:
            ret_error(ip_address, ret, function)
            return 0
    term_list = get_doors_from_ip(ip_address)
    if term_list == -1: return -1
    for index in range(len(event_list)):
        #didnt do leaver check bro
        sql_text = """SELECT temployee.employee_id, temployee.badge, temployee.date_started_with_company, temployee.badge_activation, temployee.badge_expiry, tterminal_policy.data
                FROM temployee INNER JOIN
                temployee_status ON temployee.employee_status_id = temployee_status.employee_status_id INNER JOIN
                tterminal_policy ON temployee.terminal_policy_id = tterminal_policy.terminal_policy_id
                WHERE temployee_status.exclude_from_calculation <> 1 AND
                temployee.employee_id = """ + event_list[index][1] + """ AND (
                data like '%TerminalAssignment\AccessControl\optAllYes,True%'"""
        #here is fuxked up because its not checking corect things.
        for xx in range(len(term_list)):
            sql_text += """ OR data like """ + "'%TerminalAssignment\\AccessControl\\Terminal\\" + str(
                term_list[xx][0]) + ",True%'"
        sql_text += ")"
        employee_list = sqlconns.sql_select_into_list(sql_text)
        if employee_list == -1: return -1
        #put minus 1's in here when you figure out why the fuck it not working
        #also if person not being found you will need to delete them
        #remember they said you should not delete anyone
        #check with Kiran but for now am going to delete guy from unit then add the details.
        p_authorize = create_string_buffer(str.encode("userauthorize"))
        p_data = create_string_buffer(str.encode("Pin=" + event_list[index][1]))
        ret = commpro.DeleteDeviceData(hcommpro, p_authorize, p_data, "")
        if ret < 0:
            ret_error(ip_address, ret, function)
            ret = completed_failure(str(event_list[index][1]))
            if ret == -1:
                commpro.Disconnect(hcommpro)
                return 0
        p_user = create_string_buffer(str.encode("user"))
        p_data = create_string_buffer(str.encode("Pin=" + event_list[index][1]))
        ret = commpro.DeleteDeviceData(hcommpro, p_user, p_data, "")
        if ret < 0:
            ret_error(ip_address, ret, function)
            ret = completed_failure(str(event_list[index][1]))
            if ret == -1:
                commpro.Disconnect(hcommpro)
                return 0
        if len(employee_list) > 0:
            p_data = ""
            p_data = "Pin=" + str(employee_list[0][0])

            if employee_list[0][1] != None: p_data += """\tCardNo=""" + str(int(employee_list[0][1]))
            p_data += "\tStartTime=" + get_start_time(employee_list[0][2],
                                                      employee_list[0][3]) + "\tEndTime=" + get_end_time(
                employee_list[0][4])

            p_data = create_string_buffer(str.encode(p_data))
            ret = commpro.SetDeviceData(hcommpro, p_user, p_data, "")
            if ret < 0:
                ret_error(ip_address, ret, function)
                commpro.Disconnect(hcommpro)
                ret = completed_failure(str(event_list[index][1]))
                if ret == -1: return -1
                return 0
            data = employee_list[0][5]
            datalist = data.split("""\r""")

            for z in range(len(term_list)):
                #check you allowed for this clock
                for y in range(len(datalist)):
                    term_policy_string = """AccessControl\\Terminal\\"""
                    term_policy_string += str(term_list[z][0]) + """,True"""
                    if term_policy_string in datalist[y]:
                        door_id = get_door_id(term_list[z][1])
                        auth_timezone_id = datalist[y + 1]
                        auth_timezone_id = auth_timezone_id[-1]
                        p_authorize = create_string_buffer(str.encode("userauthorize"))
                        if int(auth_timezone_id) > 0:
                            p_data = ("Pin=" + str(employee_list[0][
                                0]) + "\tAuthorizeTimezoneId=" + auth_timezone_id + "\tAuthorizeDoorId=" + str(door_id))
                            p_data = create_string_buffer(str.encode(p_data))
                            ret = commpro.SetDeviceData(hcommpro, p_authorize, p_data, "")
                            if ret < 0:
                                ret_error(ip_address, ret, function)
                                commpro.Disconnect(hcommpro)
                                ret = completed_failure(str(event_list[index][1]))
                                if ret == -1: return -1
                                return 0

    commpro.Disconnect(hcommpro)


def completed_failure(empid):
    sqltxt = "UPDATE d_inbio_events SET completed = 2"
    if str(empid) != "": sqltxt += """ WHERE key = """ + str(empid)
    ret = sqlconns.sql_command(sqltxt)
    return ret


def inbio_events_into_list():
    sqltxt = "SELECT * FROM d_inbio_events"
    ret = sqlconns.sql_select_into_list(sqltxt)
    if ret == -1: return -1
    if len(ret) == 0: return 0
    return ret


#dont think this is used...must have been drunk
def get_inbio_events():
    sqltxt = "SELECT * FROM d_inbio_events"
    ret = sqlconns.sql_select_into_list(sqltxt)
    if ret == -1: return -1
    if len(ret) == 0: return 0
    return ret


def comm_success_date_time(terminal_id):
    sqltxt = """UPDATE tterminal SET poll_success = """ + f.get_sql_date(datetime.datetime.now(),
                                                                         "yyyy-mm-dd hh:mm:ss") + """ WHERE terminal_id = """ + str(
        terminal_id)
    ret = sqlconns.sql_command(sqltxt)
    return ret


def comm_failure_date_time(terminal_id):
    sqltxt = """UPDATE tterminal SET poll_failed = """ + f.get_sql_date(datetime.datetime.now(),
                                                                        "yyyy-mm-dd hh:mm:ss") + """ WHERE terminal_id = """ + str(
        terminal_id)
    ret = sqlconns.sql_command(sqltxt)
    return ret


def insert_transactions(poll_list, terminal_id):
    bool = True
    #skipping header and last line
    length = (len(poll_list) - 1)
    for index in range(length):
        if index != 0:
            list = poll_list[index].split(",")
            cardno = list[0]  #NA
            pin = list[1]
            verified = list[2]  #NA
            door_id = list[3]
            event = translate_event(list[4])
            #inoutstate = list[5]  #maybe NA - this is in the manual but i dont think we need it.
            date_and_time = f.convert_sec_to_sql_date(list[6])
            if SPOOL_TRANSACTION == 1:
                spool_log(cardno, pin, verified, door_id, event, date_and_time)
            if event != "0":
                ret = insert_sql_transaction(pin, date_and_time, event, door_id, terminal_id)
                if ret == -1:
                    return -1
                if ret < 0: bool = False
                #probably wupe em if bool is true
    return bool


def translate_event(event):
    #check our manual for for inbio codes and DP document for timeware flags for this dictionary
    #3 came up but we dont know how yet
    dict1 = {"0": '1', "14": '1', "16": '1', "17": '1', "20": '5', "21": '3', "22": '3', "23": '3', "24": '5',
             "29": '3', "33": '3', "35": '3', "202": '8', "220": '8', "221": '8'}
    try:
        timeware_event = dict1[event]
    except:
        timeware_event = "0"
    #timeware flags
    #1 open
    #3 denied
    #5 anti passback
    #8 push button
    return timeware_event


def insert_sql_transaction(empid, dte, event, door_id, terminal_id):
    terminal_id_2 = get_terminal_id(door_id, terminal_id)
#return 0 if no door found in software, preventative measure
    if terminal_id_2 == 0:
        return 0
    sqltxt = """IF (SELECT COUNT (*) FROM taccess_archive WHERE employee_id = """ + empid + """ AND date_and_time = """ + dte + """ AND flag = """ + event + """) =0
                    INSERT INTO taccess_archive (employee_id,terminal_id,date_and_time,flag) VALUES (""" + empid + """,""" + terminal_id_2 + """,""" + dte + """,""" + event + ")"""
    ret = sqlconns.sql_command(sqltxt)
    return ret


def get_terminal_id(door_id, terminal_id):
    sqltxt = """SELECT TOP 1 number from tterminal WHERE terminal_id = """ + str(terminal_id)
    ret = sqlconns.sql_select_single_field(sqltxt)
    if ret == -1:
        return -1
    terminal_num = int(ret) + (int(door_id) - 1)
    sqltxt = """SELECT TOP 1 terminal_id from tterminal WHERE number = """ + str(terminal_num)
    ret = sqlconns.sql_select_single_field(sqltxt)
#preparing for door not existing for whatever reason, do not know why, saw this in testing
    if ret==-1: return 0
    return ret


def ret_error(ip_address, ret, function):
    f.error_logging(APPNAME, "Connect failure to " + ip_address + "...(" + str(ret) + ")", ERROR_LOG, function)


def no_connection_error(ip_address):
    list = sqlconns.sql_select_into_list("SELECT TOP 1 value FROM d_inbio_misc WHERE property like 'LOG_COMMS_FAILURES'")
    print("log_comm_failure",list)
    if list == -1: return
    if len((list)) == 0: return
    if list[0][0] == "0": return
    f.error_logging(APPNAME, "Connect failure to " + ip_address + ".", COMM_ERROR,"")
    return

def inbio_started():
    list = sqlconns.sql_select_into_list("SELECT TOP 1 value FROM d_inbio_misc WHERE property like 'paused'")
    if list == -1: return -1
    if len((list)) == 0: return True
    if list[0][0] == "0": return True
    return False


def spool_log(cardno, pin, verified, door_id, event, date_and_time):
    try:
        e = open(gl.SPOOL_LOG, 'a')
        e.write(cardno + "," + pin + "," + verified + "," + door_id + "," + event + "," + date_and_time + """\n""")
    except:
        return


def get_start_time(dte_started, dte_activated):
    if dte_activated == None: return f.convert_sql_date(dte_started, "yyyymmdd")
    x = f.convert_sql_date(dte_activated, "yyyymmdd")
    y = f.convert_sql_date(dte_started, "yyyymmdd")
    if x >= y:
        return x
    else:
        return y


def get_end_time(dte):
    if dte == None: return "23000101"
    return f.convert_sql_date(dte, "yyyymmdd")


def get_door_id(term_id):
    if term_id % 100 == 1: return 1
    if term_id % 100 == 2: return 2
    if term_id % 100 == 3: return 4
    if term_id % 100 == 4: return 8
    return 0


def build_terminal_policy_list(data):
    data_list = data.split('\\r')
    #for index in range(len(data_list)):
    return data_list


def get_doors_from_ip(terminal_ip):
    door_list = []
    sql_text = "SELECT terminal_id,number from tterminal where ip_address like '%" + terminal_ip + "%'" + " AND configuration =" + gl.access_terminal_configuration
    door_list_list = sqlconns.sql_select_into_list(sql_text)
    if door_list_list == -1: return -1
    #turn list of lists into a list as there is only one field
    return door_list_list


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
    #main = main_loop()
    #main

