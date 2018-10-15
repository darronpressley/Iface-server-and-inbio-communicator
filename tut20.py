import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

if __name__ == '__main__':
#win32serviceutil.HandleCommandLine(AppServerSvc)

    from datetime import datetime
    then = datetime(2018, 10, 12, 12, 8, 15)  # Random date in the past
    now = datetime.now()  # Now
    duration = now - then  # For build-in functions
    duration_in_s = duration.total_seconds()
    #hours = int(divmod(duration_in_s, 3600)[0])
    hours = (duration_in_s // 3600)
    print(hours)

    format_str = "%Y-%m-%d %H:%M:%S.%f"
    now = datetime.strptime("2018-10-12 10:42:19.505149",format_str)

    ct = datetime.strptime("2018-10-12 15:42:19.506149", format_str)

    now = datetime.strptime("2018-10-13 01:00:12.822149", format_str)
    now = now.replace(minute=0,second=0,microsecond=0)

    ct = datetime.strptime("2018-10-12 16:00:12.823149", format_str)
    ct = ct.replace(minute=0,second=0,microsecond=0)
    duration = now - ct
    duration_in_s = duration.total_seconds()
    print(duration_in_s)
    #hours = int(divmod(duration_in_s, 3600)[0])
    hours = (int(duration_in_s) // 3600)
    print(hours)
    print(ct)





