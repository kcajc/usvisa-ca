
from __future__ import print_function
from __future__ import unicode_literals

from .gmail import GMail,GMailWorker,GMailHandler
from .message import Message

version = "0.6.3"
description = """
        
    gmail
    -----

    The 'gmail' module provides a simple wrapper around the smtplib/email
    modules to provide an easy programmatic interface for sending email using
    the GMail SMTP service.

    The module provides the following classes:

    GMail           - Basic interface to GMail SMTP service 
    GMailWorker     - Background worker to send messages asynchronously 
                      (uses multiprocessing module)
    GMailHandler    - GMail handler for logging framework
    Message         - Wrapper around email.Message class simplifying
                      creation of email message objects

    The module also provides a cli interface to send email if run directly
    (python -mgmail.cli)
    
    Basic usage:

    >>> gmail = GMail('A.User <user@gmail.com>','password')
    >>> msg = Message('Test Message',to='xyz <xyz@xyz.com>',text='Hello')
    >>> gmail.send(msg)

    Note: You will need to setup an application-specific password rather
          than using your account-password - see:
          
            https://support.google.com/mail/?p=InvalidSecondFactor
            https://security.google.com/settings/security/apppasswords

    The Message class also provides support to simply generate html email and
    add attachments.

    >>> msg = Message('Test Message',to='xyz@xyz.com',text="Hello",html="<b>Hello</b>",attachments=['img.jpg'])

    In Python3 messages will be unicode (utf8) encoded by default unless the
    text is passed a a bytes object (the inverse is true in Python 2)

    For examples of use see cli.py and test_gmail.py/test_message.py

    Changelog:

        *   0.1     2012-10-17  Initial Release
        *   0.2     2012-10-18  Restructure module
        *   0.3     2012-12-28  Fix logging/worker 
        *   0.3.1   2012-12-28  CLI attachment mime-type fix
        *   0.4     2013-08-24  Allow user to specify 'From' and 'Reply-To' header by passing 'sender'
                                (Pull from from https://github.com/Kami - thanks)
        *   0.5     2014-02-12  Move _gmail_worker to module function to fix 
                                multiprocessor problem on win32 
                                (Fix from gabriel.nevarez@gmail.com - thanks)
        *   0.6.1   2016-09-25  Python 3 support
        *   0.6.2   2016-12-12  Fix to Python 3 exception handling
        *   0.6.3   2017-08-07  Try to handle non-ascii filenames
                                Fix for exception on `__del__` Method Invocation
                                (thanks to https://github.com/theonewolf for fix/pull request)

    License:

        *   BSD

    Author:

        *   Paul Chakravarti (paul.chakravarti@gmail.com)
"""

