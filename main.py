from ctypes import *
import datetime


def inbio_connect():
    #learning the sdk code
    params =  b'protocol=TCP,ipaddress=192.168.1.225,port=4370,timeout=4000,passwd='
    commpro = windll.LoadLibrary("plcommpro.dll")
    constr = create_string_buffer(params)
    hcommpro = commpro.Connect(constr)
    buffer= create_string_buffer(2048)
    items = b"IPAddress,~SerialNumber,DateTime"
    p_items = create_string_buffer(items)
    ret = commpro.GetDeviceParam(hcommpro,buffer,256,p_items)
    string = (buffer.raw)
    strong = str(string)
    strong = strong.replace("b'","")
    strong = strong[:-1]
    strong = strong.replace("\\x00","")
    #put the data into a list
    output = strong.split(',')
    timeanddate = output[2]
    print("tdate" + str(timeanddate))
    date_output = timeanddate.split('=')
    print("current inbio time = " + str(convert_int_to_time_date(date_output[1])))
    zk_numeric_date_time = convert_now_to_int()
    print(zk_numeric_date_time)
    print("new time = " + str(convert_int_to_time_date(zk_numeric_date_time)))
    items = "DateTime=" + str(zk_numeric_date_time)
    items = str.encode(items)
    p_items = create_string_buffer(items)
    ret = commpro.SetDeviceParam(hcommpro,p_items)

    #send a timezone
    p_table = str.encode('timezone')
    data = "TimezoneId=10\tThuTime1=" + str(timezone_dec("08:30","12:30"))
    p_data = str.encode(data)
    ret = commpro.SetDeviceData(hcommpro,p_table,p_data,"")

    #send a user
    p_table = str.encode('user')
    p_data = str.encode('Pin=200\tCardNo=14873078')
    ret = commpro.SetDeviceData(hcommpro,p_table,p_data,"")
    print(ret)

    p_table = str.encode('userauthorize')
    p_data = str.encode('Pin=200\tAuthorizeTimezoneId=10\tAuthorizeDoorId=2')
    print(p_data)
    ret = commpro.SetDeviceData(hcommpro,p_table,p_data,"")
    print(ret)

    commpro.Disconnect(hcommpro)


def inbio_connect1():
    #learning the sdk code
    params =  b'protocol=TCP,ipaddress=192.168.1.225,port=4370,timeout=4000,passwd='
    commpro = windll.LoadLibrary("plcommpro.dll")
    constr = create_string_buffer(params)
    hcommpro = commpro.Connect(constr)
    print(hcommpro)
    items = "Door1Drivertime=10"
    items = str.encode(items)
    p_items = create_string_buffer(items)
    ret = commpro.SetDeviceParam(hcommpro,p_items)
    print(ret)
    commpro.Disconnect(hcommpro)


def timezone_dec(time1,time2):
    lister = time1.split(':') + time2.split(':')
    return append_hex(((int(lister[0])*100+int(lister[1]))), ((int(lister[2])*100+int(lister[3]))))


def append_hex(a, b):
#for timezone, convert from and to time to decimal
    hexa = ("{0:#0{1}x}".format(int(a),6))
    hexb = ("{0:#0{1}x}".format(int(b),6))
    hexb = hexb.replace("0x","")
    hexa = hexa+hexb
    return int(hexa,0)


def convert_int_to_time_date(y):
    x = int(y)
    second = int(x % 60)
    minute = int((x / 60) % 60)
    hour = int((x / 3600) % 24)
    day = int((x / 86400) % 31 +1)
    month = int((x / 2678400) % 12 + 1)
    year = int((x / 32140800) + 2000)
    d = datetime.datetime(year,month,day,hour,minute,second)
    return d


def convert_now_to_int():
    x = convert_date_to_int(datetime.datetime.now())
    return x


def convert_date_to_int(dte):
    print(str(dte))
    second = int(dte.strftime("%S"))
    minute = int(dte.strftime("%M"))
    hour = int(dte.strftime("%H"))
    day = int(dte.strftime("%d"))
    month = int(dte.strftime("%m"))
    year = int(dte.strftime("%y"))
    x = ((year * 12 * 31) + ((month - 1) * 31) + (day-1))*(24*60*60) + (hour * 60 * 60) + (minute * 60) + second
    return x


inbio_connect1()
print('done')






