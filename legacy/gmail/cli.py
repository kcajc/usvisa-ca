
from __future__ import print_function
from __future__ import unicode_literals

import os 

from .gmail import GMail
from .message import Message

def cli():
    import argparse,getpass,mimetypes,sys

    parser = argparse.ArgumentParser(description='Send email message via GMail account')
    parser.add_argument('--username','-u',default=os.environ.get('GMAIL_ACCOUNT'),
                                help='GMail Username (Default: $GMAIL_ACCOUNT)')
    parser.add_argument('--password','-p',default=os.environ.get('GMAIL_PASSWD'),
                                help='GMail Password (Default: $GMAIL_PASSWD)')
    parser.add_argument('--to','-t',required=True,action='append',default=[],
                                help='To (multiple allowed)')
    parser.add_argument('--cc','-c',action='append',default=[],
                                help='Cc (multiple allowed)')
    parser.add_argument('--subject','-s',required=True,
                                help='Subject')
    parser.add_argument('--body','-b',
                                help='Message Body (text)')
    parser.add_argument('--html','-l',default=None,
                                help='Message Body (html)')
    parser.add_argument('--attachment','-a',action='append',default=[],
                                help='Attachment (multiple allowed)')
    parser.add_argument('--debug','-d',action='store_true',default=False,
                                help='Debug')

    results = parser.parse_args()

    if results.password is None:
        results.password = getpass.getpass("Password:")

    if results.body is None and results.html is None:
        results.body = sys.stdin.read()

    gmail = GMail(username=results.username,
                  password=results.password,
                  debug=results.debug)
    msg = Message(subject=results.subject,
                  to=",".join(results.to),
                  cc=",".join(results.cc),
                  text=results.body,
                  html=results.html,
                  attachments=results.attachment)
    gmail.send(msg)
    gmail.close()

if __name__ == '__main__':
    cli()

