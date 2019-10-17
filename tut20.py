

value1 = "hello"

new_word = ''
for char in reversed(value1):
    new_word += char



print(new_word)


value1 = value1[::-1]
print(value1)


from statistics import mode
import datetime
z = 1234567688890

print(datetime.datetime.now())
print(mode(str(z)))
print(datetime.datetime.now())

xx = 'ZgCiQIUbDfZpu9G2ko1QVw=='
xx = 'aByVouKtwcq/8f0qtFRLmA=='
xx = 'n1nD3ZsuYHu/71LrVyuXPg=='
import sqlconns

print(sqlconns.decrypt_with_key(xx))


xlist = (1,2,3,4,5,6,7,8,9)

print(sum(xlist))
#is the same as
x = 0
for number in xlist:
    x += number

x = {'timezone87': [b'0'], 'uface89': [b'on'], 'timezone88': [b'0'], 'timezone85': [b'0'], 'timezone82': [b'0'], 'timezone92': [b'0'], 'timezone83': [b'0'], 'timezone86': [b'0'], 'submit': [b'Commit to Database'], 'timezone74': [b'0'], 'timezone93': [b'0'], 'timezone89': [b'0'], 'timezone81': [b'0'], 'timezone80': [b'0'], 'timezone91': [b'0'], 'timezone90': [b'0']}

print(type(x))

def get_terminal_options_flags(x, terminal_id):
    uface = "0"
    prox = "0"
    nophoto = "0"
    noface = "0"
    nofinger = "0"
    notime = "0"
    timezone = "0"
    value = x.get('uface' + terminal_id, "0")
    if value != "0": uface = "1"
    value = x.get('prox' + terminal_id, "0")
    if value != "0": prox = "1"
    value = x.get('nophoto' + terminal_id, "0")
    if value != "0": nophoto = "1"
    value = x.get('noface' + terminal_id, "0")
    if value != "0": noface = "1"
    value = x.get('nofinger' + terminal_id, "0")
    if value != "0": nofinger = "1"
    value = x.get('notime' + terminal_id, "0")
    if value != "0": notime = "1"
    value = x.get('timezone' + terminal_id, "0")
    if value != "0": timezone = value[0].decode()

    return uface, prox, nophoto, noface, nofinger, notime, timezone

#val for key, val in my_dict.iteritems() if key.startswith('Date'))
for key, value in x.items():
    if 'timezone' in key:
        terminal_id = str.replace(key, 'timezone','')
        uface, prox, nophoto, noface, nofinger, notime, timezone = get_terminal_options_flags(x, terminal_id)
        print(uface, notime, prox, nophoto, noface, nofinger, notime, timezone)

        print(key,value, terminal_id, uface)


import functions as f

print(f.system_login_password('system','//f5m'))