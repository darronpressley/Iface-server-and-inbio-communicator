import sqlconns, os, sys

import gl


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
    global RECORD_BOOKING_ON_WARNING
    global EMAIL_NO_MASK_WARNING
    global EMAIL_TEMP_WARNING
    global MAX_TEMP
    global MAX_COMMANDS
    global MAX_COMMANDS_SIZE
    global RAW_CLOCKINGS

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
                        if 'https_port' in listme[index]:
                            gl.https_port = int(str.split(listme[index],'=')[1])
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
                        if "raw_clockings" in listme[index]:
                            if 'true' in str.split(listme[index],'=')[1]:
                                RAW_CLOCKINGS = True
                            if 'false' in str.split(listme[index], '=')[1]:
                                RAW_CLOCKINGS = False
                        if "check_repoll" in listme[index]:
                            CHECK_REPOLL = str.split(listme[index], '=')[1]
                        if "max_temp" in listme[index]:
                            MAX_TEMP = float(str.split(listme[index], '=')[1])
                        if "email_temp_warning" in listme[index]:
                            if 'true' in str.split(listme[index],'=')[1]:
                                EMAIL_TEMP_WARNING = True
                            if 'false' in str.split(listme[index], '=')[1]:
                                EMAIL_TEMP_WARNING = False
                        if "email_no_mask_detect" in listme[index]:
                            if 'true' in str.split(listme[index],'=')[1]:
                                EMAIL_NO_MASK_WARNING = True
                            if 'false' in str.split(listme[index], '=')[1]:
                                EMAIL_NO_MASK_WARNING = False
                        if "record_booking_on_warning" in listme[index]:
                            if 'true' in str.split(listme[index],'=')[1]:
                                RECORD_BOOKING_ON_WARNING = True
                            if 'false' in str.split(listme[index], '=')[1]:
                                RECORD_BOOKING_ON_WARNING = False
                        if "max_commands" in listme[index]:
                            MAX_COMMANDS = str.split(listme[index], '=')[1]
                        if "max_command_size" in listme[index]:
                            MAX_COMMANDS_SIZE = str.split(listme[index], '=')[1]
                    f.error_logging(APPNAME, "Port is now: "+str(gl.server_port), "error_log", "")
                except Exception as e:
                    return False
                return True
    else:
        f.error_logging(APPNAME, "Error reading database.ini file.", "error_log","")
        return False

import sys


xx = 'ZgCiQIUbDfZpu9G2ko1QVw=='
xx = 'n1nD3ZsuYHu/71LrVyuXPg=='
xx = 'VPuWTZ4e5bavg3mlbavwqg=='
#xx = '2022'


#print(sqlconns.encryption(xx))

print(sqlconns.decrypt_with_key(xx))


import sys



from win32com.client import Dispatch

zk = Dispatch("zkemkeeper.ZKEM")

print(zk)

tt = Dispatch("tscHelper.Encryption")

print(tt)

byteArr = "ExtraBitOfSalt".encode()

#Build hash
strDataIn = "Admin" + "Sky6fall!ng"
strHash = tt.ComputeHash(strDataIn, "SHA256", byteArr)

print(strHash)

set_env()

tx = """select top 1 secure_hash from tuser where user_name = 'Admin'"""
print(tx)
list = sqlconns.sql_select_single_field_timeware_user(tx)

print(list)

if strHash[0] == list: print('yer damn skippy')

strHash = None
tt = None
