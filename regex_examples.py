
#Identifiers
#\d = any number
#\D = anything but a number
#\s = space
#\S = anything but a space
#\w = any letter
#\W = anything but a letter
#. = any character, except for a new line
#\b = space around whole words
#\. = period. must use backslash, because . normally means any character.
#Modifiers:
#{1,3} = for digits, u expect 1-3 counts of digits, or “places”
#+ = match 1 or more
#? = match 0 or 1 repetitions.
#* = match 0 or MORE repetitions
#$ = matches at the end of string
#^ = matches start of a string
#| = matches either/or. Example x|y = will match either x or y
#[] = range, or “variance”
#{x} = expect to see this amount of the preceding code.
#{x,y} = expect to see this x-y amounts of the precedng code
#White Space Charts:
#\n = new line
#\s = space
#\t = tab
#\e = escape
#\f = form feed
#\r = carriage return
#Characters to REMEMBER TO ESCAPE IF USED!
#. + * ? [ ] $ ^ ( ) { } | \
#Brackets:
#[] = quant[ia]tative = will find either quantitative, or quantatative.
#[a-z] = return any lowercase letter a-z
#[1-5a-qA-Z] = return all numbers 1-5, lowercase letters a-q and uppercase A-Z

import re
import string
exampleLine = "prices xom 91.43-91.44/vz50-50.01/s 7.23-7.24"
regEx = re.findall(r'\w{1,3}\s?\d{1,2}\.?\d{0,2}-\d{1,2}\.?\d{0,2}',exampleLine)
for regy in regEx:
    print(regy)
print(regEx)


exampleString= '''
Jessica is 15 years old, and Daniel is 27 years old,
Edward is 97 and grandfather, Oscar, is 102
'''

ages = re.findall(r'\d{1,3}',exampleString)

def timezone_difference(dte,tx):
    list = tx.splitlines()
    time_adj = 0
    for n in range(len(list)):
        print('line = ',list[n])
        if 'timezone' in list[n]:
            try:
                time_adj = int(list[n].split("=")[1])
            except Exception as e:
                time_adj=0
            print('adj = ', time_adj)
            if time_adj != 0: dte = dte - timedelta(hours = (-time_adj))
    return dte

tx = '''
jhfjhf
jkhdsjhdjh
kldjkd
198346t5734y128742



timezone=1
kfjkf
klflkfg
'''

import reverse_geocode

coords = (54.513918),(-6.074368)
print(reverse_geocode.search(coords))