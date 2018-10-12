#DP
#12/10/2018
#Iface Timezone Resolver
#part of the Ifaceserver quite

#this is a standalone script and will require python34 installed to run and a windows scheduled task
#call python and with arguments for the script

#copy GOLDEN folder to customer folder
#TODO wrap as a window service should this be required anymore.
#if you need a list of the timezones run this
#for tz in pytz,all_timezones:
#   print(tz)

ATTENDANCE_TERMINALS = 10
ACCESS_TERMINALS = 4
SERVER_STARTED = 0

APPNAME = "IFACESERVER Timezone Resolver"
APP_VERSION = "2018.0.5000"
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

import time
import functions as f
from datetime import datetime
from datetime import timedelta

import time

import sys,os
import sqlconns
import gl
import pytz

TIMEZONE_DICT = {"australia":"Australia/Brisbane","dubai":"Asia/Dubai","ohio":"US/Eastern","florida":"US/Eastern"}

def TimezoneResolver():
    tx = "SELECT description,notepad,terminal_id FROM tterminal WHERE configuration IN (4,10) and ip_address not like '%.%' AND number < 1000"
    ret = sqlconns.sql_select(tx)
    if ret == -1: return
    for n in range(len(ret)):
        #print(type(ret[n]),'start of n loop',str(n),str(ret[n][0]))
        notepad = ""
        terminal_id = 0
        timezone = 0
        str_timezone = ""
        hours = 0
        if str.lower(ret[n][0]) == 'australia':
            try:
                terminal_id = ret[n][2]
                area = str.lower(ret[n][0])
                str_timezone = TIMEZONE_DICT[area]
                if ret[n][1] != None:
                    notepad = ret[n][1]
                    notepad = clear_timezone(notepad)
            except Exception as e:
                False
        if str.lower(ret[n][0]) == 'ohio':
            try:
                terminal_id = ret[n][2]
                area = str.lower(ret[n][0])
                str_timezone = TIMEZONE_DICT[area]
                if str(ret[n][1]) != None:
                    notepad = str(ret[n][1])
                    notepad = clear_timezone(notepad)
            except:
                False
        if str.lower(ret[n][0]) == 'florida':
            try:
                terminal_id = ret[n][2]
                area = str.lower(ret[n][0])
                str_timezone = TIMEZONE_DICT[area]
                if str(ret[n][1]) != None:
                    notepad = str(ret[n][1])
                    notepad = clear_timezone(notepad)
            except:
                False
        if str.lower(ret[n][0]) == 'dubai':
            try:
                terminal_id = ret[n][2]
                area = str.lower(ret[n][0])
                str_timezone = TIMEZONE_DICT[area]
                if str(ret[n][1]) != None:
                    notepad = str(ret[n][1])
                    notepad = clear_timezone(notepad)
            except:
                False
        if notepad != "":
            tz = pytz.timezone(str_timezone)
            ct = datetime.now(tz=tz)
            ct = ct.replace(tzinfo=None)
            now = datetime.now()
            duration = ct - now
            duration_in_s = duration.total_seconds()
            hours = int(divmod(duration_in_s, 3600)[0])
            tz = 'timezone='+ str(hours)
            notepad = str.replace(notepad, 'timezone=', tz)
            tx = "UPDATE tterminal SET notepad = '"+ notepad+ "' WHERE terminal_id = " + str(terminal_id)

            update_ret = sqlconns.sql_command(tx)

def clear_timezone(notepad):
    notepad = str.replace(notepad, 'timezone=0', 'timezone=')
    notepad = str.replace(notepad, 'timezone=1', 'timezone=')
    notepad = str.replace(notepad, 'timezone=2', 'timezone=')
    notepad = str.replace(notepad, 'timezone=3', 'timezone=')
    notepad = str.replace(notepad, 'timezone=4', 'timezone=')
    notepad = str.replace(notepad, 'timezone=5', 'timezone=')
    notepad = str.replace(notepad, 'timezone=6', 'timezone=')
    notepad = str.replace(notepad, 'timezone=7', 'timezone=')
    notepad = str.replace(notepad, 'timezone=8', 'timezone=')
    notepad = str.replace(notepad, 'timezone=9', 'timezone=')
    notepad = str.replace(notepad, 'timezone=10', 'timezone=')
    notepad = str.replace(notepad, 'timezone=11', 'timezone=')
    notepad = str.replace(notepad, 'timezone=12', 'timezone=')
    notepad = str.replace(notepad, 'timezone=13', 'timezone=')
    notepad = str.replace(notepad, 'timezone=14', 'timezone=')
    notepad = str.replace(notepad, 'timezone=15', 'timezone=')
    notepad = str.replace(notepad, 'timezone=16', 'timezone=')
    notepad = str.replace(notepad, 'timezone=17', 'timezone=')
    notepad = str.replace(notepad, 'timezone=18', 'timezone=')
    notepad = str.replace(notepad, 'timezone=19', 'timezone=')
    notepad = str.replace(notepad, 'timezone=20', 'timezone=')
    notepad = str.replace(notepad, 'timezone=21', 'timezone=')
    notepad = str.replace(notepad, 'timezone=22', 'timezone=')
    notepad = str.replace(notepad, 'timezone=23', 'timezone=')
    #minus figures
    notepad = str.replace(notepad, 'timezone=-1', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-2', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-3', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-4', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-5', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-6', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-7', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-8', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-9', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-10', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-11', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-12', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-13', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-14', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-15', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-16', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-17', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-18', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-19', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-20', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-21', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-22', 'timezone=')
    notepad = str.replace(notepad, 'timezone=-23', 'timezone=')
    return notepad

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

                except Exception as e:
                    return False
                return True
    else:
        f.error_logging(APPNAME, "Error reading database.ini file.", "error_log","")
        return False

if __name__ == '__main__':
    if set_env() == True:
        TimezoneResolver()
    else:
        False