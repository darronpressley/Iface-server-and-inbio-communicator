#IFACE TORNADO version
#Author Darron Pressley
#there is a lot of commented out code in this project
#this is to allow quickish switching between running this as a service and running as a application
import decimal
import sys
import os
import time
from datetime import datetime,timedelta
from ctypes import *

import tornado.ioloop
import tornado.web
import tornado.httputil
import logging

import win32service
import win32event
import threading
import asyncore
import http.server
import base64

import win32serviceutil

import functions as f
import sqlconns
import gl

SERVER_STARTED = 0

APPNAME = "IFACSERVER"
APP_VERSION = "2015.0.3.4"
# log file names
COMM_ERROR = "communications_log"
ERROR_LOG =  "error_log"
#oldtime is true by default for safety
OLD_TIME = True
INBIO_USED = False
FINGER_DELETION_MINS = 10
FUNCTION_KEYS = False
IFACE_FUNCTION_KEYS = False

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print('yoyoyoyo')
        print(self.request.uri)
        self.write("Hello, world")

class IclockHandler(tornado.web.RequestHandler):
    def get(self):
        list = self.request.uri.split("?SN=")
        list2 = list[1].split("&")
        sn = list2[0]
        ret = sqlconns.sql_command("UPDATE tterminal SET poll_success = ? WHERE ip_address = ?",datetime.now(),sn)
        if ret==-1: return
        self.set_status(200)
        self.set_header("content-type","text/plain")
        self.set_header("date", date_time_string(sn))
        #power on send stamps and options
        power_on_getrequest = build_power_on_get_request(sn)
        if power_on_getrequest == "": return
        self.write(power_on_getrequest)

    def post(self):
        print(str(self.request.uri))
        print(str(self.request.body))
        terminal_id, configuration, sn, table_type, stamp = get_terminal_id (self.request.uri)
        if terminal_id == -1: return
        postvars = self.request.body
        postvars = postvars.decode("utf-8")
        list = postvars.split("\n")
        print(list)
        if table_type =="": return
        if table_type == "OPERLOG":
            for index in range(len(list)):
                if "USERPIC" in list[index]:
                    ret = save_user_photo(list[index],terminal_id)
                    if ret==-1: return -1.
                if "FACE PIN" in list[index]:
                    ret = save_user_face(list[index],terminal_id)
                    if ret==-1: return -1
                if "FP PIN" in list[index]:
                    ret = save_user_finger(list[index],terminal_id)
                    if ret==-1: return -1
                if "OPLOG" in list[index]:
                    ret = save_op_log(list[index],terminal_id,sn)
                    if ret==-1: return -1
            ret = save_op_stamp(stamp,terminal_id,sn)
            if ret==-1: return -1
        if table_type == "ATTLOG":
            for index in range(len(list)):
                ret = insert_booking(str(list[index]),terminal_id,sn,configuration,stamp)
                if ret == -1: return
        self.set_status(200)
        self.set_header("content-type","text/plain")
        self.set_header("date", date_time_string(sn))
        self.write("OK")

class IclockDevicecmdHandler(tornado.web.RequestHandler):
    def post(self):
        sn = self.request.uri.replace("/iclock/devicecmd?SN=","")
        terminal_id = get_terminal_id_from_sn(sn)
        postvars = self.request.body
        postvars = postvars.decode("utf-8")
        cmd_list = postvars.split("\n")
        for index in range(len(cmd_list)):
            commands = cmd_list[index].split("&")
            if len(commands)==3:
                commands[0] = (commands[0].replace("ID=ID",""))
                id = int(commands[0])
                returned = int(commands[1].replace("Return=",""))
                tx = "UPDATE d_iface_commands SET completed_flag = 1, completed_date = ?,returned = 0 WHERE iface_command_id = ?"
                ret = sqlconns.sql_command(tx,datetime.now(),id)
                if ret==-1: return
        self.set_status(200)
        self.set_header("content-type","text/plain")
        self.set_header("date", date_time_string(sn))
        self.write("OK")

class IclockGetrequestHandler(tornado.web.RequestHandler):
    def get(self):
        print(str(self.request.uri))
        list = self.request.uri.split("?SN=")
        list2 = list[1].split("&")
        sn = list2[0]
        self.set_status(200)
        self.set_header("content-type","text/plain")
        self.set_header("date", date_time_string(sn))
        data_list = get_commands_list(sn)
        if data_list==-1: return
        counter = 0
        reboot=0
        clear_data=0
        data=""
        for index in range(len(data_list)):
            if data_list[index][1] == "REBOOT":
                reboot = 1
            elif data_list[index][1] == "CLEAR DATA":
                clear_data = 1
            else:
                counter+=1
                if sys.getsizeof(data+("C:ID"+str(data_list[index][0])+":"+data_list[index][1]+"\r\n"))>39000:
                    break
                data = data + "C:ID"+str(data_list[index][0])+":"+data_list[index][1]+"\r\n"
            ret = update_commands_to_sent_status(data_list[index][0])
            if ret==-1:return
        if data!="":
            self.write(data)
            return
        if clear_data==1:
            self.write("C:ID"+str(data_list[index][0])+":CLEAR DATA\r\n")
            self.write(data)
        if reboot==1:
            self.write("C:ID"+str(data_list[index][0])+":REBOOT\r\n")
        return


class TestPage(tornado.web.RequestHandler):
    def get(self):
        print('tested')
        if OLD_TIME == True:
            old_time_status = 'Oldtime option = ON.<br>'
        else:
            old_time_status = 'Oldtime option = OFF.<br>'
        if gl.face_to_personnel == True:
            photo_save_status = 'Save face photo to personnel = ON.<br>'
        else:
            photo_save_status = 'Save face photo to personnel = OFF.<br>'
        terminal_configuration_status = "Attendance terminals = configuration " + str(ATTENDANCE_TERMINAL) + '.<br>'\
                                        "Access terminals = configuration " + str(ACCESS_TERMINAL) + '.<br>'
        data = ("<HTML>Ifaceserver from " + DISTRIBUTOR + " is broadcasting.<br>Iface Server Version = " \
                                               + APP_VERSION + "<br><br>" \
                                                + "SQL Instance: " + str(sqlconns.sql_select_single_field('SELECT @@ServerName')) + "<br><br>" \
                                                + "normaltime = " + str(date_time_string_test('normaltime'))
                                                + ".<br>****oldtime = " + str(date_time_string_test('oldtime')) + '.<br>' \
                                                + old_time_status + terminal_configuration_status + photo_save_status \
                                                + 'Fingerprint delete old scan set to ' + str(FINGER_DELETION_MINS) +' mins.' + '<br>' \
                                                + 'Using Inbio Communication (ensure inbio tables are setup)= ' + str(INBIO_USED) + '.<br><br>' \
                                                + 'S680 Function keys = ' + str(FUNCTION_KEYS) + '.<br>' \
                                                + 'Iface Function keys = ' + str(IFACE_FUNCTION_KEYS) + '.<br><br>' \
                                                + 'License Year = ' + str(return_version()) + '<br><br>'\
                                               + get_terminal_status_list() +'</HTML>')
        self.write(data)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/test",TestPage),
        (r"/iclock/cdata",IclockHandler),
        (r"/iclock/getrequest",IclockGetrequestHandler),
        (r"/iclock/devicecmd",IclockDevicecmdHandler),
    ])

#class MyHandler(http.server.BaseHTTPRequestHandler):
class MyHandler(object):
    def do_GET(self):
        try:
            self.serial_number=""
            if not "?SN=" in self.path:
                if "test" in self.path:
                    if OLD_TIME == True:
                        old_time_status = 'Oldtime option = ON.<br>'
                    else:
                        old_time_status = 'Oldtime option = OFF.<br>'
                    if gl.face_to_personnel == True:
                        photo_save_status = 'Save face photo to personnel = ON.<br>'
                    else:
                        photo_save_status = 'Save face photo to personnel = OFF.<br>'
                    terminal_configuration_status = "Attendance terminals = configuration " + str(ATTENDANCE_TERMINAL) + '.<br>'\
                                                    "Access terminals = configuration " + str(ACCESS_TERMINAL) + '.<br>'
                    data = create_string_buffer(str.encode("<HTML>Ifaceserver from " + DISTRIBUTOR + " is broadcasting.<br>Version = " \
                                                           + APP_VERSION + "<br>normaltime = " + str(self.date_time_string_test('normaltime'))
                                                            + ".<br>****oldtime = " + str(self.date_time_string_test('oldtime')) + '.<br>' \
                                                            + old_time_status + terminal_configuration_status + photo_save_status + '<br>'
                                                            + 'License Year = ' + str(return_version()) + '<br><br>'
                                                           + str(get_terminal_status_list()) +'</HTML>'))
                    self.send_response(200)
                    self.do_headers()
                    self.wfile.write(data)
                return
            list = self.path.split("?SN=")
            list2 = list[1].split("&")
            sn = list2[0]
            self.serial_number = sn
            ret = sqlconns.sql_command("UPDATE tterminal SET poll_success = ? WHERE ip_address = ?",datetime.now(),sn)
            if ret==-1: return
            if "cdata" in self.path:
            #power on send stamps and options
                power_on_getrequest = create_string_buffer(str.encode(build_power_on_get_request(sn)))
                self.send_response(200)
                self.do_headers()
                if power_on_getrequest == "": return
                self.wfile.write(power_on_getrequest)
                return
            elif "getrequest" in self.path:
                #send commands from command list
                self.send_response(200)
                self.do_headers()
                #remember to change to only send unsent stuff
                data_list = get_commands_list(sn)
                if data_list==-1: return
                counter = 0
                reboot=0
                clear_data=0
                data=""
                for index in range(len(data_list)):
                    if data_list[index][1] == "REBOOT":
                        reboot = 1
                    elif data_list[index][1] == "CLEAR DATA":
                        clear_data = 1
                    else:
                        counter+=1
                        if sys.getsizeof(data+("C:ID"+str(data_list[index][0])+":"+data_list[index][1]+"\r\n"))>39000:
                            break
                        data = data + "C:ID"+str(data_list[index][0])+":"+data_list[index][1]+"\r\n"
                    ret = update_commands_to_sent_status(data_list[index][0])
                    if ret==-1:return
                if data!="":
                    data = create_string_buffer(str.encode(data))
                    self.wfile.write(data)
                    return
                if clear_data==1:
                    data = create_string_buffer(str.encode("C:ID"+str(data_list[index][0])+":CLEAR DATA\r\n"))
                    self.wfile.write(data)
                if reboot==1:
                    data = create_string_buffer(str.encode("C:ID"+str(data_list[index][0])+":REBOOT\r\n"))
                    self.wfile.write(data)
                return
                return
        except Exception as e:
            print(e)

    def do_headers(self):
        self.send_header("Content-type:","text/plain")
        self.send_header('Date', self.date_time_string())
        self.end_headers()

    def do_POST(self):
        try:
            if "devicecmd" in self.path:
                sn = self.path.replace("/iclock/devicecmd?SN=","")
                self.serial_number = sn
                #this line doesnt seem to do anything but it does so never remove it
                terminal_id = get_terminal_id_from_sn(sn)
                length = int(self.headers['content-length'])
                postvars = (self.rfile.read(length))
                postvars = postvars.decode("utf-8")
                cmd_list = postvars.split("\n")
                for index in range(len(cmd_list)):
                    commands = cmd_list[index].split("&")
                    if len(commands)==3:
                        commands[0] = (commands[0].replace("ID=ID",""))
                        id = int(commands[0])
                        returned = int(commands[1].replace("Return=",""))
                        tx = "UPDATE d_iface_commands SET completed_flag = 1, completed_date = ?,returned = 0 WHERE iface_command_id = ?"
                        ret = sqlconns.sql_command(tx,datetime.now(),id)
                        if ret==-1: return
                self.send_response(200)
                self.do_headers()
                xx = create_string_buffer(str.encode("OK"))
                self.wfile.write(xx)
                return
            terminal_id, configuration, sn, table_type, stamp = get_terminal_id (self.path)
            self.serial_number = sn
            if terminal_id == -1: return
            length = int(self.headers['content-length'])
            postvars = (self.rfile.read(length))
            postvars = postvars.decode("utf-8")
            list = postvars.split("\n")
            if table_type =="": return
            if table_type == "OPERLOG":
                for index in range(len(list)):
                    if "USERPIC" in list[index]:
                        ret = save_user_photo(list[index],terminal_id)
                        if ret==-1: return -1.
                    if "FACE PIN" in list[index]:
                        ret = save_user_face(list[index],terminal_id)
                        if ret==-1: return -1
                    if "FP PIN" in list[index]:
                        ret = save_user_finger(list[index],terminal_id)
                        if ret==-1: return -1
                    if "OPLOG" in list[index]:
                        ret = save_op_log(list[index],terminal_id,sn)
                        if ret==-1: return -1
                ret = save_op_stamp(stamp,terminal_id,sn)
                if ret==-1: return -1
            if table_type == "ATTLOG":
                for index in range(len(list)):
                    ret = insert_booking(str(list[index]),terminal_id,sn,configuration,stamp)
                    if ret == -1: return
            self.send_response(200)
            self.do_headers()
            xx = create_string_buffer(str.encode("OK"))
            self.wfile.write(xx)
            return
        except Exception as e:
            print(e)

    def log_request(self, code=None, size=None):
        print("in log_request")
        return

    def log_message(self, format, *args):
        print("in log_message")
        print("format = " + str(format))
        print("args = " + str(args))
        return

    def log_error(self, format, *args):
        print("in log_error")
        print("format = " + str(format))
        print("args = " + str(args))
        return

    def date_time_string(self):
        now = time.time()
        year, month, day, hh, mm, ss, wd, y, z = time.localtime(now)
        #there was a space between first , and %02d
        s = "%s,%02d %3s %4d %02d:%02d:%02d GMT" % (
        self.weekdayname[wd],
        day, self.monthname[month], year,hh, mm, ss)
        if self.serial_number=='': return s
        #bug out if oldtime is false
        if OLD_TIME == False: return s
        tx = sqlconns.sql_select_single_field("SELECT TOP 1 notepad from tterminal WHERE ip_address = '" + self.serial_number + "'")
        if 'oldtime' in str(tx):
            dte = datetime.now()
            dte = dte - timedelta(hours = 1)
            now = time.mktime(dte.timetuple())
            year, month, day, hh, mm, ss, wd, y, z = time.localtime(now)
            s = "%s,%02d %3s %4d %02d:%02d:%02d GMT" % (
            self.weekdayname[wd],
            day, self.monthname[month], year,hh, mm, ss)
        return s

    def date_time_string_test(self,tx):
    #this is used in the slash test
        now = time.time()
        year, month, day, hh, mm, ss, wd, y, z = time.localtime(now)
        s = "%s,%02d %3s %4d %02d:%02d:%02d GMT" % (
        self.weekdayname[wd],
        day, self.monthname[month], year,hh, mm, ss)
        if 'oldtime' in str(tx):
            dte = datetime.now()
            dte = dte - timedelta(hours = 1)
            now = time.mktime(dte.timetuple())
            year, month, day, hh, mm, ss, wd, y, z = time.localtime(now)
            #there was a space between first , and %02d
            s = "%s,%02d %3s %4d %02d:%02d:%02d GMT" % (
            self.weekdayname[wd],
            day, self.monthname[month], year,hh, mm, ss)
        return s

def get_terminal_status_list():
    terminal_list = sqlconns.sql_select_into_list('SELECT description, ip_address, configuration,poll_success FROM tterminal WHERE \
                                        configuration in (' + str(ACCESS_TERMINAL) + ',' + str(ATTENDANCE_TERMINAL) + ')'\
                                        'ORDER BY configuration, description')
    if terminal_list==-1: return ""
    tx = ""
    for index in range(len(terminal_list)):
        terminal_type = ""
        if terminal_list[index][2] == 4: terminal_type = 'Access Terminal'
        if terminal_list[index][2] == 10: terminal_type = 'ZK Terminal'
        if terminal_list[index][2] == 8: terminal_type = 'Attendance Terminal'
        if terminal_list[index][2] == 5: terminal_type = 'Hand Punch'
        if terminal_list[index][2] == 14: terminal_type = 'Fire Panel'
        if str(terminal_list[index][3]) == "None":
            tx += terminal_list[index][1] + ' --- ' + 'No polling received.' + ' --- ' + str(terminal_list[index][0]) + ' --- ' + terminal_type
        else:
            tx += terminal_list[index][1] + ' --- ' + str(f.convert_sql_date(terminal_list[index][3],'dd/mm/yyyy hh:mm')) + ' --- ' + str(terminal_list[index][0]) + ' --- ' + terminal_type
        tx += '<br>'
    return tx

class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "ifaceserver"
    _svc_display_name_ = "ifaceserver"
    _svc_description_ = "ifaceserver from North Time and Data"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        asyncoreThread = threading.Thread(target=asyncore.loop, kwargs={'timeout': 1})
        asyncoreThread.start()
        myStatusThread = threading.Thread(target=win32event.WaitForSingleObject,
                                          args=(self.hWaitStop, win32event.INFINITE))
        myStatusThread.start()

        log_initialise()
        global SERVER_STARTED
        while True:
            if myStatusThread.isAlive():
                if SERVER_STARTED==0:
                    if set_env()==True:
                        if version_check()==True:
                            self.app = make_app()
                            self.app.listen(gl.server_port)
                            SERVER_STARTED = 1
                            #logging.getLogger('tornado.access').disabled = True
                            try:
                                tornado.ioloop.IOLoop.current().start()
                                SERVER_STARTED = 1
                            except Exception as e:

                                tornado.ioloop.IOLoop.current().stop()
                else:
                    pass
            else:
                break
            time.sleep(1)

    def SvcStop(self):
        tornado.ioloop.IOLoop.current().stop()
        log_exit()
        time.sleep(3)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

def date_time_string(serial_number):
    dte = datetime.now()
    if OLD_TIME == True:
        tx = sqlconns.sql_select_single_field("SELECT TOP 1 notepad from tterminal WHERE ip_address = '" + serial_number + "'")
        if 'oldtime' in str(tx):
            dte = dte - timedelta(hours = 1)
    now = time.mktime(dte.timetuple())
    year, month, day, hh, mm, ss, wd, y, z = time.localtime(now)
    s = "%s,%02d %3s %4d %02d:%02d:%02d GMT" % (
        dte.strftime('%a'),
        day, dte.strftime('%b'), year,hh, mm, ss)
    return s

def date_time_string_test(tx):
#this is used in the slash test
    dte = datetime.now()
    if 'oldtime' in str(tx):
        dte = dte - timedelta(hours = 1)
    now = time.mktime(dte.timetuple())
    year, month, day, hh, mm, ss, wd, y, z = time.localtime(now)
    s = "%s,%02d %3s %4d %02d:%02d:%02d GMT" % (
        dte.strftime('%a'),
        day, dte.strftime('%b'), year,hh, mm, ss)
    return s

def log_initialise():
    f.error_logging(APPNAME, "server started", "error_log","")

def log_exit():
    f.error_logging(APPNAME, "iface clean exit", "error_log","")

def log_arg(tx):
    #delete when not needed
    f.error_logging(APPNAME, tx, "error_log","")

def update_commands_to_sent_status(id):

    date_now = f.get_sql_date(datetime.now(),"yyyy-mm-dd hh:mm:ss")
    tx = "UPDATE d_iface_commands SET sent=1,sent_date="+date_now+"WHERE iface_command_id="+str(id)
    sqlconns.sql_command(tx)

def get_commands_list(sn):
    terminal_id = sqlconns.sql_select_single_field("SELECT TOP 1 terminal_id FROM tterminal WHERE ip_address = '" + sn+"'")
    if terminal_id == "": return -1
    if int(terminal_id) > 0:
        data_list = sqlconns.sql_select_into_list("SELECT top 50 iface_command_id,command FROM d_iface_commands where sent <> 1 and terminal_id ="+terminal_id+"ORDER BY iface_command_id")
        if data_list==-1: return -1
        return data_list
    else:
        return -1

def save_op_stamp(stamp,terminal_id,sn):
    date_now = f.get_sql_date(datetime.now(),"yyyy-mm-dd hh:mm:ss")
    tx = "UPDATE d_iface_stamps SET stamp = " + stamp + ",date_added = " + date_now  + ",sn = '" + sn + "' WHERE table_name like 'op_stamp' AND terminal_id = " + str(terminal_id) + ""\
                " IF @@ROWCOUNT=0" \
                " INSERT INTO d_iface_stamps(table_name,stamp,terminal_id,date_added,sn) VALUES ('op_stamp','" + stamp + "','" + str(terminal_id) + "'," + date_now + ",'" + sn + "')"
    ret = sqlconns.sql_command(tx)
    if ret==-1: return -1
    return

def save_op_log(xx,terminal_id,sn):
    list = xx.split("\t")
    if list[0] == "OPLOG 3":
        dte = list[2]
        #push button
        if list[3] == "53":
            tx = "INSERT INTO taccess_archive (user_id,employee_id,terminal_id,date_and_time,flag,badge) VALUES (0,0,?,?,?,0)"
            ret = sqlconns.sql_command(tx,terminal_id,dte,8)
            if ret==-1: return -1
    return

def save_user_face(xx,terminal_id):
    list = xx.split("\t")
    user_id = list[0].replace("FACE PIN=","")
    if user_id=="":return 0
    fid = list[1].replace("FID=","")
    size = list[2].replace("SIZE=","")
    valid = list[3].replace("VALID=","")
    tmp = list[4].replace("TMP=","")
    date_now = f.get_sql_date(datetime.now(),"yyyy-mm-dd hh:mm:ss")
    tx = "UPDATE d_iface_tmp SET size = '" + size + "',[valid]="+valid+", [tmp]='" + tmp + "',date_added="+date_now+",terminal_id="+str(terminal_id)+" WHERE employee_id =" + user_id + " AND fid="+fid+"" \
                " IF @@ROWCOUNT=0" \
                " INSERT INTO d_iface_tmp(employee_id,size,tmp,date_added,[valid],fid,terminal_id) VALUES ('"+user_id+"','"+size+"','"+tmp+"',"+date_now+","+valid+","+fid+","+str(terminal_id)+")"
    ret = sqlconns.sql_command(tx)
    if ret==-1: return ret
    #if fid = 11 then check recently got 12 from this terminal that are new and put entry into tevent_update AND clear new flag
    if fid=="11":
        ret = update_tevent_update(user_id)
    return ret

def save_user_finger(xx,terminal_id):
    list = xx.split("\t")
    user_id = list[0].replace("FP PIN=","")
    if user_id=="":return 0
    fid = list[1].replace("FID=","")
    size = list[2].replace("Size=","")
    valid = list[3].replace("Valid=","")
    tmp = list[4].replace("TMP=","")
    #clear old templates
    tx = "DELETE from d_iface_finger WHERE employee_id = " + str(user_id) + " AND date_added < dateadd(minute,-" + str(FINGER_DELETION_MINS) + ",getdate())"
    sqlconns.sql_command(tx)
    date_now = f.get_sql_date(datetime.now(),"yyyy-mm-dd hh:mm:ss")
    tx = "UPDATE d_iface_finger SET size = '" + size + "',[valid]="+valid+", [tmp]='" + tmp + "',date_added="+date_now+",terminal_id="+str(terminal_id)+" WHERE employee_id =" + user_id + " AND fid="+fid+"" \
                " IF @@ROWCOUNT=0" \
                " INSERT INTO d_iface_finger(employee_id,size,tmp,date_added,[valid],fid,terminal_id) VALUES ('"+user_id+"','"+size+"','"+tmp+"',"+date_now+","+valid+","+fid+","+str(terminal_id)+")"
    ret = sqlconns.sql_command(tx)
    if ret==-1: return ret
    ret = update_tevent_update(user_id)
    return ret

def update_tevent_update(empid):
    tx = "IF (SELECT COUNT(*) FROM d_inbio_events WHERE [key] = '" + str(empid)+ "')= 0" \
        " INSERT INTO d_inbio_events" \
		" ([key]) VALUES" \
		" ('"+str(empid)+"')"
    if INBIO_USED:
        ret = sqlconns.sql_command(tx)
    tx = "IF (SELECT COUNT(*) FROM d_iface_events WHERE employee_id = " + str(empid)+ ")= 0" \
        " INSERT INTO d_iface_events" \
		" (employee_id) VALUES" \
		" ("+str(empid)+")"
    ret = sqlconns.sql_command(tx)
    return ret

def save_user_photo(xx,terminal_id):
    list = xx.split("\t")
    user_id = list[0].replace("USERPIC PIN=","")
    file_name = list[1].replace("FileName=","")
    size = list[2].replace("Size=","")
    content = list[3].replace("Content=","")
    date_now = f.get_sql_date(datetime.now(),"yyyy-mm-dd hh:mm:ss")
    tx = "UPDATE d_iface_photo SET size = '" + size + "', content='" + content + "',date_added="+date_now+",terminal_id="+str(terminal_id)+",new=1 WHERE employee_id =" + user_id + "" \
                    " IF @@ROWCOUNT=0" \
                    " INSERT INTO d_iface_photo(employee_id,file_name,size,content,date_added,terminal_id,new) VALUES ('"+user_id+"','"+file_name+"','"+size+"','"+content+"',"+date_now+","+str(terminal_id)+",1)"
    ret = sqlconns.sql_command(tx)
    if ret==0:
        if gl.face_to_personnel==True:
            content = base64.b64decode(content)
            tx = "UPDATE temployee SET photo = ? WHERE employee_id = ?"
            reta = sqlconns.sql_command_args(tx,content,user_id)
    return ret

def build_power_on_get_request(sn):
    terminal_id = get_terminal_id_from_sn(sn)
    if terminal_id=="": return ""
    #photo_stamp = 1
    att_stamp = 1
    op_stamp = 1
    tx = "SELECT table_name,stamp FROM d_iface_stamps WHERE terminal_id = " + str(terminal_id)
    ret = sqlconns.sql_select_into_list(tx)
    if ret!=-1:
        for index in range(len(ret)):
            if "att_stamp" in ret[index][0]:att_stamp = ret[index][1]
            if "op_stamp" in ret[index][0]:op_stamp = ret[index][1]
            #if "photo_stamp" in ret[index][0]:photo_stamp = ret[index][1]
    xx = "GET OPTION FROM:" + sn + "\r\nAttStamp=" + str(att_stamp) + "\r\nOpStamp=" + str(op_stamp) + \
         "\r\nStamp=" + str(att_stamp) + \
         "\r\nPhotoStamp=" + str(op_stamp) + \
             "\r\nErrorDelay=" + "3" + "\r\nDelay=" + "15" + "\r\nTransTimes=" + "00:00;14:05" + \
            "\r\nTransInterval=" + "1" + "\r\nTransFlag=" + "1" + "\r\nRealtime=" + \
            "1" + "\r\nEncrypt=" + "0" + "\r\nTimeZone=" + "1" + "\r\n"
    print(xx)
    #ths line below just just about photostamp
    #"\r\nStamp=" + str(att_stamp) + \
    return xx
#keep just in case            "\r\nPhotoStamp=" + str(op_stamp) + \

def get_terminal_id_from_sn(sn):
    tx = "SELECT TOP 1 terminal_id from tterminal WHERE ip_address = '" + sn+"'"
    ret = sqlconns.sql_select_single_field(tx)
    if ret==-1: return ""
    return ret

def get_device_serial(xx):
    xx = str.replace(xx,'/iclock/cdata?SN=','')
    list = str.split(xx,'&')
    return list[0]

def get_sn_getrequest(xx):
    return str.replace(xx,'/iclock/getrequest?SN=','')

def convert_card_to_hex(card):
    xx = "%x" % card
    xx = xx.zfill(10).upper()
    x1 = xx[0:2]
    x2 = xx[2:2 + 2]
    x3 = xx[4:4 + 2]
    x4 = xx[6:6 + 2]
    x5 = xx[8:8 + 2]
    return x5+x4+x3+x2+x1

def get_terminal_id(path):
    if "?SN=" not in path:
        return -1,-1,"","",""
    path = path.replace("/iclock/cdata?SN=","")
    list = str.split(path,"&")
    sn = list[0]
    table_type = list[1].replace("table=","")
    stamp = list[2].split("=",1)[1]
    tx = "SELECT TOP 1 terminal_id, configuration FROM tterminal WHERE ip_address = '" + sn+"'"
    ret = sqlconns.sql_select_into_list(tx)
    if ret == -1 or len(ret) == 0:
        terminal_id = -1
        configuration = -1
    else:
        terminal_id = ret[0][0]
        configuration = ret[0][1]
    return terminal_id, configuration, sn, table_type, stamp

def ret_error(ip_address, ret, function):
    f.error_logging(APPNAME, "Connect failure to " + ip_address + "...(" + str(ret) + ")", ERROR_LOG, function)

def insert_booking(data,terminal_id,sn,configuration,stamp):
    list = data.split("\t")
    if list[0]=='': return 1
    emp_id = int(list[0])
    booking = list[1]
    flag = 0
    if IFACE_FUNCTION_KEYS == True:
        if int(list[4])  == 3: flag = 3
    tx = "INSERT INTO d_iface_att (stamp,emp_id,date_and_time,sn)"\
        " VALUES ('" + stamp + "'," + str(emp_id) + ",'" + booking + "','" + sn + "')"
    ret = sqlconns.sql_command(tx)
    if ret==-1: return -1
    dte = f.iface_string_to_date_format(booking)
    if configuration == ACCESS_TERMINAL:
        booking = f.get_sql_date(dte,"yyyy-mm-dd hh:mm:ss")
        tx = "INSERT INTO taccess_archive (user_id,employee_id,terminal_id,date_and_time,flag,badge)"\
            "   VALUES (0," + str(emp_id) + "," + str(terminal_id) + "," + booking + ",1,0)"
        ret = sqlconns.sql_command(tx)
        if ret==-1: return -1
    elif configuration == ATTENDANCE_TERMINAL:
        booking = f.get_sql_date(dte,"yyyy-mm-dd hh:mm")
        tx = "INSERT INTO twork_unprocessed (employee_id,terminal_id,date_and_time,[type],flag,[key],memo,authorisation,authorisation_finalised,source)"\
            " VALUES (" + str(emp_id) + "," + str(terminal_id) + "," + booking + ",1000," + str(flag) + ",0,'',3,1,0)"
        ret = sqlconns.sql_command(tx)
        if ret==-1: return -1
        tx = tx.replace("twork_unprocessed", "twork_unprocessed_archive")
        ret = sqlconns.sql_command(tx)
        if ret==-1: return -1
        if FUNCTION_KEYS == True:
            if int(list[2]) > 0:
                tx = "INSERT INTO d_iface_att_event (employee_id,date_and_time,event,handled,terminal_id)"\
                    " VALUES (" + str(emp_id) + "," + booking + "," + str(list[2]) + ",0," + str(terminal_id) + ")"
                ret = sqlconns.sql_command(tx)
                if ret==-1: return -1
        if IFACE_FUNCTION_KEYS == True:
            if int(list[4]) > 0:
                tx = "INSERT INTO d_iface_att_event (employee_id,date_and_time,event,handled,terminal_id)"\
                    " VALUES (" + str(emp_id) + "," + booking + "," + str(list[4]) + ",0," + str(terminal_id) + ")"
                ret = sqlconns.sql_command(tx)
                if ret==-1: return -1
    else:
        return -1
    date_now = f.get_sql_date(datetime.now(),"yyyy-mm-dd hh:mm:ss")
    tx = "UPDATE d_iface_stamps SET stamp = " + stamp + ",date_added = " + date_now + ",sn = '" + str(sn) + "'  WHERE table_name like 'att_stamp' AND terminal_id = " + str(terminal_id) + ""\
                    " IF @@ROWCOUNT=0" \
                    " INSERT INTO d_iface_stamps(table_name,stamp,terminal_id,date_added,sn) VALUES ('att_stamp','" + stamp + "'," + str(terminal_id) + "," + \
                    date_now + ",'" + str(sn) + "')"
    ret = sqlconns.sql_command(tx)
    if ret==-1: return -1
    return 1

def set_env():
    global ACCESS_TERMINAL
    global ATTENDANCE_TERMINAL
    global DISTRIBUTOR
    global OLD_TIME
    global INBIO_USED
    global FINGER_DELETION_MINS
    global FUNCTION_KEYS
    global IFACE_FUNCTION_KEYS
    #this line doesnt do anything I think
    #f.error_logging(APPNAME,"error_log","2","")
    if os.path.isfile(gl.SCRIPT_ROOT + 'database.ini'):
        if sqlconns.readsql_connection_timeware_main_6() == 0:
            f.error_logging(APPNAME, "Error reading database.ini file.", "error_log","")
            return False
        elif sqlconns.readsql_connection_timeware_main_6() == 1:
            test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
            if test_comms == 0:
                    f.error_logging(APPNAME, "Error connecting to SQL server.", "error_log","")
            else:
                if os.path.isfile(gl.GENERAL_INI):
                    fob=open(gl.GENERAL_INI, "r")
                    listme = fob.readlines()
                    fob.close()
                else:
                    f.error_logging(APPNAME, "Error reading general.ini file.", "error_log","")
                    return False
                try:
                    for index in range(len(listme)):
                        if "'" in listme[index]: continue
                        if 'distributor' in listme[index]:
                            DISTRIBUTOR = str.split(listme[index],'=')[1]
                        if 'server_port' in listme[index]:
                            gl.server_port = int(str.split(listme[index],'=')[1])
                        if 'face_to_personnel' in listme[index]:
                            if 'true' in str.split(listme[index],'=')[1]:
                                gl.face_to_personnel = True
                        if "access_terminal" in listme[index]:
                            ACCESS_TERMINAL = int(listme[index].split("=")[1])
                        if "attendance_terminal" in listme[index]:
                            ATTENDANCE_TERMINAL = int(listme[index].split("=")[1])
                        if "fingerprint_deletion" in listme[index]:
                            FINGER_DELETION_MINS = int(listme[index].split("=")[1])
                        if 'oldtime' in listme[index]:
                            if 'false' in str.split(listme[index],'=')[1]:
                                OLD_TIME = False
                        if "inbio" in listme[index]:
                            if 'true' in str.split(listme[index],'=')[1]:
                                INBIO_USED = True
                        if "s680_function_keys" in listme[index]:
                            if 'true' in str.split(listme[index],'=')[1]:
                                FUNCTION_KEYS = True
                        if "iface_function_keys" in listme[index]:
                            if 'true' in str.split(listme[index],'=')[1]:
                                IFACE_FUNCTION_KEYS = True
                except Exception as e:
                    return False
                return True
    else:
        f.error_logging(APPNAME, "Error reading database.ini file.", "error_log","")
        return False

def version_check():
    if os.path.isfile(gl.LICENSE_TXT):
        fob=open(gl.LICENSE_TXT, "r")
        listme = fob.readlines()
        fob.close()
        try:
            version_year = sqlconns.decrypt_with_key(listme[0])
            ret = sqlear = sqlconns.decrypt_with_key(listme[0])
            ret = sqlconns.sql_select_single_field("SELECT TOP 1 [data] FROM tversion WHERE [property] like 'database version'")
            if ret==-1:return False
            database_version = str.split(ret,'.')
            if int(version_year) >= int('20'+database_version[0]):
                return True
            else:
                f.error_logging(APPNAME, "Version is out of date....canot start.", "error_log","")
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



if __name__ == "__main__":
    #win32serviceutil.HandleCommandLine(AppServerSvc)
    if set_env()==True:
      if version_check()==True:
            app = make_app()
            app.listen(gl.server_port)
            SERVER_STARTED = 1
            logging.getLogger('tornado.access').disabled = True
            tornado.ioloop.IOLoop.current().start()