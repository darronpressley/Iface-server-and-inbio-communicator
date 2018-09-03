import gl
import sqlconns
import functions
import os
import sys
import base64
import datetime


#This was used for the SDC program to export the clockings

def set_env():
        global VERSION
        global APPSERVER
        global APPNAME

        if os.path.isfile('database.ini'):
            if sqlconns.readsql_connection_timeware_main_6() == 0:
                print("no ini file")
                return
            elif sqlconns.readsql_connection_timeware_main_6() == 1:
                test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
                if test_comms == 0:
                    print("no connection")
                    return
                else:
                    APPSERVER = gl.SERVER

        else:
            return

def try_sql():
    xx = sqlconns.sql_select_into_list("SELECT photo,paylink from temployee where employee_status_id <> 8")
    for index in range(len(xx)):
        if xx[index][1] != None:
            if xx[index][0] != None:
                yy = xx[index][0]
                #print(str(len(yy)) + " " + str(xx[index][1]))
                f=open("d:/ntd/images/"+ str(xx[index][1])+".png",'wb')
                f.write(yy)
                f.close()


def big_sql_query():
    xx = sqlconns.sql_select_into_list("SELECT TOP 400 command from d_iface_commands WHERE sent <> 1 ORDER BY iface_command_id DESC")
    print(xx)

if __name__ == '__main__':
    set_env()
    print(datetime.datetime.now())
    big_sql_query()
    print(datetime.datetime.now())