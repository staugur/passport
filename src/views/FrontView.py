# -*- coding: utf-8 -*-
"""
    passport.views.FrontView
    ~~~~~~~~~~~~~~

    The blueprint for front view.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""
import json
from config import VAPTCHA
from utils.send_email_msg import SendMail
from utils.web import email_tpl, login_required, anonymous_required, dfr, set_cookie
from utils.tool import logger, generate_verification_code, email_check, phone_check
from libs.auth import Authentication
from vaptchasdk import vaptcha as VaptchaApi
from flask import Blueprint, request, render_template, jsonify, g, abort, redirect, url_for, flash, make_response, current_app

#初始化前台蓝图
FrontBlueprint = Blueprint("front", __name__)
#初始化邮箱发送服务
sendmail = SendMail()
#初始化手势验证码服务
vaptcha = VaptchaApi(VAPTCHA["vid"], VAPTCHA["key"])

@FrontBlueprint.route('/')
def index():
    #首页
    return render_template("index.html")

@FrontBlueprint.route('/link')
def link():
    """重定向链接"""
    nextUrl = request.args.get("nextUrl") or url_for(".index")
    return redirect(nextUrl)

@FrontBlueprint.route('/signUp', methods=['GET', 'POST'])
@anonymous_required
def signUp():
    if request.method == 'POST':
        sceneid = request.args.get("sceneid") or "02"
        token = request.form.get("token")
        challenge = request.form.get("challenge")
        if token and challenge and vaptcha.validate(challenge, token, sceneid):
            account = request.form.get("account")
            vcode = request.form.get("vcode")
            password = request.form.get("password")
            repassword = request.form.get("repassword")
            register_ip = request.headers.get('X-Real-Ip', request.remote_addr)
            auth = Authentication(g.mysql, g.redis)
            try:
                res = auth.signUp(account=account, vcode=vcode, password=password, repassword=repassword, register_ip=register_ip)
            except Exception,e:
                logger.error(e, exc_info=True)
                flash(u"系统异常，请稍后再试")
            else:
                res = dfr(res)
                if res["success"]:
                    # 写登陆日志
                    return redirect(url_for('.signIn'))
                else:
                    flash(res["msg"])
        else:
            flash(u"人机验证失败")
        return redirect(url_for('.signUp'))
    return render_template("auth/signUp.html")

@FrontBlueprint.route('/signIn', methods=['GET', 'POST'])
@anonymous_required
def signIn():
    if request.method == 'POST':
        sceneid = request.args.get("sceneid") or "01"
        token = request.form.get("token")
        challenge = request.form.get("challenge")
        if token and challenge and vaptcha.validate(challenge, token, sceneid):
            account = request.form.get("account")
            password = request.form.get("password")
            login_ip = request.headers.get('X-Real-Ip', request.remote_addr)
            auth = Authentication(g.mysql, g.redis)
            res = auth.signIn(account=account, password=password)
            res = dfr(res)
            if res["success"]:
                # 记录登录日志
                auth.brush_loginlog(res, login_ip=login_ip, user_agent=request.headers.get("User-Agent"))
                # 登录成功，设置cookie
                sessionId = set_cookie(uid=res["uid"])
                response = make_response(redirect(g.redirect_uri))
                # 设置cookie根据浏览器周期过期，当无https时去除`secure=True`
                secure = False if request.url_root.split("://")[0] == "http" else True
                response.set_cookie(key="sessionId", value=sessionId, max_age=None, httponly=True, secure=secure)
                return response
            else:
                flash(res["msg"])
        else:
            flash(u"人机验证失败")
        return redirect(url_for('.signIn'))
    return render_template("auth/signIn.html")

@FrontBlueprint.route("/OAuthGuide")
@anonymous_required
def OAuthGuide():
    """OAuth2登录未注册时引导路由，选择绑定已有账号或直接登录(首选)"""
    if request.args.get("openid"):
        return render_template("auth/OAuthGuide.html")
    else:
        return redirect(url_for(".index"))

@FrontBlueprint.route("/OAuthGuide/DirectLogin", methods=["POST"])
@anonymous_required
def OAuthDirectLogin():
    """OAuth2直接登录(首选)"""
    if request.method == 'POST':
        openid = request.form.get("openid")
        if openid:
            auth = Authentication(g.mysql, g.redis)
            # 直接注册新账号并设置登录态
            ip = request.headers.get('X-Real-Ip', request.remote_addr)
            res = auth.oauth2_signUp(openid, ip)
            res = dfr(res)
            if res["success"]:
                # 记录登录日志
                auth.brush_loginlog(res, login_ip=ip, user_agent=request.headers.get("User-Agent"))
                # 登录成功，设置cookie
                sessionId = set_cookie(uid=res["uid"])
                response = make_response(redirect(url_for(".index")))
                # 设置cookie根据浏览器周期过期，当无https时去除`secure=True`
                secure = False if request.url_root.split("://")[0] == "http" else True
                response.set_cookie(key="sessionId", value=sessionId, max_age=None, httponly=True, secure=secure)
                return response
            else:
                flash(res["msg"])
            return redirect(url_for('.index'))
        else:
            return redirect(url_for(".index"))

@FrontBlueprint.route("/OAuthGuide/BindAccount", methods=["GET", "POST"])
@anonymous_required
def OAuthBindAccount():
    """OAuth2绑定已有账号登录"""
    if request.method == 'POST':
        openid = request.form.get("openid")
        sceneid = request.args.get("sceneid") or "03"
        token = request.form.get("token")
        challenge = request.form.get("challenge")
        if token and challenge and vaptcha.validate(challenge, token, sceneid):
            account = request.form.get("account")
            password = request.form.get("password")
            auth = Authentication(g.mysql, g.redis)
            res = auth.oauth2_bindLogin(openid=openid, account=account, password=password)
            res = dfr(res)
            if res["success"]:
                # 记录登录日志
                auth.brush_loginlog(res, login_ip=request.headers.get('X-Real-Ip', request.remote_addr), user_agent=request.headers.get("User-Agent"))
                # 登录成功，设置cookie
                sessionId = set_cookie(uid=res["uid"])
                response = make_response(redirect(url_for(".index")))
                # 设置cookie根据浏览器周期过期，当无https时去除`secure=True`
                secure = False if request.url_root.split("://")[0] == "http" else True
                response.set_cookie(key="sessionId", value=sessionId, max_age=None, httponly=True, secure=secure)
                return response
            else:
                flash(res["msg"])
        else:
            flash(u"人机验证失败")
        return redirect(url_for('.OAuthBindAccount', openid=openid))
    else:
        openid = request.args.get("openid")
        if openid:
            return render_template("auth/OAuthBindAccount.html")
        else:
            redirect(url_for(".index"))

@FrontBlueprint.route('/miscellaneous/_sendVcode', methods=['POST'])
def misc_sendVcode():
    """发送验证码：邮箱、手机"""
    res = dict(msg=None, success=False)
    account = request.form.get("account")
    if email_check(account):
        email = account
        key = "passport:signUp:vcode:{}".format(email)
        try:
            hasKey = g.redis.exists(key)
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(msg="System is abnormal")
        else:
            if hasKey:
                res.update(msg="Have sent the verification code, please check the mailbox")
            else:
                vcode = generate_verification_code()
                result = sendmail.SendMessage(to_addr=email, subject=u"Passport邮箱注册验证码", formatType="html", message=email_tpl %(email, u"注册", vcode))
                if result["success"]:
                    try:
                        g.redis.set(key, vcode)
                        g.redis.expire(key, 300)
                    except Exception,e:
                        logger.error(e, exc_info=True)
                        res.update(msg="System is abnormal")
                    else:
                        res.update(msg="Sent verification code, valid for 300 seconds", success=True)
                else:
                    res.update(msg="Mail delivery failed, please try again later")
    elif phone_check(account):
        res.update(msg="Not support phone number registration")
    else:
        res.update(msg="Invalid account")
    logger.debug(res)
    return jsonify(dfr(res))

@FrontBlueprint.route("/miscellaneous/_getChallenge")
def misc_getChallenge():
    """Vaptcha获取流水
    @param sceneid str: 场景id，如01登录、02注册
    """
    sceneid = request.args.get("sceneid") or ""
    return jsonify(json.loads(vaptcha.get_challenge(sceneid)))

@FrontBlueprint.route("/miscellaneous/_getDownTime")
def misc_getDownTime():
    """Vaptcha宕机模式
    like: ?data=request&_t=1516092685906
    """
    data = request.args.get("data")
    logger.info("vaptcha into downtime, get data: {}, query string: {}".format(data, request.args.to_dict()))
    return jsonify(json.loads(vaptcha.downtime(data)))

@FrontBlueprint.route("/logout")
@login_required
def logout():
    response = make_response(redirect(url_for('signIn')))
    response.set_cookie(key='sessionId', value='', expires=0)
    return response


