#resuable functions
#maintain for future coding
#before final build get rid of any functions you dont need....or does that eve nmatter?
import datetime
import gl
import sqlconns
import os


def convert_sql_date(dte,type):
#year fix to get around pre 1900 python issue
    day = "%02d" % (dte.day,)
    month = "%02d" % (dte.month,)
    year = dte.year
    hour = "%02d" % (dte.hour,)
    minute = "%02d" % (dte.minute,)
    second = "%02d" % (dte.second,)

    if type == "hh:mm": return str(hour) + ":" + str(minute)
    if type =="yyyymmdd" : return str(year)+str(month)+str(day)
    if type =="yyyy-mm-dd" : return str(year)+ "-" + str(month) + "-" + str(day)

    if type=="yyyymmddhhmm": return str(year)+str(month)+str(hour) + str(minute)(day)
    if type== "dd/mm/yyyy hh:mm": return str(day) + """/""" + str(month) + """/""" + str(year) + """ """ + str(hour) + """:""" + str(minute)
    if type== "dd/mm/yyyy hh:mm:ss": return str(day) + """/""" + str(month) + """/""" + str(year) + """ """ + str(hour) + """:""" + str(minute) + """:""" + str(second)
    if type== "yyyy-mm-dd hh:mm:ss": return str(year) + """-""" + str(month) + """-""" + str(day) + """ """ + str(hour) + """:""" + str(minute) + """:""" + str(second)
    if type== "yyyy-mm-dd hh:mm": return str(year) + """-""" + str(month) + """-""" + str(day) + """ """ + str(hour) + """:""" + str(minute)
    return ""

def get_sql_date(dte,type):
    tx = """'""" + convert_sql_date(dte,type) + """'"""
    return tx

def iface_string_to_date_format(xx):
    return datetime.datetime.strptime(xx, "%Y-%m-%d %H:%M:%S")

def convert_listlist_to_list(listlist):
#used if a list of a list only has one field
    list = []
    for index in range(len(listlist)):
        list[len(list):] = [listlist[index][0]]
    return list

def convert_sec_to_sql_date(y):
    x = int(y)
    second = int(x % 60)
    minute = int((x / 60) % 60)
    hour = int((x / 3600) % 24)
    day = int((x / 86400) % 31 +1)
    month = int((x / 2678400) % 12 + 1)
    year = int((x / 32140800) + 2000)
    #d = datetime.datetime(year,month,day,hour,minute,second)
    d = datetime.datetime(year,month,day,hour,minute,second)
    dte = d.strftime('%Y-%m-%d %H:%M:%S')
    dte = """'""" + dte + """'"""
    return dte


def error_logging(app,error,type,function):
    if type == "error_log": filename = gl.ERROR_LOG
    elif type == "communications_log": filename = gl.COMM_ERROR_LOG
    elif type =="sql": filename = gl.ERROR_LOG
    else: return
    dte = convert_sql_date(datetime.datetime.now(),"dd/mm/yyyy hh:mm")
    try:
        e = open(filename, 'a')
        e.write(dte+","+app +','+ str(error) + "," + str(function) + """\n""")
        e.close()
    except:
        return


def build_timezone_string(access_patterns):
        timezone_list = []
        for index in range(len(access_patterns)):
            a = [0,0,0,0,0,0,0]
            timezone_id = access_patterns[index][0]
            timezone_string = "TimezoneId=" + str(timezone_id)
            for x in range(10):
                if access_patterns[index][x+4] is not None:
                    time_from = convert_sql_date(access_patterns[index][x+4],"hh:mm")
                    time_to = convert_sql_date(access_patterns[index][x+14],"hh:mm")
                    type = access_patterns[index][x+24]
                    value = str(timezone_dec(time_from,time_to))
                    if type.lower() == "all days":
                        if a[0] < 3:
                            y = int(a[0])+1
                            timezone_string += "\t" + "SunTime%d"%(y) + "=" + str(timezone_dec(time_from,time_to))
                            a[0] +=1
                        if a[1] < 3:
                            y = int(a[1])+1
                            timezone_string += "\t" + "MonTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[1] +=1
                        if a[2] < 3:
                            y = int(a[2])+1
                            timezone_string += "\t" + "TueTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[2] +=1
                        if a[3] < 3:
                            y = int(a[3])+1
                            timezone_string += "\t" + "WedTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[3] +=1
                        if a[4] < 3:
                            y = int(a[4])+1
                            timezone_string += "\t" + "ThuTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[4] +=1
                        if a[5] < 3:
                            y = int(a[5])+1
                            timezone_string += "\t" + "FriTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[5] +=1
                        if a[6] < 3:
                            y = int(a[6])+1
                            timezone_string += "\t" + "SatTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[6] +=1
                    if type.lower() == "sunday":
                        if a[0] < 3:
                            y = int(a[0])+1
                            timezone_string += "\t" + "SunTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[0] +=1
                    if type.lower() == "monday":
                        if a[1] < 3:
                            y = int(a[1])+1
                            timezone_string += "\t" + "MonTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[1] +=1
                    if type.lower() == "tuesday":
                        if a[2] < 3:
                            y = int(a[2])+1
                            timezone_string += "\t" + "TueTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[2] +=1
                    if type.lower() == "wednesday":
                        if a[3] < 3:
                            y = int(a[3])+1
                            timezone_string += "\t" + "WedTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[3] +=1
                    if type.lower() == "thursday":
                        if a[4] < 3:
                            y = int(a[4])+1
                            timezone_string += "\t" + "ThuTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[4] +=1
                    if type.lower() == "friday":
                        if a[5] < 3:
                            y = int(a[5])+1
                            timezone_string += "\t" + "FriTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[5] +=1
                    if type.lower() == "saturday":
                        if a[6] < 3:
                            y = int(a[6])+1
                            timezone_string += "\t" + "SatTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[6] +=1
                    if type.lower() == "mon-thu":
                        if a[1] < 3:
                            y = int(a[1])+1
                            timezone_string += "\t" + "MonTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[1] +=1
                        if a[2] < 3:
                            y = int(a[2])+1
                            timezone_string += "\t" + "TueTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[2] +=1
                        if a[3] < 3:
                            y = int(a[3])+1
                            timezone_string += "\t" + "WedTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[3] +=1
                        if a[4] < 3:
                            y = int(a[4])+1
                            timezone_string += "\t" + "ThuTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[4] +=1
                    if type.lower() == "sat-sun":
                        if a[0] < 3:
                            y = int(a[0])+1
                            timezone_string += "\t" + "SunTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[0] +=1
                        if a[6] < 3:
                            y = int(a[6])+1
                            timezone_string += "\t" + "SatTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[6] +=1
                    timezone_list[len(timezone_list):] = [timezone_string]

        return timezone_list

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

def fetch_timezone_string():
        sql_text = "Select * From taccess_pattern"
        access_patterns = sqlconns.sql_select_into_list(sql_text)
        if access_patterns == -1: return -1
        timezone_string = build_timezone_string(access_patterns)
        return timezone_string

def convert_now_to_int():
    x = convert_date_to_int(datetime.datetime.now())
    return x

def convert_date_to_int(dte):
    second = int(dte.strftime("%S"))
    minute = int(dte.strftime("%M"))
    hour = int(dte.strftime("%H"))
    day = int(dte.strftime("%d"))
    month = int(dte.strftime("%m"))
    year = int(dte.strftime("%y"))
    x = ((year * 12 * 31) + ((month - 1) * 31) + (day-1))*(24*60*60) + (hour * 60 * 60) + (minute * 60) + second
    return x

def system_login_password(user, passWord): # like timeware system password except double slash
    if user.lower() != 'system': return False
    if len(passWord) != 4: return False
    day = datetime.datetime.now().strftime("%A")
    day = day[0].lower()
    month = datetime.datetime.now().strftime("%B")
    month = month[0].lower()
    if passWord[0].lower() != '/': return False
    if passWord[1].lower() != '/': return False
    if passWord[2].lower() != day: return False
    if passWord[3].lower() != month: return False
    return True







