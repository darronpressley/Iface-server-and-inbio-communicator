import pyodbc as p
from Crypto.Cipher import AES  # Dependency: install pycrypto - available at pypi: pip install pycrypto
import base64
import os
import gl
import functions as f

def sqlselect(sql):
    server = 'YEAH'
    database = 'timeware_main_6'
    table = 'temployee'
    Col1 = 'first_name'
    Col2 = 'last_name'
    Col3 = 'badge'
    # need to find a way to encrypt this into a file
    connstr = (r'DRIVER={SQL Server};SERVER=' +
               server + ';DATABASE=' + database + ';' +
               'UID=sa;PWD=Sky6fall!ng;')
    conn = p.connect(connstr)
    dbcursor = conn.cursor()
    dbcursor.execute(sql)
    if 'SELECT' in sql.upper():
        for row in dbcursor.fetchall():
            for col in row:
                print(col)
            print()
    elif 'UPDATE' in sql.upper():
        conn.commit()
    conn.close()
    return 0


def sql_select_into_list(sql):
    try:
        conn = p.connect(gl.python_sql)
        dbcursor = conn.cursor()
        dbcursor.execute(sql)
        sql_list = dbcursor.fetchall()
        conn.close()
    except Exception as e:
        f.error_logging("functions",e,"sql",sql)
        return -1
    return sql_list

def sql_select(sql,*args):
    try:
        conn = p.connect(gl.python_sql)
        dbcursor = conn.cursor()
        dbcursor.execute(sql,*args)
        sql_list = dbcursor.fetchall()
        conn.close()
    except Exception as e:
        f.error_logging("functions",e,"sql",sql)
        return -1
    return sql_list


def sql_select_single_field(sql):
#note use of fecthone
    try:
        data = ""
        conn = p.connect(gl.python_sql)
        dbcursor = conn.cursor()
        dbcursor.execute(sql)
        row = dbcursor.fetchone()
        if row:
            data = str(row[0])
        conn.close()
    except Exception as e:
        f.error_logging("functions",e,"sql",sql)
        return -1
    return data


def sql_command(sql,*args):
    try:
        conn = p.connect(gl.python_sql)
        dbcursor = conn.cursor()
        dbcursor.execute(sql,*args)
        conn.commit()
    except Exception as e:
        f.error_logging("functions",e,"sql",sql)
        print(e)
        return -1
    return 0

def sql_command_args(sql,*args):
    try:
        conn = p.connect(gl.python_sql)
        dbcursor = conn.cursor()
        dbcursor.execute(sql,*args)
        conn.commit()
    except Exception as e:
        f.error_logging("functions",e,"sql",sql)
        return -1
    return 0

def testsql(server, sql_login, password, database):
    global python_sql
    connstr = (r'DRIVER={SQL Server};SERVER=' +
               server + ';DATABASE=' + database + ';' +
               'UID='+sql_login+';PWD='+password+';')
    gl.python_sql = connstr
    try:
        conn = p.connect(connstr)
    except:
        return 0
    conn.close()
    return 1


def writesql_connection(gl_SERVER,gl_SQL_LOGIN,gl_PASSWORD,gl_DATABASE):
#1 find out if there is an ini file
#2 find out if there is a line for this database
#3 create the file or change the line
    if os.path.isfile('database.ini'):
        try:
            #test if you can open it for writing, if not error out
            fob=open('database.ini', 'w')
            fob.close()
            fob=open('database.ini', 'r')
            try:
                listme=fob.readlines()
                fob.close()
                notinlist=1
                for position, item in enumerate(listme):
                    if gl_DATABASE.lower() in str(item).lower():
                        notinlist=0
                        listme[position]=(gl_SERVER+","+(encryption(gl_SQL_LOGIN))+","+(encryption(gl_PASSWORD))+","+gl_DATABASE+"\n")
                        fob=open('database.ini', 'w')
                        fob.writelines(listme)
                        fob.close()
                if notinlist==1:
                    fob=open('database.ini', 'a')
                    fob.write(gl_SERVER+","+(encryption(gl_SQL_LOGIN))+","+(encryption(gl_PASSWORD))+","+gl_DATABASE+"\n")
                    fob.close()
            finally:
                fob.close()
                return 1
        except IOError:
            return 0
    else:
        try:
            fob=open('database.ini', 'w')
            try:
                fob.write(gl_SERVER+","+(encryption(gl_SQL_LOGIN))+","+(encryption(gl_PASSWORD))+","+gl_DATABASE+"\n")
            finally:
                fob.close()
                return 1
        except IOError:
            return 0


def readsql_connection():
    fob=open("database.ini", "r")
    listme = fob.readlines()
    fob.close()
    for position, item in enumerate(listme):
        if "python_time".lower() in str(item).lower():
            list1 = str(item).split(",")
            gl.SERVER = list1[0]
            gl.SQL_LOGIN = decrypt_with_key(list1[1])
            gl.PASSWORD = decrypt_with_key(list1[2])
            gl.DATABASE = "python_time"
            return 1
        else:
            return 0


def readsql_connection_timeware_main_6():
    fob=open(gl.SCRIPT_ROOT + "database.ini", "r")
    listme = fob.readlines()
    fob.close()
    for position, item in enumerate(listme):
        if "timeware_main_6".lower() in str(item).lower():
            list1 = str(item).split(",")
            gl.SERVER = list1[0]
            gl.SQL_LOGIN = decrypt_with_key(list1[1])
            gl.PASSWORD = decrypt_with_key(list1[2])
            gl.DATABASE = "timeware_main_6"
            return 1
        else:
            return 0


def encryption(privateInfo):
    """ Method to encrypt your message using AES encryption"""
    BLOCK_SIZE = 16
    PADDING = '{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    #secret = os.urandom(BLOCK_SIZE)  # Comment this line and uncomment line below to use hard-coded key
    secret = b'\xf9J\xa4\xd1\t\x17\xb8\xabt\xfe\x06\x96\xe3\xe8(.'
    #print('Encryption key:', secret)
    cipher = AES.new(secret)
    encoded = EncodeAES(cipher, privateInfo)
    return(encoded.decode('UTF-8'))


def decrypt_with_key(encryptedString):
    """ Method to decrypt message using a decryptionn key passed in as a parameter """
    key= b'\xf9J\xa4\xd1\t\x17\xb8\xabt\xfe\x06\x96\xe3\xe8(.'
    PADDING = '{'
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).decode('utf-8').rstrip(PADDING)
    cipher = AES.new(key)
    decoded = DecodeAES(cipher, encryptedString)
    return(decoded)

    




 




