import msoffcrypto

file = msoffcrypto.OfficeFile(open("daznotes.docx", "rb"))

#file = msoffcrypto.OfficeFile(open("1.docx", "rb"))

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ1234567890!"

import string, itertools

# This piece of code does not mean to be fully workable
# due to SoloLearn Code Playground limitations..
import itertools
import string
import multiprocessing

# charset will contain letters, numbers
# and punctuation marks..
#charset = string.ascii_letters + string.digits + string.punctuation

# this charset contains only uppercase letters...
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ123456789!"

password = "SOLO"



bool = False

def brute(n):
    global bool
    for pwd in itertools.product(charset, repeat=n):
        if bool: break
        test = ''.join(pwd)
       # print(test)
        try:
            file.load_key(password=test)
            file.decrypt(open("decrypted.docx", "wb"))
            print('SUCCESS',test)
            bool = True
            break
        except:
            print('FAIL',test)

'8'
if __name__ == '__main__':
    brute(8)
   # for n in range(4,20):
    #    jobs = []
     #   p = multiprocessing.Process(target=brute, args=(n,))
      #  jobs.append(p)
       # p.start()

