#! /usr/bin/env python

import poplib
from cStringIO import StringIO
import email

def showMessage(msg):
    if msg.is_multipart():
        for part in msg.get_payload():
            showMessage( part )
    else:
        types = msg.get_content_type()
        if types=='text/plain':
            try:
               body =msg.get_payload(decode=True)
               print body
            except:
               print '[*001*]BLANK'
               
        elif types=='text/base64':
            try:
               body = base64.decodestring(msg.get_payload())
               print body
            except:
               print '[*001*]BLANK'

def list_mail(host, username, password):
    pp = poplib.POP3(host)
    pp.user(username)
    pp.pass_(password)
    (numMessages, _) = pp.stat()
    for i in xrange(1):
    #for i in xrange(numMessages):
        m = pp.retr(i + 1)
        buf = StringIO()
        for j in m[1]:
            print >>buf, j
        buf.seek(0)
        msg = email.message_from_file(buf)
        #print msg.keys()
        (subject, encoding) = email.Header.decode_header(msg['Subject'])[0]
        From = email.Header.decode_header(msg['From'])[0][0]
        To = email.Header.decode_header(msg['To'])[0][0]
        if encoding:
            print '%d [ %s => %s ] : %s ' % (i + 1, From, To, subject.decode(encoding).encode('utf-8'))
        else:
            print '%d [ %s => %s ] : %s ' % (i + 1, From, To, subject)
        showMessage(msg)
    pp.quit()

def main():
    (host, user, passwd) = ('pop.126.com', 'NNN', 'NNN')
    list_mail(host, user, passwd)

if __name__ == '__main__':
    main()
