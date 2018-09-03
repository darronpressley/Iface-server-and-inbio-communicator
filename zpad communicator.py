APP_VERSION = '0.0.1'
APPNAME = "zpad_client"
'''Android Biopad integration with NTP
    terminal policies will be ignored, if you have a badge number and are an employee you can clock.
    only using localhost and default ports 4373 and 4372
'''
SERVER_STARTED = 0

import thriftpy
import inspect
import base64
import datetime
import time
import hashlib
import win32serviceutil
import win32service
import win32event
import threading
import asyncore
from thriftpy.rpc import make_client
from thriftpy.protocol.binary import TBinaryProtocolFactory
from thriftpy.transport import TBufferedTransportFactory
from thriftpy.transport import TFramedTransportFactory

import gl,sqlconns,functions as f,os,sys

f.error_logging(APPNAME, 'we are at the start', 'error_log', "")

thrift_file = gl.SCRIPT_ROOT+"zk.thrift"

f.error_logging(APPNAME, thrift_file, 'error_log', "")

try:
    zk_thrift = thriftpy.load("zk.thrift",
                                module_name="zk_thrift")
except Exception as e:
    f.error_logging(APPNAME, str(e), 'error_log',"reading thrift file")

COMM_ERROR = "communications_log"
ERROR_LOG =  "error_log"



class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "Zpad Communicator"
    _svc_display_name_ = "Zpad Communicator"
    _svc_description_ = "Zpad Communicator from North Time and Data"

    def __init__(self,args):
         win32serviceutil.ServiceFramework.__init__(self, args)
         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        global SERVER_STARTED
        SERVER_STARTED = 0
        log_exit()
        time.sleep(5)
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
        county = 0

        global SERVER_STARTED
        while True:
            if myStatusThread.isAlive():
                county += 1
                if county == 10:
                    dte = str(datetime.datetime.now())
                    e = open("c:/temp/1log.txt", 'a')
                    e.write(dte + """\n""")
                    e.close()
                    county = 0
                if SERVER_STARTED==0:
                    if set_env()==True:
                        if version_check()==True:
                            try:
                                init_client()
                                log_initialise()
                                SERVER_STARTED = 1
                            except Exception as e:
                                f.error_logging(APPNAME, str(e), "error_log", "")
                else:
                    pass
            else:
                break
            time.sleep(1)


def log_initialise():
    f.error_logging(APPNAME, "Service started.", "error_log","")

def log_exit():
    f.error_logging(APPNAME, "iface clean exit", "error_log","")

def time_ms():
   return (int(time.time()) * 1000)

def get_swipe_from_ms(ms):
    x = int(ms)
    x = x / 1000.00
    dte = datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M')
    return dte

def att_data(data):
    list = str.split(data,';')
    #for n in range(len(list)):
       #print('testing att list',list[n])
    empid = ""
    clock_num = ""
    dte = ""
    event = ""
    status = ""
    empid = str.rsplit(list[7],"=")[1]
    clock_num = str.rsplit(list[9],"=")[1]
    dte = get_swipe_from_ms(str.rsplit(list[2],"=")[1])
    return empid, clock_num, dte

def push_command_delete(client,pushdata):
    try:
        client.pushdata = zk_thrift.ZKProtoSyncOperation(id=-1, action=zk_thrift.ZKProtoSyncAction.DELETE,
                                                         timestamp=time_ms(), data=pushdata,
                                                         compressed=None)
        opsToInsert = []
        opsToInsert.append(client.pushdata)
        client.push(opsToInsert)
    except Exception as e:
        f.error_logging(APPNAME, str(e), 'error_log', str(inspect.stack()[0][3]))
        return -1

def push_command_insert(client,pushdata):
    try:
        client.pushdata = zk_thrift.ZKProtoSyncOperation(id=-1, action=zk_thrift.ZKProtoSyncAction.INSERT,
                                                         timestamp=time_ms(), data=pushdata,
                                                         compressed=None)
        opsToInsert = []
        opsToInsert.append(client.pushdata)
        client.push(opsToInsert)
    except Exception as e:
        f.error_logging(APPNAME,str(e),'error_log',str(inspect.stack()[0][3]))
        return -1

def set_admin(client,empid,pwd):
    try:
        hash_object = hashlib.md5(pwd.encode())
        pwd = hash_object.hexdigest()
        pushdata = "table=employee_login;id_employee="+str(empid)+";id_login=1;id_multi_value=0;id_action_group=1;value=" + pwd + ";salt=;"
        ret = push_command_insert(client, pushdata)
        if ret == -1: return -1
        for n in range(4):
            role_id = str(n+1)
            pushdata = "table=role2entity;id_role=" + role_id + ";id_entity="+str(empid)
            ret = push_command_insert(client, pushdata)
            if ret==-1:return -1
        return
    except Exception as e:
        f.error_logging(APPNAME, str(e), 'error_log', str(inspect.stack()[0][3]))
        return -1

def process_pull_data(ops):
    ret = 0
    listy = []
    last_record = False
    if 'last=True' in str(ops): last_record = True
    ops = str.replace(str(ops), 'ZKProtoSyncOperations(operations=[ZKProtoSyncOperation', '')
    ops = str.replace(str(ops), ', last=False)', '')
    ops = str.replace(str(ops), ', last=True)', '')
    xx = ops
    xx = str.replace(xx, ']', '')
    xx = str.replace(xx, '(', '')
    listy = str.split(xx, ', ZKProtoSyncOperation')
    for n in range(len(listy)):
        if 'attendance_log' in str(listy[n]):
            listy[n] + '\n'
            empid, clock_num, dte = att_data(listy[n])
            if empid !="":
                ret = insert_booking(empid, clock_num, dte)
                if ret==-1: return -1
    return last_record

def insert_booking(empid, clock_num, dte):
    #if person not found flag for update and dont save
    ret = sqlconns.sql_select_single_field('SELECT COUNT(*) as FOO from temployee WHERE employee_id = ' + str(empid))
    if sqlconns.sql_select_single_field('SELECT COUNT(*) as FOO from temployee WHERE employee_id = ' + str(empid)) == "0":
        ret = sqlconns.sql_command('INSERT into d_zpad_events (employee_id) VALUES (?)',empid)
    terminal_id = sqlconns.sql_select_single_field("SELECT TOP 1 terminal_id FROM tterminal WHERE number = " + clock_num)
    if terminal_id == "": terminal_id = "0"
    if terminal_id ==-1:return -1
    if terminal_id !="0":
        ret = sqlconns.sql_command("UPDATE tterminal SET poll_success = ? WHERE number = ?",datetime.datetime.now(),clock_num)
        if ret==-1: return
    booking = "'"+dte+"'"
    flag = 0
    tx = "INSERT INTO twork_unprocessed (employee_id,terminal_id,date_and_time,[type],flag,[key],memo,authorisation,authorisation_finalised,source)" \
                 " VALUES (" + str(empid) + "," + str(terminal_id) + "," + booking + ",1000," + str(flag) + ",0,'',3,1,0)"
    ret = sqlconns.sql_command(tx)
    if ret == -1: return -1
    tx = tx.replace("twork_unprocessed", "twork_unprocessed_archive")
    ret = sqlconns.sql_command(tx)
    if ret == -1: return -1
    return 0


def del_empid(client,empid):
    try:
        pushdata = 'table=attendance_log;id_employee='+str(empid)
        ret = push_command_delete(client, pushdata)
        pushdata = 'table=employee_login_combination;id_employee='+str(empid)
        ret = push_command_delete(client, pushdata)
        pushdata = 'table=role2entity;id_entity='+str(empid)
        ret = push_command_delete(client, pushdata)
        pushdata = "table=employee_login;id_employee="+str(empid)
        ret = push_command_delete(client, pushdata)
        pushdata = "table=employee;_id="+str(empid)
        ret = push_command_delete(client, pushdata)
        pushdata = "table=entity;_id="+str(empid)
        ret = push_command_delete(client, pushdata)
        return 0
    except ConnectionResetError as e:
        f.error_logging(APPNAME, str(e), 'error_log', str(inspect.stack()[0][3]))
        return -1

def insert_empid(client, empid, security_pin, first_name, last_name, badge):
    try:
        emp = str(empid)
        pushdata = "table=entity;_id="+emp+";enabled=1"
        ret = push_command_insert(client, pushdata)
        if ret == -1: return -1
        pushdata = "table=employee;_id="+emp+";birth_date=;pin="+str(emp)+";first_name="+first_name+";last_name="+last_name+";address=;phone=;email=;national_id=;gender=0;photo="
        ret = push_command_insert(client, pushdata)
        if ret == -1: return -1
        if badge>0:
            cardno = hex(badge)
            cardno = cardno.upper()
            cardno = cardno.replace('0X',"")
            pushdata = "table=employee_login;id_employee="+emp+";id_login=3;id_multi_value=1;id_action_group=1;value="+cardno+";salt=;"
            ret = push_command_insert(client, pushdata)
            if ret == -1: return -1
            # login combination
            pushdata = "table=employee_login_combination;id_employee="+emp+";login_combination=3;"
            ret = push_command_insert(client, pushdata)
            if ret == -1: return -1
            pushdata = "table=employee_login_combination;id_employee="+emp+";login_combination=4;"
            ret = push_command_insert(client, pushdata)
            if ret == -1: return -1
        if security_pin != '':
            ret = set_admin(client,emp,security_pin)
            if ret ==-1: return -1
        return 0
    except ConnectionResetError as e:
        f.error_logging(APPNAME, str(e), 'error_log', str(inspect.stack()[0][3]))
        return -1

def pull_data(client):
    try:
        # pull data and process clocking times
        no_more_ops = False
        while no_more_ops == False:
            ops = client.pull()
            no_more_ops = process_pull_data(ops)
            if no_more_ops ==-1: return -1
            client.ackOperation = zk_thrift.ZKProtoSyncOperation(id=-1, action=zk_thrift.ZKProtoSyncAction.ACKNOWLEDGE, timestamp=time_ms(),
                                                   data=None, compressed=None)
            opsToPush = []
            opsToPush.append(client.ackOperation)
        try:
            client.push(opsToPush)
        except Exception as e:
            return -1
        return 0
    except ConnectionResetError as e:
        f.error_logging(APPNAME, str(e), 'error_log', str(inspect.stack()[0][3]))
        return -1

def build_zpad_command_list(client):
    try:
        tx = "SELECT employee_id,[index] from d_zpad_events"
        list_to_update = sqlconns.sql_select_into_list(tx)
        if list_to_update==-1: return -1
        for n in range(len(list_to_update)):
            tx = "SELECT TOP 1 temployee.employee_id,security_pin,first_name,last_name,badge, exclude_from_calculation FROM temployee LEFT OUTER JOIN" \
                 " temployee_status ON temployee.employee_status_id = temployee_status.employee_status_id" \
                " WHERE employee_id = " + str(list_to_update[n][0])
            emp_details = sqlconns.sql_select_into_list(tx)
            if emp_details ==-1: return -1
            if len(emp_details) == 0:
                ret = del_empid(client,str(list_to_update[n][0]))
                ret = sqlconns.sql_command("DELETE FROM d_zpad_events WHERE employee_id = ?", list_to_update[n][0])
                if ret == 1: return -1
            for y in range(len(emp_details)):
                empid = int(emp_details[y][0])
                if emp_details[y][1] != None:
                    security_pin = str(emp_details[y][1])
                else:
                    security_pin = ''
                first_name = str(emp_details[y][2])
                last_name = str(emp_details[y][3])
                if emp_details[y][4] != None:
                    badge = int(emp_details[y][4])
                else:
                    badge = 0
                exclude_from_calculation = str(emp_details[y][5])
                ret = del_empid(client, empid)
                if exclude_from_calculation=="0":
                    ret = insert_empid(client, empid, security_pin, first_name, last_name, badge)
                if ret == -1:
                    return -1
                else:
                    ret = sqlconns.sql_command("DELETE FROM d_zpad_events WHERE employee_id = ?",empid)
                    if ret==1: return -1
    except ConnectionResetError as e:
        f.error_logging(APPNAME, str(e), 'error_log', str(inspect.stack()[0][3]))
        return -1

def main():
    waiting_for_server = False
    while waiting_for_server == False:
        if SERVER_STARTED == 0 :return 1
        try:
            client = make_client(zk_thrift.ZKProtoSyncService,
                            '127.0.0.1', 4372)
            waiting_for_server = True
        except Exception as e:
            waiting_for_server = False
            time.sleep(10)
    protocolVersion = 1
    clientUUID = 12345678
    maxOperations = 10000
    client.openInfo = zk_thrift.ZKProtoSyncOpenInfo(protocolVersion, clientUUID,
                                                             "ZKProtoClient", maxOperations, None,time_ms())
    waiting_for_authorise = False
    while waiting_for_authorise == False:
        if SERVER_STARTED == 0 :return 1
        try:
            client.open(client.openInfo)
            waiting_for_authorise = True
        except Exception as e:
            waiting_for_authorise = False
            if 'Client not authorized' in str(e):
                #client.close()
                time.sleep(10)

    while SERVER_STARTED == 1:
        #pull
        ret = pull_data(client)
        if ret==-1:
            try:
                client.close()
                return -1
            except Exception as e:
                return -1
        #push
        ret = build_zpad_command_list(client)
        if ret==-1:
            try:
                client.closE()
            except Exception as e:
                return -1
        time.sleep(1)
    return 1

def init_client():
    while SERVER_STARTED ==1:
        f.error_logging(APPNAME, "In Init client.", "error_log", "init_client")
        #if we get back here we just need to reloop
        #should only return here when there is a problem but we want to start again none the less
        ret = main()

def set_env():
    if os.path.isfile(gl.SCRIPT_ROOT + 'database.ini'):
        if sqlconns.readsql_connection_timeware_main_6() == 0:
            f.error_logging(APPNAME, "Error reading database.ini file.", "error_log", "")
            return False
        elif sqlconns.readsql_connection_timeware_main_6() == 1:
            test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
            if test_comms == 0:
                f.error_logging(APPNAME, "Error connecting to SQL server.", "error_log", "")
                return False
            return True
    else:
        f.error_logging(APPNAME, "Error reading database.ini file.", "error_log", "")
        return False

def version_check():
    if os.path.isfile(gl.LICENSE_TXT):
        fob=open(gl.LICENSE_TXT, "r")
        listme = fob.readlines()
        fob.close()
        try:
            version_year = sqlconns.decrypt_with_key(listme[0])
            ret = sqlconns.sql_select_single_field("SELECT TOP 1 [data] FROM tversion WHERE [property] like 'database version'")
            if ret==-1:return False
            database_version = str.split(ret,'.')
            if int(version_year) >= int('20'+database_version[0]):
                return True
            else:
                f.error_logging(APPNAME, "Version is out of date....cannot start.", "error_log","")
                return False
        except Exception as e:
            return False
    else:
        f.error_logging(APPNAME, "Error reading license.txt file.", "error_log","")
        return False

def return_version():
    if os.path.isfile(gl.LICENSE_TXT):
        fob=open(gl.LICENSE_TXT, "r")
        listme = fob.readlines()
        fob.close()
        try:
            version_year = sqlconns.decrypt_with_key(listme[0])
            return version_year
        except Exception as e:
            return False
    else:
        f.error_logging(APPNAME, "Error reading license.txt file.", "error_log","")
        return False

def test_main():
    print('started')
    if set_env() == True:
        if version_check() == True:
            global SERVER_STARTED
            SERVER_STARTED = 1
            print('SERVER STARTED = ',SERVER_STARTED)
            init_client()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
    #test_main()