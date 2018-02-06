#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    passport.utils.send_email_msg
    ~~~~~~~~~~~~~~

    1. If you don't have a mail server, try local mail service, this requires that your local mail service is turned on.
    The following is a part of the change.

    Modify this line:
    smtp_server='127.0.0.1'

    Comment on this line:
    #useraddr='xxxx'
    #password='xxxx'
    #server.login(useraddr, password)

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from .tool import email_check, logger
from config import EMAIL


class SendMail(object):
    """发送邮件类"""

    def __init__(self):
        self.useraddr = EMAIL["useraddr"]
        self.password = EMAIL["userpass"]
        self.smtp_server = EMAIL["smtpServer"]
        self.smtp_port = EMAIL["smtpPort"]
        self.smtp_ssl = True if EMAIL["smtpSSL"] in ("true", "True", True) else False
        self.from_addr = self._format_addr("SaintIC Passport <{}>".format(self.useraddr))

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def SendMessage(self, to_addr, subject, message, formatType="plain"):
        """
        发送文本/HTML消息
        @param to_addr(str, unicode, list, tuple) 收件人地址，多个收件人请使用列表或元组
        @param subject(str, unicode) 主题
        @param message(str, unicode) 邮件正文
        @param formatType(str, unicode)  邮件格式类型 plain或html
        """
        res = dict(success=False)
        if subject and message and isinstance(subject, (str, unicode)) and isinstance(message, (str, unicode)) and isinstance(to_addr, (str, unicode, list, tuple)):
            if isinstance(to_addr, (str, unicode)):
                to_addrs = (to_addr,)
            else:
                to_addrs = to_addr
            msg = MIMEText(message, formatType, 'utf-8')
            msg['From'] = self.from_addr
            msg['To'] = to_addr
            msg['Subject'] = Header(subject, 'utf-8').encode()
            try:
                if self.smtp_ssl is True:
                    server = smtplib.SMTP_SSL(self.smtp_server, port=self.smtp_port)
                else:
                    server = smtplib.SMTP(self.smtp_server, port=self.smtp_port)
                # server.set_debuglevel(1)
                server.login(self.useraddr, self.password)
                server.sendmail(self.useraddr, to_addrs, msg.as_string())
                server.quit()
            except smtplib.SMTPException, e:
                logger.error(e, exc_info=True)
                res.update(msg="Unable to send mail")
            else:
                res.update(success=True)
        else:
            res.update(msg="email format error")
        logger.debug(res)
        return res
