import win32serviceutil
import win32service
import win32event
import servicemanager
import configparser
import os
import inspect
import logging
from logging.handlers import RotatingFileHandler

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "MyService"
    _svc_display_name_ = "My Service"

    _config = configparser.ConfigParser()

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        self._config.read(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/config.ini')
        print(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
        print(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/teconfig.ini')

        print(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
        print(self._config.sections())
        logDir = self._config["DEFAULT"]["loggingDir"]
        logPath = logDir + "/service-log.log"

        self._logger = logging.getLogger("MyService")
        self._logger.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(logPath, maxBytes=4096, backupCount=10)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))

        self._logger.info("Service Is Starting")

        self.main()

    def main(self):
        # your code could go here
        rc = None
        while rc != win32event.WAIT_OBJECT_0:

            # your code here...

            # hang for 1 minute or until service is stopped - whichever comes first
            rc = win32event.WaitForSingleObject(self.hWaitStop, (1 * 60 * 1000))

            # your code also here ...

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)