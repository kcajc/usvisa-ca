
from __future__ import print_function
from __future__ import unicode_literals

import logging
from multiprocessing import Process
try:
    from multiprocessing import SimpleQueue
except ImportError:
    from multiprocessing.queues import SimpleQueue
import os.path
import smtplib
import time

from email.utils import formatdate,make_msgid,getaddresses,parseaddr
from smtplib import SMTPResponseException,SMTPServerDisconnected,SMTPAuthenticationError

from .message import Message

class GMail(object):

    """
        GMail SMTP sender

        Basic usage:

        >>> gmail = GMail('A.User <user@gmail.com>','password')
        >>> msg = Message('Test Message',to='xyz <xyz@xyz.com>',text='Hello')
        >>> gmail.send(msg)

    """

    def __init__(self,username,password,debug=False):
        """
            GMail SMTP connection

            username    : GMail username 
                          This can either be a simple address ('user@gmail.com') 
                          or can include a name ('"A User" <user@gmail.com>').
                          
                          The username specified is used as the sender address

            password    : GMail password
            debug       : Debug flag (passed to smtplib)

            The SMTP connection is not opened automatically and requires that
            'connect' is called (the 'send' method will check if the connection
            is open and connect if required). The connection is kept open
            between calls to 'send' to avoid start-up latency and should be
            closed manually if required.

        """
        # Default GMail SMTP address/port
        self.server = 'smtp.gmail.com'
        self.port = 587
        # Parse address component of username
        self.username = parseaddr(username)[1]
        self.password = password
        self.sender = username
        self.debug = debug
        self.session = None

    def connect(self):
        """
            Connect to GMail SMTP service using smtplib
        """
        self.session = smtplib.SMTP(self.server,self.port)
        self.session.set_debuglevel(self.debug)
        self.session.ehlo()
        self.session.starttls()
        self.session.ehlo()
        self.session.login(self.username,self.password)

    def send(self,message,rcpt=None):
        """
            message         : email.Message instance
            rcpt            : List of recipients (normally parsed from
                              To/Cc/Bcc fields)

            Send message
        """
        # Check if connected and connect if false
        if not self.is_connected():
            self.connect()
        # Extract recipients
        if rcpt is None:
            rcpt = [ addr[1] for addr in getaddresses((message.get_all('To') or []) + 
                                                      (message.get_all('Cc') or []) + 
                                                      (message.get_all('Bcc') or [])) ]
        # Fill in message fileds if not already set
        # NOTE: this modifies the original message and in particular deletes the Bcc field
        if message['From'] is None:
            message['From'] = self.sender
        if message['Reply-To'] is None:
            message['Reply-To'] = self.sender
        if message['Date'] is None:
            message['Date'] = formatdate(time.time(),localtime=True)
        if message['Message-ID'] is None:
            message['Message-ID'] = make_msgid()
        del message['Bcc']

        # Send message
        self.session.sendmail(self.sender,rcpt,message.as_string())

    def is_connected(self):
        """
            Check is session connected - initially by checking session instance and
            then sending NOOP to validate connection

            Sets self.session to None if connection has been closed
        """
        if self.session is None:
            return False
        try:
            rcode,msg = self.session.noop()
            if rcode == 250:
                return True
            else:
                self.session = None
                return False
        except (SMTPServerDisconnected,SMTPResponseException):
            self.session = None
            return False
            
    def close(self):
        """
            Close SMTP connection
        """
        if self.is_connected():
            self.session.quit()
            self.session = None

    def __del__(self):
        """
            Close session on delete
        """
        self.close()

def _gmail_worker(username,password,queue,debug=False):
    gmail = GMail(username,password,debug)
    gmail.connect()
    while True:
        try:
            msg,rcpt = queue.get()
            if msg == 'QUIT':
                break
            gmail.send(msg,rcpt)
        except SMTPServerDisconnected:
            gmail.connect()
            gmail.send(msg,rcpt)
        except SMTPResponseException:
            pass
        except KeyboardInterrupt:
            break
    gmail.close()

class GMailWorker(object):

    """
        Background GMail SMTP sender

        This class runs a GMail connection object in the background (using 
        the multiprocessing module) which accepts messages through a 
        simple queue. No feedback is provided.

        The worker object should be closed on exit (will otherwise prevent
        the interpreter from exiting).

        The object provides a similar api to the Gmail object.

        Basic usage:

        >>> gmail_worker = GMailWorker('A.User <user@gmail.com>','password')
        >>> msg = Message('Test Message',to='xyz <xyz@xyz.com',text='Hello')
        >>> gmail_worker.send(msg)
        >>> gmail_worker.close()

    """
    def __init__(self,username,password,debug=False):
        """
            GMail SMTP connection worker

            username    : GMail username 
                          This can either be a simple address ('user@gmail.com') 
                          or can include a name ('"A User" <user@gmail.com>').
                          
                          The username specified is used as the sender address

            password    : GMail password
            debug       : Debug flag (passed to smtplib)

            Runs '_gmail_worker' helper in background using multiprocessing
            module.

            '_gmail_worker' loops listening for new message objects on the
            shared queue and sends these using the GMail SMTP connection.
        """
        self.queue = SimpleQueue()
        self.worker = Process(target=_gmail_worker,args=(username,password,self.queue,debug))
        self.worker.start()

    def send(self,message,rcpt=None):
        """
            message         : email.Message instance
            rcpt            : List of recipients (normally parsed from
                              To/Cc/Bcc fields)

            Send message object via background worker
        """
        self.queue.put((message,rcpt))

    def close(self):
        """
            Close down background worker
        """
        self.queue.put(('QUIT',None))

    def __del__(self):
        self.close()

class GMailHandler(logging.Handler):
    """
        GMailHandler provides a handler for the 'logging' framework. The 
        handler should be setup/configured as a normal logging handler.

        The handler can either send messages in the foreground or background
        (using GMailHandler). To avoid impacting application performance
        it is normally run in the background (though this can be overridden).

        The format of the log messages can be changed by setting a formatter
        object as normal. In addition the Subject iformat can be specified
        using the setSubjectFormatter() method.

        >>> logger = logging.getLogger("GMailLogger")
        >>> logger.setLevel(logging.DEBUG)
        >>> gh = GMailHandler('A.User <user@gmail.com>','password','Log Recipient <xxx@yyy.zzz>')
    """

    def __init__(self,username,password,to,bg=True):
        logging.Handler.__init__(self)
        if bg:
            self.gmail= GMailWorker(username,password)
        else:
            self.gmail= GMail(username,password)
        self.to = to
        self.formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        self.subject_formatter = logging.Formatter('[%(levelname)s] %(message).40s')

    def setSubjectFormatter(self,f):
        self.subject_formatter = f

    def emit(self,record):
        try:
            msg = Message(subject=self.subject_formatter.format(record).split("\n")[0],
                          to=self.to,
                          text=self.format(record))
            self.gmail.send(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self.gmail.close()

    def __del__(self):
        self.close()
