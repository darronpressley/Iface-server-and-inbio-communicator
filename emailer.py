import os, re
import sys
import smtplib
 
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

#####exhcnage version
useraccount = "darron.pressley"
sender = 'darron.pressley@northtimeanddata.co.uk'
password = "Sky6fall!ng"
recipient = 'darronpressley@gmail.com'
subject = 'Timeware Alert - Urgent'
test_message = 'The following Items require your attention.\n'


useraccount = "darronpressley@gmail.com"
sender = 'darronpressley@gmail.com'
password = "Starfall9"
recipient = 'Darronpressley@gmail.com'
subject = 'Timeware Alert - Urgent'
test_message = "hey man how you do\n"
directory = "c:/temp"
 
def email_test():
    msg = MIMEMultipart()
    msg['Subject'] = 'Python emaillib Test'
    msg['To'] = recipient
    msg['From'] = sender
    files = os.listdir(directory)
    gifsearch = re.compile(".gif", re.IGNORECASE)
    files = filter(gifsearch.search, files)
    for filename in files:
        #path = os.path.join(directory, filename)
        if not os.path.isfile("C:/temp/message.txt"):
            continue
        img = MIMEImage(open("C:/temp/message.txt", 'rb').read(), _subtype="gif")
        img.add_header('Content-Disposition', 'attachment', filename=filename)
        #msg.attach(img)
    part = MIMEText('text', "plain")
    part.set_payload(test_message)
    msg.attach(part)
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(useraccount, password)

    session.sendmail(sender, recipient, msg.as_string())
    session.quit()


def email_txt(message,address):
    msg = MIMEMultipart()
    msg['Subject'] = 'Python emaillib Test'
    msg['To'] = address
    msg['From'] = sender
    part = MIMEText('text', "plain")
    part.set_payload(message)
    msg.attach(part)
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(useraccount, password)
    session.sendmail(sender, recipient, msg.as_string())
    session.quit()

email_test()
