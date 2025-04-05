
from __future__ import print_function
from __future__ import unicode_literals

import logging,os,unittest
from email.mime.base import MIMEBase

from .gmail import GMail,GMailWorker,GMailHandler,Message

class GMailTest(unittest.TestCase):

    def test_gmail(self):
        gmail = GMail(os.environ['GMAIL_ACCOUNT'],
                      os.environ['GMAIL_PASSWD'])
        msg1 = Message(u'GMail Test Message #1',
                       to=os.environ['GMAIL_RCPT'],
                       text=b'Hello')
        msg2 = Message(u'GMail Test Message #2',
                       to=os.environ['GMAIL_RCPT'],
                       text=b'Hello')
        msg3 = Message(u"GMail Unicod\xe9 Test",
                        to=os.environ['GMAIL_RCPT'],
                        text=u"Hello \xf8\xf9\xfa")
        msg4 = Message(u"GMail HTML + Attachment Test",
                        to=os.environ['GMAIL_RCPT'],
                        text=u"test",
                        html=u"<b>Hello \xe9\xfc\xe7",
                        attachments=[MIMEBase('application','unknown'),os.path.abspath(__file__)])
        gmail.send(msg1)
        gmail.send(msg2)
        gmail.send(msg3)
        gmail.send(msg4)
        gmail.close()

    def test_worker(self):
        gmail_worker = GMailWorker(os.environ['GMAIL_ACCOUNT'],
                                   os.environ['GMAIL_PASSWD'])
        msg1 = Message('GMailWorker Test Message #1',
                       to=os.environ['GMAIL_RCPT'],
                       text='Hello')
        msg2 = Message('GMailWorker Test Message #2',
                       to=os.environ['GMAIL_RCPT'],
                       text='Hello')
        gmail_worker.send(msg1)
        gmail_worker.send(msg2)
        gmail_worker.close()

    def test_logging(self):
        logger = logging.getLogger("GMailLogger")
        logger.setLevel(logging.DEBUG)

        gh = GMailHandler(os.environ['GMAIL_ACCOUNT'],
                          os.environ['GMAIL_PASSWD'],
                          os.environ['GMAIL_RCPT'],
                          False)

        gh.setLevel(logging.DEBUG)
        logger.addHandler(gh)

        logger.debug("Debug Message")
        logger.info("Info Message")
        logger.warning("Warn Message")
        logger.error("Error Message")

        try:
            1/0
        except Exception as e:
            logger.exception(e)

        gh.close()

    def test_logging_bg(self):
        logger = logging.getLogger("GMailBackgroundLogger")
        logger.setLevel(logging.DEBUG)

        gh = GMailHandler(os.environ['GMAIL_ACCOUNT'],
                          os.environ['GMAIL_PASSWD'],
                          os.environ['GMAIL_RCPT'],
                          True)

        gh.setLevel(logging.DEBUG)
        logger.addHandler(gh)

        logger.error("Background Error Message")

        gh.close()

if __name__ == '__main__':
    if os.getenv('GMAIL_ACCOUNT') and os.getenv('GMAIL_PASSWD') and os.getenv('GMAIL_RCPT'):
        unittest.main()
    else:
        print("Must set GMAIL_ACCOUNT, GMAIL_PASSWD, GMAIL_RCPT environment variables")
    
