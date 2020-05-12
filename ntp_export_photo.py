import gl
import sqlconns
import functions
import os
import sys
import base64
import datetime
IMAGE_TYPE = '.png'
EXPORT_PATH = ''
FILENAME_FORMAT = 'paylinklastnamefirstname'

PATH_ROOT = os.path.dirname(os.path.realpath(sys.executable)) + "\\"
#if you ever need to run inbio communicator as an application again put this line back in
#if not "library" in SCRIPT_ROOT: SCRIPT_ROOT = ""

PATH_ROOT=PATH_ROOT.replace("NTP_photo_export.exe","")

EXPORT_INI = PATH_ROOT + "export.ini"

#This was used for the SDC program to export the clockings

def set_env():
        global VERSION
        global APPSERVER
        global APPNAME
        global IMAGE_TYPE
        global FILENAME_FORMAT
        global EXPORT_PATH
        global FILENAME_FORMAT

        if os.path.isfile('export.ini'):
            fob = open(EXPORT_INI, "r")
            listme = fob.readlines()
            fob.close()
        else:
            print('export.ini not found')
            return False
        for index in range(len(listme)):
            if "'" in listme[index]: continue
            if 'image_type' in listme[index]:
                IMAGE_TYPE = str.split(listme[index], '=')[1]
                IMAGE_TYPE = str.replace(IMAGE_TYPE, '\n', '')
            if 'export_path' in listme[index]:
                EXPORT_PATH = str.split(listme[index], '=')[1]
                EXPORT_PATH = str.replace(EXPORT_PATH, """\\""", """/""")
                EXPORT_PATH = str.replace(EXPORT_PATH, '\n', '')
            if 'filename_format' in listme[index]:
                FILENAME_FORMAT = str.split(listme[index], '=')[1]
                FILENAME_FORMAT = str.replace(FILENAME_FORMAT, '\n', '')
        if os.path.isfile('database.ini'):
            if sqlconns.readsql_connection_timeware_main_6() == 0:
                print("no sqlconnection.ini file")
                return False
            elif sqlconns.readsql_connection_timeware_main_6() == 1:
                test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
                if test_comms == 0:
                    print("no connection")
                    return False
                else:
                    APPSERVER = gl.SERVER
        else:
            return False
        return True

def try_sql():
    xx = sqlconns.sql_select_into_list("SELECT photo,paylink,last_name,first_name from temployee where employee_status_id <> 8")
    cnt = 0
    for index in range(len(xx)):
        if xx[index][1] != None:
            if xx[index][0] != None:
                cnt += 1
                paylink = xx[index][1]
                lastname = xx[index][2]
                firstname = xx[index][3]
                filename = ''
                if FILENAME_FORMAT == 'lastnamefirstnamepaylink':
                    filename = EXPORT_PATH + lastname + '_' + firstname + '_' + paylink
                elif FILENAME_FORMAT == 'lastnamefirstname':
                    filename = EXPORT_PATH + lastname + '_' + paylink
                elif FILENAME_FORMAT == 'paylink':
                    filename = EXPORT_PATH + paylink
                else:
                    print('Error in filename_format...check ini file.')
                    return -1
                filename += IMAGE_TYPE
                print('Writing...', filename)
                f=open(filename,'wb')
                f.write(xx[index][0])
                f.close()
    return cnt

if __name__ == '__main__':
    bool = set_env()
    if bool == True:
        if IMAGE_TYPE == '.png' or IMAGE_TYPE =='.jpg':
            print('Export Photos starting at:', datetime.datetime.now(),'... to path ' + EXPORT_PATH)

            cnt = try_sql()
            if cnt != -1:
                print('Finish at: ', datetime.datetime.now(), '...' + str(cnt) + ' photos exported.')
        else:
            print('Image type must be .png or .jpg ...check export.ini setup.')



