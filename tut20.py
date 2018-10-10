exDict = {'Jack':15, 'Bob':22,'Allice':45}

#print(exDict)

#print(exDict['Jack'])

exDict['Tim'] = 15

exDict['Tim'] = 16
#print(exDict)

del exDict['Tim']

#print(exDict)

import re

'''
Identifiers

\d any number
\D anything but a number
\s space
\S anything but a space
\w any char
\W anything but a char
.  any char escept for a newline
\b the white space around words
 \. a period
 
 Modifiers:
 {1,3} we're expecting 1-3
 + Match 1 or more
 ? Match 0 or 1
 * Match 0 or more
 $ match the end of the string
 ^ match the beginning of a string
 | either or 
 [] range or "variance" [1-5A-Za-z]
(x) expecting "x" amount

White Space Characters
\n newline
\s space
\t tab
\e escape
\f form feed
\r return

DONT FORGET!
. + * ? [] $ ^ () {} | \


'''



exampleString= '''' \
Jessica is 15 years old, and Daniel is 27 years old.
Edward is 97, and his grandfather, Oscar, is 102.
'''

ages = re.findall(r'\d{1,3}',exampleString)
names = re.findall((r'[A-Z][a-z]*'), exampleString)
print(ages)
print(names)


ageDict = {}
x = 0
for eachName in names:
    ageDict[eachName] = ages[x]
    x+=1

print(ageDict)





print(int(589881173))
xxx = int(589881173)
if int(xxx) < (999999999):
    print("yoyoyo")


import base64
import tornado
import asyncore




print(base64.__all__)
print(tornado.version)


import datetime
print(datetime.datetime.now())








