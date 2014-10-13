#!/usr/bin/env python

import sys
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def main():
    if len(sys.argv) < 3:
      print "Usage: %s <from email> <to email>", sys.argv[0]
      sys.exit(1)

    f = open('mail.html', 'r')
    content = f.read()
    f.close()

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Weekly Review Metrics"
    msg['From'] = sys.argv[1]
    msg['To'] = sys.argv[2]

    text = "The weekly log does not support plain-text (yet)."
    # Hang off mail.html as attachment.

    html = content
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP('localhost')
    s.sendmail(me, you, msg.as_string())
    s.quit()

if __name__ == "__main__":
    main()
