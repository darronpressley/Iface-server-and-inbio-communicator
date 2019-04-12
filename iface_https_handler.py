import logging
import tornado.ioloop
import maproxy.proxyserver
import servicemanager
import win32service
import win32event
import threading
import asyncore
import os
import base64
import gl
import sqlconns
import functions as f
import win32serviceutil
import time

SERVER_STARTED = 0

APPNAME = "IFACE_HTTP_Handler"
APP_VERSION = "uface 2018.0.5000"
# log file names
ERROR_LOG =  "error_log"

class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "iface https server"
    _svc_display_name_ = "iface https server"
    _svc_description_ = "iface https server from North Time and Data"

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
                            ssl_certs = {"certfile": gl.CERT_FILE,
                                         "keyfile": gl.KEY_FILE}
                            # "client_ssl_options=ssl_certs" simply means "listen using SSL"
                            server = maproxy.proxyserver.ProxyServer("localhost", gl.server_port,
                                                                     client_ssl_options=ssl_certs)
                            log_initialise()
                            SERVER_STARTED = 1
                            server.listen(gl.https_port)
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


def set_env():
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
                        if 'https_port' in listme[index]:
                            gl.https_port = int(str.split(listme[index],'=')[1])
                        if 'server_port' in listme[index]:
                            gl.server_port = int(str.split(listme[index],'=')[1])

                    f.error_logging(APPNAME, "Port is now: "+str(gl.https_port), "error_log", "")
                except Exception as e:
                    return False
                return True
    else:
        f.error_logging(APPNAME, "Error reading database.ini file.", "error_log","")
        return False

def log_initialise():
    f.error_logging(APPNAME, "server started.", "error_log","")

def log_exit():
    f.error_logging(APPNAME, "iface clean exit.", "error_log","")

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


if __name__ == "__main__":
    #win32serviceutil.HandleCommandLine(AppServerSvc)
    #set_env()

 if set_env()==True:
        # HTTPS->HTTP
        ssl_certs = {"certfile": "certificate.pem",
                     "keyfile": "privatekey.pem"}
        # "client_ssl_options=ssl_certs" simply means "listen using SSL"
        print(gl.server_port)
        server = maproxy.proxyserver.ProxyServer("localhost", gl.server_port,
                                                 client_ssl_options=ssl_certs)
        log_initialise()
        SERVER_STARTED = 1
        server.listen(gl.https_port)
        logging.getLogger('tornado.access').disabled = True
        tornado.ioloop.IOLoop.instance().start()


