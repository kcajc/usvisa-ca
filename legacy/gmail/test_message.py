
from __future__ import print_function
from __future__ import unicode_literals

import os,unittest
from email.mime.base import MIMEBase
from textwrap import dedent

from .gmail import Message

class MessageTest(unittest.TestCase):

    def test_simple(self):
        m = Message("Simple",to="xyz@xyz.com",cc="abc@abc.com",bcc="bcc@bcc.com",text=b"text")
        self.assertEqual(m.as_string().strip(),
                         dedent("""
                                    Content-Type: text/plain; charset="us-ascii"
                                    MIME-Version: 1.0
                                    Content-Transfer-Encoding: 7bit
                                    To: xyz@xyz.com
                                    Cc: abc@abc.com
                                    Bcc: bcc@bcc.com
                                    Subject: Simple

                                    text
                                """).strip())

    def test_unicode(self):
        m = Message(u"Unicod\xe9",to="xyz@xyz.com",text=u"Hello \xf8\xf9\xfa")
        self.assertEqual(m.as_string().strip(),
                         dedent("""
                                     Content-Type: text/plain; charset="utf-8"
                                     MIME-Version: 1.0
                                     Content-Transfer-Encoding: base64
                                     To: xyz@xyz.com
                                     Subject: =?utf-8?q?Unicod=C3=A9?=

                                     SGVsbG8gw7jDucO6
                                """).strip())

    def test_html(self):
         m = Message(u"HTML",to="xyz@xyz.com",text="text",html="html")
         self.assertEqual([ p.get_content_type() for p in m.walk() ],
                          ['multipart/mixed','multipart/alternative','text/plain','text/html'])

    def test_attachment(self):
         m = Message(u"Attachment",to="xyz@xyz.com",text="text",html="html",
                           attachments=[MIMEBase('application','unknown'),os.path.abspath(__file__)])
         self.assertEqual([ p.get_content_type() for p in m.walk() ],
                          ['multipart/mixed','multipart/alternative','text/plain',
                              'text/html','application/unknown','text/x-python'])

if __name__ == '__main__':
    unittest.main()
    
