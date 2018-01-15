# -*- coding: utf-8 -*-
"""
    passport.utils.web
    ~~~~~~~~~~~~~~

    Common function for web.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""
import json
from functools import wraps
from flask import g, request, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.signin:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def clicklog_write(redis, data):
    """访问日志写redis(另外需要有程序或按条件异步读取redis写入到mysql中)"""
    key = "passport:sys_clicklog"
    redis.lpush(key, json.dumps(data))

# 邮件模板：参数依次是邮箱账号、使用场景、验证码
email_tpl = u"""<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><style>a{text-decoration: none}</style></head><body><table style="width:550px;"><tr><td style="padding-top:10px; padding-left:5px; padding-bottom:5px; border-bottom:1px solid #D9D9D9; font-size:16px; color:#999;">SaintIC Passport</td></tr><tr><td style="padding:20px 0px 20px 5px; font-size:14px; line-height:23px;">尊敬的<b>%s</b>，您正在申请<i>%s</i><br><br>申请场景的邮箱验证码是 <b style="color: red">%s</b><br><br>5分钟有效，请妥善保管验证码，不要泄露给他人。<br></td></tr><tr><td style="padding-top:5px; padding-left:5px; padding-bottom:10px; border-top:1px solid #D9D9D9; font-size:12px; color:#999;">此为系统邮件，请勿回复<br/>请保管好您的邮箱，避免账户被他人盗用<br/><br/>如有任何疑问，可查看网站帮助 <a target="_blank" href="https://passport.saintic.com">https://passport.saintic.com</a></td></tr></table></body></html>"""
