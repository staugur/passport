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
from .tool import logger
from .jwt import JWTUtil, JWTException
from .aes_cbc import CBC

jwt = JWTUtil()
cbc = CBC()

def set_cookie(uid, seconds=7200):
    """设置cookie"""
    sessionId = jwt.createJWT(payload=dict(uid=uid), expiredSeconds=seconds)
    return cbc.encrypt(sessionId)

def verify_cookie(cookie):
    """验证cookie"""
    if cookie:
        try:
            sessionId = cbc.decrypt(cookie)
        except Exception,e:
            logger.warn(e)
        else:
            try:
                success = jwt.verifyJWT(sessionId)
            except JWTException,e:
                logger.error(e, exc_info=True)
            else:
                # 验证token无误即设置登录态，所以确保解密、验证两处key切不可丢失，否则随意伪造！
                return success
    return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.signin:
            return redirect(url_for('signIn'))
        return f(*args, **kwargs)
    return decorated_function

def anonymous_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.signin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# 邮件模板：参数依次是邮箱账号、使用场景、验证码
email_tpl = u"""<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><style>a{text-decoration: none}</style></head><body><table style="width:550px;"><tr><td style="padding-top:10px; padding-left:5px; padding-bottom:5px; border-bottom:1px solid #D9D9D9; font-size:16px; color:#999;">SaintIC Passport</td></tr><tr><td style="padding:20px 0px 20px 5px; font-size:14px; line-height:23px;">尊敬的<b>%s</b>，您正在申请<i>%s</i><br><br>申请场景的邮箱验证码是 <b style="color: red">%s</b><br><br>5分钟有效，请妥善保管验证码，不要泄露给他人。<br></td></tr><tr><td style="padding-top:5px; padding-left:5px; padding-bottom:10px; border-top:1px solid #D9D9D9; font-size:12px; color:#999;">此为系统邮件，请勿回复<br/>请保管好您的邮箱，避免账户被他人盗用<br/><br/>如有任何疑问，可查看网站帮助 <a target="_blank" href="https://passport.saintic.com">https://passport.saintic.com</a></td></tr></table></body></html>"""

def dfr(res, language="zh_CN"):
    """定义前端返回，将res中msg字段转换语言
    @param res dict: like {"msg": None, "success": False}, 英文格式
    @param language str: `zh_CN 简体中文`, `zh_HK 繁体中文`
    """
    # 翻译转换字典库
    trans = dict(
        zh_CN = {
            "Hello World": u"世界，你好",
            "Account already exists": u"账号已存在",
            "System is abnormal": u"系统异常，请稍后再试",
            "Registration success": u"注册成功",
            "Registration failed": u"注册失败",
            "Check failed": u"校验未通过",
            "Email already exists": u"邮箱已存在",
            "Invalid verification code": u"无效的验证码",
            "Invalid password: Inconsistent password or length failed twice": u"无效的密码：两次密码不一致或长度不合格",
            "Not support phone number registration": u"暂不支持手机号注册",
            "Invalid account": u"无效的账号",
            "Wrong password": u"密码错误",
            "Invalid account: does not exist or has been disabled": u"无效的账号：不存在或已禁用",
            "Invalid password: length unqualified": u"无效的密码：长度不合格",
            "Temporarily do not support phone number login": u"暂不支持手机号登录",
            "Have sent the verification code, please check the mailbox": u"已发送过验证码，请查收邮箱",
            "Sent verification code, valid for 300 seconds": u"已发送验证码，有效期300秒",
            "Mail delivery failed, please try again later": u"邮件发送失败，请稍后重试",
        },
        zh_HK = {
            "Hello World": u"世界，你好",
            "Account already exists": u"帳號已存在",
            "System is abnormal": u"系統异常",
            "Registration success": u"注册成功",
            "Registration failed": u"注册失敗",
            "Check failed": u"校驗未通過",
            "Email already exists": u"郵箱已存在",
            "Invalid verification code": u"無效的驗證碼",
            "Invalid password: Inconsistent password or length failed twice": u"無效的密碼：兩次密碼不一致或長度不合格",
            "Not support phone number registration": u"暫不支持手機號注册",
            "Invalid account": u"無效的帳號",
            "Wrong password": u"密碼錯誤",
            "Invalid account: does not exist or has been disabled": u"無效的帳號：不存在或已禁用",
            "Invalid password: length unqualified": u"無效的密碼：長度不合格",
            "Temporarily do not support phone number login": u"暫不支持手機號登入",
            "Have sent the verification code, please check the mailbox": u"已發送過驗證碼，請查收郵箱",
            "Sent verification code, valid for 300 seconds": u"已發送驗證碼，有效期300秒",
            "Mail delivery failed, please try again later": u"郵件發送失敗，請稍後重試",
        }
    )
    if isinstance(res, dict):
        if res.get("msg"):
            msg = res["msg"]
            try:
                new = trans[language][msg]
            except KeyError,e:
                logger.warn(e)
            else:
                res["msg"] = new
    return res
 