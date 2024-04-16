
from __future__ import print_function
from __future__ import unicode_literals

import os,sys

from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mimetypes import guess_type

if sys.version_info[0] == 2:
    unicode_type = unicode
else:
    unicode_type = str

class Message(object):
    """
        Wrapper around email.Message class simplifying creation of simple email
        message objects.

        Allows most basic email messages types (including text, html &
        attachments) to be created simply from constructor. More complex
        messages should be created using the email.mime classes directly

        Class wraps the email.Message class and delegates item/attr lookups
        to the wrapped class (allows the object to be treated as a MIMEBase
        instance even though it doesnt inherit from this)

        Basic usage:

        >>> msg = Message('Test Message',to='xyz@xyz.com',text="Hello",html="<b>Hello</b>",attachments=['img.jpg'])

    """

    def __init__(self,subject,to,cc=None,bcc=None,text=None,html=None,
                 attachments=None, sender=None, reply_to=None):
        """
            Create message object

            subject         : Subject field
            to              : To recipients (as string - eg. "A <a@xyz.com>, B <b@xyz.com>")
            cc              : Cc recipients (same format as to)
            bcc             : Bcc recipients (same format as to)
            text            : Plain text body
            html            : HTML body ('text' will be included as alternative)
            attachments     : List of attachments - if the item is a subclass of MIMEBase
                              this is inserted directly, otherwise it is assumed to be
                              a filename and a MIME attachment craeted guessing the
                              content-type (for detailed control of the attachment
                              parameters create these separately)
            sender          : Value for the 'From' header (e.g. Foo Barr <info@example.com>).
                              If specified, 'Reply-To' header is also set to this address.
            reply_to        : Value for the 'Reply-To' header.

        """
        if not html and not attachments:
            # Simple plain text email
            self.root = MIMEText(text,'plain',self._charset(text))
        else:
            # Multipart message
            self.root = MIMEMultipart()
            if html:
                # Add html & plain text alernative parts
                alt = MIMEMultipart('alternative')
                alt.attach(MIMEText(text,'plain',self._charset(text)))
                alt.attach(MIMEText(html,'html',self._charset(html)))
                self.root.attach(alt)
            else:
                # Just add plain text part
                txt = MIMEText(text,'plain',self._charset(text))
                self.root.attach(txt)
            # Add attachments
            for a in attachments or []:
                self.root.attach(self._attachment(a))
        # Set headers
        self.root['To'] = to
        if cc: self.root['Cc'] = cc
        if bcc: self.root['Bcc'] = bcc

        if sender:
            self.root['From'] = sender

            if not reply_to:
                # If 'Reply-To' is not provided, set it to the 'From' value
                self.root['Reply-To'] = sender

        if reply_to:
            self.root['Reply-To'] = reply_to

        self.root['Subject'] = subject

    def _charset(self,s):
        """
            Guess charset - assume ascii for text and force utf-8 for unicode
            (email.mime classes take care of encoding)
        """
        return 'utf-8' if isinstance(s,unicode_type) else 'us-ascii'

    def _attachment(self,a):
        """
            Create MIME attachment
        """
        if isinstance(a,MIMEBase):
            # Already MIME object - return
            return a
        else:
            # Assume filename - guess mime-type from extension and return MIME object
            main,sub = (guess_type(a)[0] or 'application/octet-stream').split('/',1)
            attachment = MIMEBase(main,sub)
            with open(a,'rb') as f:
                attachment.set_payload(f.read())
            if sys.version_info[0] == 2:
                # Try to handle non-ascii filenames
                attachment.add_header('Content-Disposition','attachment',
                        filename=unicode(os.path.basename(a),sys.getfilesystemencoding()))
            else:
                attachment.add_header('Content-Disposition','attachment',
                        filename=os.path.basename(a))
            encode_base64(attachment)
            return attachment

    # Delegate to root MIME object (allows object to be treated as MIMEBase)

    def __getitem__(self,key):
        return self.root.__getitem__(key)

    def __setitem__(self,key,value):
        self.root.__setitem__(key,value)

    def __delitem__(self,key):
        return self.root.__delitem__(key)

    def __getattr__(self,attr):
        if attr != 'root':
            return getattr(self.root,attr)

