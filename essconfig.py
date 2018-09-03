import sys

import fileinput


if len(sys.argv) != 4:
    print("UPDATEESS [SERVERNAME] [USERNAME] [PASSWORD]")
    sys.exit(2)

server = sys.argv[1]
user_name = sys.argv[2]
password = sys.argv[3]

try:
     fileToSearch = 'c:/inetpub/wwwroot/nmd3/ess/web.config'

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
          for line in file:
               print(line.replace('PROG-DEV51', server), end='')

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
          for line in file:
               print(line.replace('User ID=sa', 'User ID=' + user_name), end='')

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
          for line in file:
               print(line.replace('Password=39steps', 'Password=' + password), end='')

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
          for line in file:
               print(line.replace('user ID=sa', 'user ID=' + user_name), end='')

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
          for line in file:
               print(line.replace('password=39steps', 'password=' + password), end='')

     fileToSearch = 'c:/inetpub/wwwroot/nmd3/twc/web.config'

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
          for line in file:
               print(line.replace('PROG-DEV51', server), end='')

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
          for line in file:
               print(line.replace('User ID=sa', 'User ID=' + user_name), end='')

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
          for line in file:
               print(line.replace('Password=39steps', 'Password=' + password), end='')

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace('user ID=sa', 'user ID=' + user_name), end='')

     with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace('password=39steps', 'password=' + password), end='')

except Exception as e:
     print(e)
     sys.exit(2)

print("config files successfully updated, if you need to do this again it will have to be a manual change.")