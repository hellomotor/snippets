#! /usr/bin/env python

import poplib
from cStringIO import StringIO
import email

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
    pp.quit()

def main():
    (host, user, passwd) = ('pop.126.com', 'NNN', 'NNN')
    list_mail(host, user, passwd)

if __name__ == '__main__':
    main()
