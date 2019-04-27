

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
import sqlconns

print(sqlconns.decrypt_with_key(xx))


xlist = (1,2,3,4,5,6,7,8,9)

print(sum(xlist))
#is the same as
x = 0
for number in xlist:
    x += number

print(x)