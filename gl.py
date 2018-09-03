import os

SERVER = ""
DATABASE = "python_time"
SQL_LOGIN = ""
PASSWORD = ""
python_sql = ""

#iface server globals
server_port = 82
face_to_personnel = False

access_terminal_configuration = "4"

logo_path = "python.PNG"
small_icon_path = "python_small.ico"

'window control'
personnel_screen_open = 0
advanced_options_open = 0

'last employee viewed'
last_employee_viewed = 0

#system parameters
COMM_TIMEOUT = "5000"
SPOOL_TRANSACTIONS=""
LOG_COMMS_FAILURES=""

#error logs
#log file names
#this line gives you the working folder which is inside the library ZIP
#Replace the library.zip part of the path with null
SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__)) + "\\"
#if you ever need to run inbio communicator as an application again put this line back in
#if not "library" in SCRIPT_ROOT: SCRIPT_ROOT = ""
SCRIPT_ROOT=SCRIPT_ROOT.replace("library.zip","")
SCRIPT_ROOT=SCRIPT_ROOT.replace("iface analyser.exe","")
SCRIPT_ROOT=SCRIPT_ROOT.replace("adp.exe","")
SCRIPT_ROOT=SCRIPT_ROOT.replace("inbio config.exe","")

COMM_ERROR_LOG = SCRIPT_ROOT+"communications.log"
ERROR_LOG = SCRIPT_ROOT + "error.log"
SPOOL_LOG = SCRIPT_ROOT + "spool.log"
GENERAL_INI = SCRIPT_ROOT + "general.ini"
ADP_INI = SCRIPT_ROOT + "adp.ini"
LICENSE_TXT = SCRIPT_ROOT + "license.txt"

