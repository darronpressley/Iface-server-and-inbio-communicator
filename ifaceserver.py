#IFACE TORNADO version
#Author Darron Pressley darronpressley@gmail.com
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
from tornado import template as t
import logging

import servicemanager
import win32service
import win32event
import threading
import asyncore

import base64


import win32serviceutil

import functions as f
import sqlconns
import gl

SERVER_STARTED = 0

APPNAME = "IFACESERVER"
APP_VERSION = "uface 2018.0.5000"
# log file names
COMM_ERROR = "communications_log"
ERROR_LOG =  "error_log"
#oldtime is true by default for safety
OLD_TIME = True
INBIO_USED = False
FINGER_DELETION_MINS = 10
FUNCTION_KEYS = False
IFACE_FUNCTION_KEYS = False
CC_FUNCTION_KEYS = False
ORIGINAL_BOOKINGS = True

#mins and max stamps allowed to be recorded to prevent repoll issues
#criteris is > and < than
MIN_STAMP = 9998
MAX_STAMP = 1999999999


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/index.html')

class IclockHandler(tornado.web.RequestHandler):
    def compute_etag(self):
        return None
##power on request
    def get(self):
        list = self.request.uri.split("?SN=")
        list2 = list[1].split("&")
        sn = list2[0]
        ret = sqlconns.sql_command("UPDATE tterminal SET poll_success = ? WHERE ip_address = ?",datetime.now(),sn)
        if ret==-1: return
        #record ip address, you may have bother with this if https is ever used
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        if remote_ip != None: log_ip_address(sn,remote_ip)
        #power on send stamps and options
        power_on_getrequest = build_power_on_get_request(sn)
        if power_on_getrequest != "": self.write(power_on_getrequest)
        dte = date_time_string(sn)
        bDateHeader = False # are we sending the date header?
        #if dte != None: bDateHeader = True do not send dte heaaer in power on
        self.device_headers(dte,bDateHeader)

    def post(self):
        terminal_id, configuration, sn, table_type, stamp = get_terminal_id (self.request.uri)
        if terminal_id == -1: return
        postvars = self.request.body
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
        self.write("OK")
        dte = date_time_string(sn)
        bDateHeader = False # are we sending the date header?
        if dte != None: bDateHeader = True
        self.device_headers(dte,bDateHeader)

    def device_headers(self,dte,bDateHeader):
        self.set_status(200)# do not know if we need this and seems to conflict with status OK?
        self.clear_header("Server")
        self.set_header("HTTP", "1.1")
        self.set_header("Status","OK")
        self.set_header("cotent-type", "text/plain")
        #send time header or not
        if bDateHeader:
            self.set_header("Date",dte)
        else:
            self.clear_header("Date")


class IclockDevicecmdHandler(tornado.web.RequestHandler):
    def compute_etag(self):
        return None
#####devicecmd page, to update if commands are successful
    def post(self):
        sn = self.request.uri.replace("/iclock/devicecmd?SN=","")
        #terminal_id = get_terminal_id_from_sn(sn)#TODO is this line used?
        postvars = self.request.body
        postvars = postvars.decode("utf-8")
        cmd_list = postvars.split("\n")
        for index in range(len(cmd_list)):
            commands = cmd_list[index].split("&")
            if len(commands)==3:
                commands[0] = (commands[0].replace("ID=ID",""))
                #the command below used to int command[0]
                id = commands[0]
                returned = int(commands[1].replace("Return=",""))
                tx = "UPDATE d_iface_commands SET completed_flag = 1, completed_date = ?,returned = 0 WHERE iface_command_id = ?"
                ret = sqlconns.sql_command(tx,datetime.now(),id)
                if ret==-1: return
        self.write("OK")
        dte = date_time_string(sn)
        bDateHeader = False # are we sending the date header?
        if dte != None: bDateHeader = True
        self.device_headers(dte,bDateHeader)

    def device_headers(self,dte,bDateHeader):
        self.set_status(200)# do not know if we need this and seems to conflict with status OK?
        self.clear_header("Server")
        self.set_header("HTTP", "1.1")
        self.set_header("Status","OK")
        self.set_header("cotent-type", "text/plain")
        #send time header or not
        if bDateHeader:
            self.set_header("Date",dte)
        else:
            self.clear_header("Date")


class IclockGetrequestHandler(tornado.web.RequestHandler):
    def compute_etag(self):
        return None
###cdata page to send commands to the clock
    def get(self):
        list = self.request.uri.split("?SN=")
        list2 = list[1].split("&")
        sn = list2[0]
        uface = False#TODO this line is legacy. can it be removed
        tx = "SELECT TOP 1 notepad from tterminal WHERE ip_address = '" + sn + "'"
        notepad_options = str.lower(sqlconns.sql_select_single_field(tx))
        if "uface" in str.lower(notepad_options):uface = True #TODO this line is legacy, can it be removed
        data_list = get_commands_list(sn)
        if data_list==-1:
            return
        ret = sqlconns.sql_command("UPDATE tterminal SET poll_success = ? WHERE ip_address = ?",datetime.now(),sn)
        if ret==-1: return
        counter = 0
        reboot=0
        clear_data=0
        data=""
        #used to do this for uface terminals now do for all
        if len(data_list) == 0:
            ok = "OK"
            self.write(ok)
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
            dte = date_time_string(sn)
            bDateHeader = False  # are we sending the date header?
            if dte != None: bDateHeader = True
            self.device_headers(dte, bDateHeader)
            return
        if clear_data==1:
            self.write("C:ID"+str(data_list[index][0])+":CLEAR DATA\r\n")
            self.write(data)
        if reboot==1:
            self.write("C:ID"+str(data_list[index][0])+":REBOOT\r\n")
        dte = date_time_string(sn)
        bDateHeader = False # are we sending the date header?
        if dte != None: bDateHeader = True
        self.device_headers(dte,bDateHeader)

    def device_headers(self,dte,bDateHeader):
        self.set_status(200)# do not know if we need this and seems to conflict with status OK?
        self.clear_header("Server")
        self.set_header("HTTP", "1.1")
        self.set_header("Status","OK")
        self.set_header("cotent-type", "text/plain")
        #send time header or not
        if bDateHeader:
            self.set_header("Date",dte)
        else:
            self.clear_header("Date")

class TestPage(tornado.web.RequestHandler):
    def compute_etag(self):
        return None

    def get(self):
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
        data = ("<HTML><h1>Ifaceserver from " + DISTRIBUTOR + " is broadcasting.</h1>" \
                                                + "<br>Iface Server Version = " \
                                               + APP_VERSION + "<br><br>" \
                                                + "SQL Instance: " + str(sqlconns.sql_select_single_field('SELECT @@ServerName')) + "<br><br>" \
                                                + "normaltime = " + str(date_time_string_test('normaltime'))
                                                + ".<br>****oldtime = " + str(date_time_string_test('oldtime')) + '.<br>' \
                                                + old_time_status + terminal_configuration_status + photo_save_status \
                                                + 'Fingerprint delete old scan set to ' + str(FINGER_DELETION_MINS) +' mins.' + '<br>' \
                                                + 'Using Inbio Communication (ensure inbio tables are setup)= ' + str(INBIO_USED) + '.<br>' \
                                                + 'S680 Function keys = ' + str(FUNCTION_KEYS) + '.<br>' \
                                                + 'S680 Cost Centre Function keys = ' + str(CC_FUNCTION_KEYS)  + '.<br>' \
                                                + """Populating 'Original Bookings' = """ + str(ORIGINAL_BOOKINGS) + '.<br>' \
                                                + 'Iface Function keys = ' + str(IFACE_FUNCTION_KEYS) + '.<br><br>' \
                                                + 'License Year = ' + str(return_version()) + '.<br><br>'\
                                                + 'Min Stamp = ' + str(MIN_STAMP) + '.<br>'\
                                                + 'Max Stamp = ' + str(MAX_STAMP) + '.<br><br>'\
                                               + get_terminal_status_list() +'</HTML>')
        self.write(data)
        self.device_headers(None,False)

    def device_headers(self, dte, bDateHeader):
        self.set_status(200)# do not know if we need this and seems to conflict with status OK?
        self.clear_header("Server")
        self.set_header("Etag", "")
        self.clear_header("Etag")
        self.set_header("HTTP", "1.1")
        self.set_header("Status", "OK")
        #line removed for the test page
        #self.set_header("content-type", "text/plain")
        # send time header or not
        if bDateHeader:
            self.set_header("Date", dte)
        else:
            self.clear_header("Date")


class DeviceOptions(tornado.web.RequestHandler):
    def get(self):

        squirrel = "Squirrel"
        terminal_grid_options = "t grid options"
        self.render('templates/options.html', squirrel=squirrel, terminal_grid_options=terminal_grid_options)

    def post(self):
        self.name = self.get_argument("Submit", None)

        self.tmp = 'templates/options.html'
        self.render(self.tmp)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/test",TestPage),
        (r"/iclock/cdata",IclockHandler),
        (r"/iclock/getrequest",IclockGetrequestHandler),
        (r"/iclock/devicecmd",IclockDevicecmdHandler),
        (r"/options",DeviceOptions)
    ])


def log_ip_address(sn, ip):
    tx = "UPDATE d_iface_stamps SET last_ip = '"+ ip+ "' WHERE sn = '"+ sn+ "'"
    ret = sqlconns.sql_command(tx)

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
                            logging.getLogger('tornado.access').disabled = True
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

def date_time_string_old(serial_number):
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

def date_time_string(serial_number):
    notepad_options = sqlconns.sql_select_single_field(
            "SELECT TOP 1 notepad from tterminal WHERE ip_address = '" + serial_number + "'")
    if 'notime' in str.lower(notepad_options): return None
    dte = datetime.now()
    if OLD_TIME == True:
        if 'oldtime' in str.lower(notepad_options):
            dte = dte - timedelta(hours = 1)
    #'timezone mod, use timezone=1 in the notepad option for Denmark'
    dte = timezone_difference(dte,str(notepad_options))
    now = time.mktime(dte.timetuple())
    year, month, day, hh, mm, ss, wd, y, z = time.localtime(now)
    s = "%s,%02d %3s %4d %02d:%02d:%02d GMT" % (
        dte.strftime('%a'),
        day, dte.strftime('%b'), year,hh, mm, ss)
    return s


def date_time_string_power(serial_number):
#probably not used anymore since not setting time and date in power on get request
    dte = datetime.now()
    if OLD_TIME == True:
        tx = sqlconns.sql_select_single_field("SELECT TOP 1 notepad from tterminal WHERE ip_address = '" + serial_number + "'")
        if 'oldtime' in str(tx):
            dte = dte - timedelta(hours = 1)

    #'are we using timezones'
    if 'timezone' in str(tx): dte = timezone_difference (dte,tx)

    now = time.mktime(dte.timetuple())
    year, month, day, hh, mm, ss, wd, y, z = time.localtime(now)
    s = "%s,%02d %3s %4d %02d:%02d:%02d GMT" % (
        dte.strftime('%a'),
        day, dte.strftime('%b'), year,hh, mm, ss)
    return s

def timezone_difference(dte,tx):
    list = tx.splitlines()
    time_adj = 0
    for n in range(len(list)):
        if 'timezone' in list[n]:
            try:
                time_adj = int(list[n].split("=")[1])
            except Exception as e:
                time_adj=0
            if time_adj != 0:
                dte = dte - timedelta(hours = (-time_adj))
                return dte
    return dte

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
    f.error_logging(APPNAME, "server started.", "error_log","")

def log_exit():
    f.error_logging(APPNAME, "iface clean exit.", "error_log","")

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
    #if stamp is too big then bomb out for safety...do not record stamps than can be from 1970 eg 3300000000
    # typical stamp is 601659677, that is 9 digits long
    #get MAX and MIN stamps from general.ini

    date_now = f.get_sql_date(datetime.now(),"yyyy-mm-dd hh:mm:ss")
    tx = "UPDATE d_iface_stamps SET stamp = " + stamp + ",date_added = " + date_now  + ",sn = '" + sn + "' WHERE table_name = 'op_stamp' AND terminal_id = " + str(terminal_id) + ""\
                " IF @@ROWCOUNT=0" \
                " INSERT INTO d_iface_stamps(table_name,stamp,terminal_id,date_added,sn) VALUES ('op_stamp','" + stamp + "','" + str(terminal_id) + "'," + date_now + ",'" + sn + "')"

    #just replace op_stamp with bad_op_stamp
    if int(stamp) >= int(MAX_STAMP) or int(stamp) <= int(MIN_STAMP):
        tx =str.replace(tx, 'op_stamp', 'bad_op_stamp')
        return

    ret = sqlconns.sql_command(tx)
    if ret==-1: return -1
    return

def save_op_log(xx,terminal_id,sn):
    list = xx.split("\t")
    if list[0] == "OPLOG 3":
        dte = list[2]
        #push button
        if list[3] == "53":
            tx = "if (SELECT COUNT (*) from taccess_archive WHERE terminal_id = ? AND date_And_time = ? AND flag = ?)>0"\
                 "INSERT INTO taccess_archive (user_id,employee_id,terminal_id,date_and_time,flag,badge) VALUES (0,0,?,?,?,0)"
            ret = sqlconns.sql_command(tx,terminal_id,dte,8,terminal_id,dte,8)
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
    #check if already there
    tx = "SELECT TOP 1 d_iface_face_id from d_iface_tmp WHERE employee_id ="+ user_id+ " AND fid="+fid+" AND [tmp] ='"+ tmp+ "'"
    ret = sqlconns.sql_select_single_field(tx)
    if ret!= "" and int(ret) > 0:
        tx = "If ("\
        "SELECT count(*) from d_iface_tmp"\
        " where d_iface_face_id = " + str(int(ret)) + " and repoll_count is null) > 0"\
        " UPDATE d_iface_tmp"\
        " SET repoll_count = 1,"\
        " repoll_date = getdate()"\
        " WHERE d_iface_face_id =" + str(int(ret)) + ""\
        " ELSE"\
        " UPDATE d_iface_tmp"\
        " SET repoll_count = repoll_count + 1,"\
        " repoll_date = getdate()"\
        " WHERE d_iface_Face_id = " + str(int(ret))
        ret = sqlconns.sql_command(tx)

        return 1
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
    #check if exists
    tx = "Select top 1 [d_iface_finger_id] from d_iface_finger WHERE employee_id =" + user_id + " AND fid="+fid+ " AND tmp = '"+ tmp + "'"
    ret = sqlconns.sql_select_single_field(tx)
    if ret != "" and int(ret) > 0:
        tx = "If ("\
        "SELECT count(*) from d_iface_finger"\
        " where d_iface_finger_id = "+str(int(ret))+ " and repoll_count is null) > 0"\
        " UPDATE d_iface_finger"\
        " SET repoll_count = 1,"\
        " repoll_date = getdate()"\
        " WHERE d_iface_finger_id ="+ str(int(ret))+ ""\
        " ELSE"\
        " UPDATE d_iface_finger"\
        " SET repoll_count = repoll_count + 1,"\
        " repoll_date = getdate()"\
        " WHERE d_iface_finger_id = "+ str(int(ret))
        ret = sqlconns.sql_command(tx)
        return 1
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
    #check exixts and dont write
    tx = "Select top 1 [d_iface_photo_id] from d_iface_photo WHERE employee_id =" + user_id + " AND content = '"+ content + "'"
    ret = sqlconns.sql_select_single_field(tx)
    if ret != "" and int(ret) > 0:
        tx = "If ("\
        "SELECT count(*) from d_iface_photo"\
        " where d_iface_photo_id = "+str(int(ret))+ " and repoll_count is null) > 0"\
        " UPDATE d_iface_photo"\
        " SET repoll_count = 1,"\
        " repoll_date = getdate()"\
        " WHERE d_iface_photo_id ="+ str(int(ret))+ ""\
        " ELSE"\
        " UPDATE d_iface_photo"\
        " SET repoll_count = repoll_count + 1,"\
        " repoll_date = getdate()"\
        " WHERE d_iface_photo_id = "+ str(int(ret))
        ret = sqlconns.sql_command(tx)
        return 1
    #photo does not exist, carry on
    tx = "UPDATE d_iface_photo SET size = '" + size + "', content='" + content + "',date_added="+date_now+",terminal_id="+str(terminal_id)+",new=1 WHERE employee_id =" + user_id + "" \
                    " IF @@ROWCOUNT=0" \
                    " INSERT INTO d_iface_photo(employee_id,file_name,size,content,date_added,terminal_id,new) VALUES ('"+user_id+"','"+file_name+"','"+size+"','"+content+"',"+date_now+","+str(terminal_id)+",1)"
    ret = sqlconns.sql_command(tx)
    if ret==0:
        if gl.face_to_personnel==True:
            content = base64.b64decode(content)
            tx = "UPDATE temployee SET photo = ? WHERE employee_id = ?"
            ret = sqlconns.sql_command_args(tx,content,user_id)
    return ret

def build_power_on_get_request(sn):
    terminal_id = get_terminal_id_from_sn(sn)
    if terminal_id=="": return ""
    att_stamp = 1
    op_stamp = 1
    tx = "SELECT table_name,stamp FROM d_iface_stamps WHERE terminal_id = " + str(terminal_id)
    ret = sqlconns.sql_select_into_list(tx)
    if ret!=-1:
        for index in range(len(ret)):
            if ret[index][0]== "att_stamp": att_stamp = ret[index][1]
            if ret[index][0]== "op_stamp": op_stamp = ret[index][1]
    else:
        return ret
    tx =   "SELECT TOP 1 notepad from tterminal WHERE ip_address = '" + sn + "'"
    notepad_options = str.lower(sqlconns.sql_select_single_field(tx))
#tidy up on stamps based on latest push firmware, refer to older backups if you need to revert this.
    trans_flag_string = "1"
    if 'uface' in notepad_options:
        trans_flag_string = 'TransData AttLog\tOpLog\tAttPhoto\tEnrollUser\tChgUser\tEnrollFP\tChgFP\tFACE\tUserPic'
    xx = "GET OPTION FROM:" + sn + \
            "\r\nStamp=" + str(att_stamp) +\
            "\r\nOpStamp=" + str(op_stamp) + \
            "\r\nPhotoStamp=" + str(op_stamp) + \
            "\r\nErrorDelay=3" +\
            "\r\nDelay=5" + \
            "\r\nTransTimes=" + "00:00;14:05" + \
            "\r\nTransInterval=" + "1" + \
            "\r\nTransFlag=" + trans_flag_string + \
            "\r\nRealtime=1" + \
            "\r\nTimeZone=1" + \
            "\r\nATTLOGStamp=" + str(att_stamp) + \
            "\r\nOPERLOGStamp=" + str(op_stamp) + \
            "\r\nATTPHOTOStamp=" + str(op_stamp) + \
            "\r\n"

    return xx

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
    #if stamp is bad do not save it
    if int(stamp) >= int(MAX_STAMP) or int(stamp) <= int(MIN_STAMP):
        date_now = f.get_sql_date(datetime.now(), "yyyy-mm-dd hh:mm:ss")
        tx = "UPDATE d_iface_stamps SET stamp = " + stamp + ",date_added = " + date_now + ",sn = '" + str(
            sn) + "'  WHERE table_name = 'bad_att_stamp' AND terminal_id = " + str(terminal_id) + "" \
            " IF @@ROWCOUNT=0" \
            " INSERT INTO d_iface_stamps(table_name,stamp,terminal_id,date_added,sn) VALUES ('bad_att_stamp','" + stamp + "'," + str(
            terminal_id) + "," + \
             date_now + ",'" + str(sn) + "')"
        ret = sqlconns.sql_command(tx)
        if ret == -1: return -1

    #check if in att log table and bail out if need be
    test_dte = f.iface_string_to_date_format(booking)
    test_booking = f.get_sql_date(test_dte, "yyyy-mm-dd hh:mm:ss")
    if int(list[2]) != 100:
        if bAttFound (sn,emp_id,test_booking): return 1
    #if a cost centre clocking then check att_log_table and bail out if need be
    else:
        if bAttEventFound(terminal_id, emp_id, test_booking): return 1

    if IFACE_FUNCTION_KEYS == True:
        if int(list[4])  == 3: flag = 3
    #backup attendance clocking, may add as an option in future, may add a purge to the build commands script anything older than a year?
    #this is handled in the application script
    tx = "INSERT INTO d_iface_att (stamp,emp_id,date_and_time,sn)"\
        " VALUES ('" + stamp + "'," + str(emp_id) + ",'" + booking + "','" + sn + "')"
    ret = sqlconns.sql_command(tx)
    if ret==-1: return -1

    dte = f.iface_string_to_date_format(booking)

    #DEVICE = ACCESS CONTROL TERMINAL
    if configuration == ACCESS_TERMINAL:
        booking = f.get_sql_date(dte,"yyyy-mm-dd hh:mm:ss")
        #if booking not found then write it
        tx = "INSERT INTO taccess_archive (user_id,employee_id,terminal_id,date_and_time,flag,badge)"\
            "   VALUES (0," + str(emp_id) + "," + str(terminal_id) + "," + booking + ",1,0)"
        ret = sqlconns.sql_command(tx)
        if ret==-1: return -1
        #insert rollcall
        roll_call_enabled,reader_direction,reader_description, zone_id = get_terminal_roll_call_info (terminal_id)
        if roll_call_enabled == -1: return -1
        reader = 1
        if roll_call_enabled ==True:
            ret = update_roll_call_table (emp_id,reader,reader_direction,reader_description,terminal_id,zone_id,dte)
            if ret ==-1 : return -1
    elif configuration == ATTENDANCE_TERMINAL:
        booking = f.get_sql_date(dte, "yyyy-mm-dd hh:mm")
        #cost centre clocking = 100
        #if code is differentt to 100 then it also needs an attendance entry
        if int(list[2]) < 100:
            #this is the ACTUAL ATTENDANCE swipe
            tx = "INSERT INTO twork_unprocessed (employee_id,terminal_id,date_and_time,[type],flag,[key],memo,authorisation,authorisation_finalised,source)"\
                " VALUES (" + str(emp_id) + "," + str(terminal_id) + "," + booking + ",1000," + str(flag) + ",0,'',3,1,0)"
            ret = sqlconns.sql_command(tx)
            if ret==-1: return -1
            if ORIGINAL_BOOKINGS:
                tx = tx.replace("twork_unprocessed", "twork_unprocessed_archive")
                ret = sqlconns.sql_command(tx)
                if ret==-1: return -1
        if FUNCTION_KEYS == True:
            #shouldnt be over 100 as this will conflict with other functions
            #business leave booking on terminal
            if int(list[2]) > 0 and int(list[2])<100:
                tx = "INSERT INTO d_iface_att_event (employee_id,date_and_time,event,handled,terminal_id)"\
                    " VALUES (" + str(emp_id) + "," + booking + "," + str(list[2]) + ",0," + str(terminal_id) + ")"
                ret = sqlconns.sql_command(tx)
                if ret==-1: return -1
        if IFACE_FUNCTION_KEYS == True:
            #business leave booking on iface terminal
            if int(list[4]) > 0:
                tx = "INSERT INTO d_iface_att_event (employee_id,date_and_time,event,handled,terminal_id)"\
                    " VALUES (" + str(emp_id) + "," + booking + "," + str(list[4]) + ",0," + str(terminal_id) + ")"
                ret = sqlconns.sql_command(tx)
                if ret==-1: return -1
        if CC_FUNCTION_KEYS == True:
            ########## Work codes have been removed, list[4] is now nothing pending ticket from ZK
            ########## Now use punch key over 100
            ########## 100 can be use for Dummy default button
            # cc function keys if code is greater than 100 then make the booking but other than that ignore it.

            if int(list[2]) >= 100:
                #cc_id = int(list[4])
                #if cc_id >0:
                tx = "INSERT INTO d_iface_att_event (employee_id,date_and_time,event,handled,terminal_id)" \
                     " VALUES (" + str(emp_id) + "," + booking + "," + str(list[2]) + ",0," + str(
                    terminal_id) + ")"
                ret = sqlconns.sql_command(tx)
                if ret == -1: return -1
    else:
        return -1
    date_now = f.get_sql_date(datetime.now(),"yyyy-mm-dd hh:mm:ss")
    tx = "UPDATE d_iface_stamps SET stamp = " + stamp + ",date_added = " + date_now + ",sn = '" + str(sn) + "'  WHERE table_name = 'att_stamp' AND terminal_id = " + str(terminal_id) + ""\
                    " IF @@ROWCOUNT=0" \
                    " INSERT INTO d_iface_stamps(table_name,stamp,terminal_id,date_added,sn) VALUES ('att_stamp','" + stamp + "'," + str(terminal_id) + "," + \
                    date_now + ",'" + str(sn) + "')"

    ret = sqlconns.sql_command(tx)
    if ret==-1: return -1
    return 1

def bAttFound (sn,emp_id,booking):
    tx = "select TOP 1 [d_iface_att_id] from d_iface_att WHERE sn = '"+ sn+ "' AND emp_id = "+ str(emp_id)+ " AND date_and_time = "+ booking
    ret = sqlconns.sql_select_single_field(tx)

    if ret == "":
        return False
    if int(ret) > 0:
        tx = "If ("\
        "SELECT count(*) from d_iface_att" \
        " where d_iface_att_id = "+str(int(ret))+ " and repoll_count is null) > 0"\
        " UPDATE d_iface_att"\
        " SET repoll_count = 1,"\
        " repoll_date = getdate()"\
        " WHERE d_iface_att_id ="+ str(int(ret))+ ""\
        " ELSE"\
        " UPDATE d_iface_att"\
        " SET repoll_count = repoll_count + 1,"\
        " repoll_date = getdate()"\
        " WHERE d_iface_att_id = "+ str(int(ret))
        ret = sqlconns.sql_command(tx)

        return True
    else:
        return False

def bAttEventFound (terminal_id,emp_id,booking):
    tx = "select TOP 1 [d_iface_att_id] from d_iface_att WHERE terminal_id = "+ str(terminal_id) + " AND emp_id = "+ str(emp_id)+ " AND date_and_time = "+ booking
    ret = sqlconns.sql_select_single_field(tx)
    if ret == "": return False
    if int(ret) > 0:
        tx = "If ("
        "SELECT count(*) from d_iface_att_event"
        " where d_iface_events_id = "+str(int(ret))+ " and repoll_count is null) > 0"
        " UPDATE d_iface_att_event"
        " SET repoll_count = 1,"
        " repoll_date = getdate()"
        " WHERE d_iface_events_id ="+ str(int(ret))+ ""
        " ELSE"
        " UPDATE d_iface_att_event"
        " SET repoll_count = repoll_count + 1,"
        " repoll_date = getdate()"
        " WHERE d_iface_events_id = "+ str(int(ret))
        ret = sqlconns.sql_command(tx)
        return True
    else:
        return False

def get_terminal_roll_call_info(terminal_id):
    tx = "SELECT TOP 1 roll_call_enabled,r1_direction,r1_description,r1_zone_id FROM tterminal WHERE terminal_id = " + str(terminal_id)
    roll_call_info_list = sqlconns.sql_select_into_list(tx)
    if roll_call_info_list == -1 : return -1,-1,-1,-1
    for n in range(len(roll_call_info_list)):
        roll_call_enabled = roll_call_info_list[n][0]
        reader_direction = roll_call_info_list[n][1]
        reader_description = roll_call_info_list[n][2]
        zone_id = roll_call_info_list[n][3]
    return roll_call_enabled,reader_direction,reader_description,zone_id

def update_roll_call_table(empid,reader,reader_direction,reader_description,terminal_id,zone_id,dte):
    ret = sqlconns.sql_command("UPDATE temployee_roll_call SET reader = ?,reader_direction = ?,reader_description = ?,terminal_id = ?,zone_id = ?,date_and_time = ? WHERE employee_id = ?"\
                    " IF @@ROWCOUNT=0" \
                    " INSERT INTO temployee_roll_call(employee_id,reader,reader_direction,reader_description,terminal_id,zone_id,date_and_time) VALUES (?,?,?,?,?,?,?)",
                               reader,reader_direction,reader_description,terminal_id,zone_id,dte,
                               empid,
                               empid,reader,reader_direction,reader_description,terminal_id,zone_id,dte)
    return ret

def set_env():
    global ACCESS_TERMINAL
    global ATTENDANCE_TERMINAL
    global DISTRIBUTOR
    global OLD_TIME
    global INBIO_USED
    global FINGER_DELETION_MINS
    global FUNCTION_KEYS
    global IFACE_FUNCTION_KEYS
    global ORIGINAL_BOOKINGS
    global CC_FUNCTION_KEYS
    global MIN_STAMP
    global MAX_STAMP
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
                        if "original_bookings" in listme[index]:
                            if 'false' in str.split(listme[index],'=')[1]:
                                ORIGINAL_BOOKINGS = False
                        if "cost_centre_function_keys" in listme[index]:
                            if 'true' in str.split(listme[index], '=')[1]:
                                CC_FUNCTION_KEYS = True
                        if "max_stamp" in listme[index]:
                            MAX_STAMP = str.split(listme[index], '=')[1]
                        if "min_stamp" in listme[index]:
                            MIN_STAMP = str.split(listme[index], '=')[1]
                    f.error_logging(APPNAME, "Port is now: "+str(gl.server_port), "error_log", "")
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



if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(AppServerSvc)
    set_env()


#    if set_env()==True:
 #       if version_check()==True:
  #          log_initialise()
   #         app = make_app()
    #        app.listen(gl.server_port)
     #       SERVER_STARTED = 1
      #      logging.getLogger('tornado.access').disabled = True
       #     tornado.ioloop.IOLoop.current().start()

