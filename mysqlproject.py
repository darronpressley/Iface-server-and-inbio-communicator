#import pyodbc
#import re #RegEx library
import sqlconns
import decimal

sqlconns.sqlselect("select count(*) as foo FROM temployee where employee_status_id <> 8")

sqlconns.sqlselect("UPDATE temployee SET employee_status_id = 8")

sqlconns.sqlselect("select count(*) as foo FROM temployee where employee_status_id <> 8")

input("press Enter to continue")
