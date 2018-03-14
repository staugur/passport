# -*- coding: utf-8 -*-
"""
    passport.utils.web
    ~~~~~~~~~~~~~~

    Common function for web.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import json
import requests
from .tool import access_logger, logger, gen_fingerprint, parseAcceptLanguage, get_current_timestamp, timestamp_after_timestamp
from .jwt import JWTUtil, JWTException
from .aes_cbc import CBC
from libs.base import ServiceBase
from urllib import urlencode
from functools import wraps
from flask import g, request, redirect, url_for, make_response, abort, jsonify, flash
from werkzeug import url_decode
from config import SYSTEM

jwt = JWTUtil()
cbc = CBC()
sbs = ServiceBase()


def get_referrer_url():
    """获取上一页地址"""
    if request.referrer and request.referrer.startswith(request.host_url) and request.endpoint and not "api." in request.endpoint:
        url = request.referrer
    else:
        url = None
    return url


def get_redirect_url(endpoint="front.signIn"):
    """获取重定向地址
    NextUrl: 引导重定向下一步地址
    ReturnUrl: 最终重定向地址
    以上两个不存在时，如果定义了非默认endpoint，则首先返回；否则返回referrer地址，不存在时返回endpoint默认主页
    """
    url = request.args.get('NextUrl') or request.args.get('ReturnUrl')
    if not url:
        if endpoint != "front.signIn":
            url = url_for(endpoint)
        else:
            url = get_referrer_url() or url_for(endpoint)
    logger.debug(url)
    return url


def set_loginstate(sessionId, returnUrl):
    """设置登录态"""
    response = make_response(redirect(returnUrl))
    response.set_cookie(key="sessionId", value=sessionId, max_age=SYSTEM["SESSION_EXPIRE"], httponly=True, secure=False if request.url_root.split("://")[0] == "http" else True)
    return response


def set_sessionId(uid, seconds=SYSTEM["SESSION_EXPIRE"], sid=None):
    """设置cookie"""
    payload = dict(uid=uid, sid=sid) if sid else dict(uid=uid)
    sessionId = jwt.createJWT(payload=payload, expiredSeconds=seconds)
    return cbc.encrypt(sessionId)


def verify_sessionId(cookie):
    """验证cookie"""
    if cookie:
        try:
            sessionId = cbc.decrypt(cookie)
        except Exception, e:
            logger.debug(e)
        else:
            try:
                success = jwt.verifyJWT(sessionId)
            except JWTException, e:
                logger.debug(e)
            else:
                # 验证token无误即设置登录态，所以确保解密、验证两处key切不可丢失，否则随意伪造！
                return success
    return False


def analysis_sessionId(cookie, ReturnType="dict"):
    """分析获取cookie中payload数据"""
    data = dict()
    if cookie:
        try:
            sessionId = cbc.decrypt(cookie)
        except Exception, e:
            logger.debug(e)
        else:
            try:
                success = jwt.verifyJWT(sessionId)
            except JWTException, e:
                logger.debug(e)
            else:
                if success:
                    # 验证token无误即设置登录态，所以确保解密、验证两处key切不可丢失，否则随意伪造！
                    data = jwt.analysisJWT(sessionId)["payload"]
    if ReturnType == "dict":
        return data
    else:
        return data.get("sid"), data.get("uid")


def checkGet_ssoRequest(sso):
    """检查是否是正确的sso请求并返回相应结果"""
    # 判断此次请求是否是正确的sso请求
    sso_isOk = False
    # 设置sso请求跳转返回的地址
    sso_returnUrl = None
    # 方便写入redis时识别注册的应用
    sso_appName = None
    # 验证参数并赋值
    if verify_sessionId(sso):
        # sso jwt payload
        sso = analysis_sessionId(sso)
        if sso and isinstance(sso, dict) and "app_name" in sso and "app_id" in sso and "app_secret" in sso:
            # 通过app_name获取注册信息并校验参数
            app_data = g.api.userapp.getUserApp(sso["app_name"])
            if app_data:
                if sso["app_id"] == app_data["app_id"] and sso["app_secret"] == app_data["app_secret"]:
                    sso_isOk = True
                    sso_appName = sso["app_name"]
                    sso_returnUrl = "{}/sso/authorized?{}".format(app_data["app_redirect_url"].strip("/"), urlencode(dict(Action="ssoLogin", ReturnUrl=sso["ReturnUrl"] if sso.get("ReturnUrl") else "/")))
    return sso_isOk, sso_returnUrl, sso_appName


def checkSet_ssoTicketSid(sso_isOk, sso_returnUrl, sso_appName, uid, defaultReturnUrl=None):
    sessionId = set_sessionId(uid=uid)
    returnUrl = defaultReturnUrl or url_for("front.userset")
    if sso_isOk:
        # 创建ticket，返回为真即是ticket
        tickets = g.api.usersso.ssoCreateTicket()
        if tickets and isinstance(tickets, (list, tuple)) and len(tickets) == 2:
            ticket, sid = tickets
            logger.debug("checkSet_ssoTicketSid set sessionId for sid: {}, uid: {}".format(sid, uid))
            sessionId = set_sessionId(uid=uid, sid=sid)
            if g.api.usersso.ssoCreateSid(ticket=ticket, uid=uid, source_app_name=sso_appName):
                returnUrl = "{}&ticket={}".format(sso_returnUrl, ticket)
            else:
                flash(dfr(dict(msg="Failed to create authorization ticket")))
        else:
            flash(dfr(dict(msg="Failed to create authorization ticket")))
    return (sessionId, returnUrl)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.signin:
            return redirect(url_for('front.signIn'))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.signin:
            return redirect(get_redirect_url())
        return f(*args, **kwargs)
    return decorated_function


def adminlogin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.signin and g.uid:
            if sbs.isAdmin(g.uid):
                return f(*args, **kwargs)
        return abort(404)
    return decorated_function


def apilogin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.signin:
            return jsonify(dfr(dict(msg="Authentication failed or no permission to access", code=1)))
        return f(*args, **kwargs)
    return decorated_function


def apiadminlogin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.signin and g.uid:
            if sbs.isAdmin(g.uid):
                return f(*args, **kwargs)
        return jsonify(dfr(dict(msg="Authentication failed or no permission to access", code=1)))
    return decorated_function


def tpl_adminlogin_required():
    """模板中判断是否为管理员用户"""
    if g.signin and g.uid and sbs.isAdmin(g.uid):
        return True
    return False


def oauth2_name2type(name):
    """将第三方登录根据name转化为对应数字
    @param name str: OAuth name
    1手机号 2邮箱 3GitHub 4qq 5微信 6百度 7新浪微博 8Coding 9码云
    """
    BIND = dict(
        mobile=1,
        email=2,
        github=3,
        qq=4,
        wechat=5,
        baidu=6,
        weibo=7,
        coding=8,
        gitee=9
    )
    if name in BIND:
        return BIND[name]


def oauth2_type2name(otype):
    """将第三方登录根据name转化为对应数字
    @param name str: OAuth name
    1手机号 2邮箱 3GitHub 4qq 5微信 6百度 7新浪微博 8Coding 9码云
    """
    BIND = {
        3: "github",
        4: "qq",
        5: "wechat",
        6: "baidu",
        7: "weibo",
        8: "coding",
        9: "gitee"
    }
    if otype in BIND:
        return BIND[otype]


def oauth2_genderconverter(gender):
    """性别转换器"""
    if gender:
        if gender in (u"男", "男", "man", "m", 0, "0"):
            return 1
        elif gender in (u"女", "女", "woman", "f", "female", 1, "1"):
            return 0
    return 2


class OAuth2(object):
    """OAuth2.0 Client基类"""

    def __init__(self, name, client_id, client_secret, redirect_url, authorize_url, access_token_url, get_userinfo_url, get_openid_url=None, **kwargs):
        """
        必选参数：
            name: 开放平台标识
            client_id: 开放平台申请的应用id
            client_secret: 开放平台申请的应用密钥
            redirect_url: 开放平台申请的应用回掉地址
            authorize_url: 开放平台的授权地址
            access_token_url: 开放平台的access_token请求地址
            get_userinfo_url: 开放平台的用户信息请求地址
            get_openid_url: 开放平台的获取用户唯一标识请求地址，可选
        可选参数：
            scope: 申请权限，保持默认即可
            state: client端的状态值，可随机可校验，防CSRF攻击
            access_token_method: 开放平台的access_token请求方法，默认post，仅支持get、post
            get_userinfo_method: 开放平台的用户信息请求方法，默认get，仅支持get、post
            get_openid_method: 开放平台的获取用户唯一标识请求方法，默认get，仅支持get、post
            content_type: 保留
            verify_state: 是否验证state值
        """
        self._name = name
        self._consumer_key = client_id
        self._consumer_secret = client_secret
        self._redirect_url = redirect_url
        self._authorize_url = authorize_url
        self._access_token_url = access_token_url
        self._get_openid_url = get_openid_url
        self._get_userinfo_url = get_userinfo_url
        self._encoding = "utf-8"
        self._response_type = "code"
        self._scope = kwargs.get("scope", "")
        self._access_token_method = kwargs.get("access_token_method", "post").lower()
        self._get_openid_method = kwargs.get("get_openid_method", "get").lower()
        self._get_userinfo_method = kwargs.get("get_userinfo_method", "get").lower()
        self._content_type = kwargs.get("content_type", "application/json")
        self._verify_state = kwargs.get("verify_state", True)
        self._requests = requests.Session()

    @property
    def __make_state(self):
        """生成state并设置过期时间10min"""
        state = gen_fingerprint(n=4)
        key = "passport:oauth:state:{}".format(state)
        pipe = sbs.redis.pipeline()
        pipe.set(key, timestamp_after_timestamp(seconds=600))
        pipe.expire(key, 600)
        pipe.execute()
        return state

    def __verify_state(self, state):
        """验证state"""
        if self._verify_state is False:
            return True
        key = "passport:oauth:state:{}".format(state)
        if state and sbs.redis.exists(key):
            expire = sbs.redis.get(key)
            if get_current_timestamp() <= int(expire):
                return True
        return False

    @property
    def requests(self):
        # 请求函数，同requests
        return self._requests

    def authorize(self, **params):
        '''登录的第一步：请求授权页面以获取`Authorization Code`
        :params: 其他请求参数
        '''
        sso = request.args.get("sso") or None
        _request_params = self._make_params(
            response_type=self._response_type,
            client_id=self._consumer_key,
            redirect_uri=self._redirect_url + "?sso=" + sso if sso else self._redirect_url,
            state=self.__make_state,
            scope=self._scope,
            **params
        )
        return redirect(self._authorize_url + "?" + _request_params)

    def authorized_response(self):
        '''登录第二步：授权回调，通过`Authorization Code`获取`Access Token`'''
        code = request.args.get("code")
        # state 可以先写入redis并设置过期，此处做验证，增强安全
        state = request.args.get("state")
        if code and self.__verify_state(state):
            _request_params = self._make_params(
                grant_type="authorization_code",
                client_id=self._consumer_key,
                client_secret=self._consumer_secret,
                code=code,
                redirect_uri=self._redirect_url
            )
            url = self._access_token_url + "?" + _request_params
            resp = self.requests.get(url) if self._access_token_method == 'get' else self.requests.post(url)
            try:
                data = resp.json()
            except:
                data = resp.text
            # 包含access_token、expires_in、refresh_token等数据
            return data
        else:
            logger.info("Invalid code or state")

    def get_openid(self, access_token, **params):
        '''登录第三步准备：根据access_token获取用户唯一标识id'''
        _request_params = self._make_params(
            access_token=access_token,
            **params
        )
        if not self._get_openid_url:
            return None
        url = self._get_openid_url + "?" + _request_params
        resp = self.requests.get(url) if self._get_openid_method == 'get' else self.requests.post(url)
        try:
            data = resp.json()
        except:
            data = resp.text
        return data

    def get_userinfo(self, access_token, **params):
        '''登录第三步：根据access_token获取用户信息(部分开放平台需要先获取openid、uid，可配置get_openid_url，先请求get_openid接口)'''
        _request_params = self._make_params(
            access_token=access_token,
            **params
        )
        url = self._get_userinfo_url + "?" + _request_params
        resp = self.requests.get(url) if self._get_userinfo_method == 'get' else self.requests.post(url)
        try:
            data = resp.json()
        except:
            data = resp.text
        return data

    def goto_signIn(self, uid, sso=None):
        """OAuth转入登录流程，表示登录成功
        -- 如果sso存在则解析sso并跳转到sso对应回调地址
        -- 否则直接设置cookie登录态
        """
        if not uid:
            raise
        if sso:
            sso_isOk, sso_returnUrl, sso_appName = checkGet_ssoRequest(sso)
            logger.debug("OAuth2, method: {}, sso_isOk: {}, ReturnUrl: {}".format(request.method, sso_isOk, sso_returnUrl))
            sessionId, returnUrl = checkSet_ssoTicketSid(sso_isOk, sso_returnUrl, sso_appName, uid)
        else:
            sessionId, returnUrl = set_sessionId(uid=uid), url_for("front.userset")
        # sso正确时sessionId含有sid，且returnUrl是appName的回调地址；当不正确时，仅为uid，returnUrl为上一页地址
        return set_loginstate(sessionId, returnUrl)

    def goto_signUp(self, openid, sso=None):
        """OAuth转入注册绑定流程"""
        return redirect(url_for("front.OAuthGuide", openid=openid, sso=sso)) if sso else redirect(url_for("front.OAuthGuide", openid=openid))

    def _make_params(self, **kwargs):
        """传入编码成url参数"""
        return urlencode(kwargs)

    def url_code(self, content):
        '''
        parse string, such as access_token=E8BF2BCAF63B7CE749796519F5C5D5EB&expires_in=7776000&refresh_token=30AF0BD336324575029492BD2D1E134B.
        return data, such as {'access_token': 'E8BF2BCAF63B7CE749796519F5C5D5EB', 'expires_in': '7776000', 'refresh_token': '30AF0BD336324575029492BD2D1E134B'}
        '''
        return url_decode(content, charset=self._encoding).to_dict() if content else None


# 邮件模板：参数依次是邮箱账号、使用场景、验证码
email_tpl = u"""<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><style>a{text-decoration: none}</style></head><body><table style="width:550px;"><tr><td style="padding-top:10px; padding-left:5px; padding-bottom:5px; border-bottom:1px solid #D9D9D9; font-size:16px; color:#999;">SaintIC Passport</td></tr><tr><td style="padding:20px 0px 20px 5px; font-size:14px; line-height:23px;">尊敬的<b>%s</b>，您正在申请<i>%s</i><br><br>申请场景的邮箱验证码是 <b style="color: red">%s</b><br><br>5分钟有效，请妥善保管验证码，不要泄露给他人。<br></td></tr><tr><td style="padding-top:5px; padding-left:5px; padding-bottom:10px; border-top:1px solid #D9D9D9; font-size:12px; color:#999;">此为系统邮件，请勿回复<br/>请保管好您的邮箱，避免账户被他人盗用<br/><br/>如有任何疑问，可查看网站帮助 <a target="_blank" href="https://passport.saintic.com">https://passport.saintic.com</a></td></tr></table></body></html>"""


def dfr(res, default='en-US'):
    """定义前端返回，将res中msg字段转换语言
    @param res dict: like {"msg": None, "success": False}, 英文格式
    @param default str: 默认语言
    """
    try:
        language = parseAcceptLanguage(request.cookies.get("locale", request.headers.get('Accept-Language', default)), default)
        if language == "zh-Hans-CN":
            language = "zh-CN"
    except:
        language = default
    # 翻译转换字典库
    trans = {
        # 简体中文
        "zh-CN": {
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
            "Not support phone number login": u"暂不支持手机号登录",
            "Have sent the verification code, please check the mailbox": u"已发送过验证码，请查收邮箱",
            "Sent verification code, valid for 300 seconds": u"已发送验证码，有效期300秒",
            "Mail delivery failed, please try again later": u"邮件发送失败，请稍后重试",
            "Third-party login binding failed": u"第三方登录绑定失败",
            "Has been bound to other accounts": u"已经绑定其他账号",
            "Operation failed, rolled back": u"操作失败，已回滚",
            "Authentication failed or no permission to access": u"认证失败或无权限访问",
            "There are invalid parameters": u"存在无效或不合法的参数",
            "No data": u"没有数据",
            "Name already exists": u"名称已存在",
            "Personal domain has been occupied": u"个性域名已被占用",
            "Unsuccessfully obtained file or format is not allowed": u"未获取到文件或格式不合法",
            "Image address is not valid": u"图片地址不合法",
            "System rate-limit policy is blocked": u"系统限流策略阻止",
            "Please bind the email or phone first": u"请先绑定邮箱或手机",
            "Failed to create authorization ticket": u"创建授权令牌失败",
        },
        # 繁体中文-香港
        "zh-HK": {
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
            "Not support phone number login": u"暫不支持手機號登入",
            "Have sent the verification code, please check the mailbox": u"已發送過驗證碼，請查收郵箱",
            "Sent verification code, valid for 300 seconds": u"已發送驗證碼，有效期300秒",
            "Mail delivery failed, please try again later": u"郵件發送失敗，請稍後重試",
            "Third-party login binding failed": u"第三方登錄綁定失敗",
            "Has been bound to other accounts": u"已經綁定其他賬號",
            "Operation failed, rolled back": u"操作失敗，已回滾",
            "Authentication failed or no permission to access": u"認證失敗或無權限訪問",
            "There are invalid parameters": u"存在無效或不合法的參數",
            "No data": u"沒有數據",
            "Name already exists": u"名稱已存在",
            "Personal domain has been occupied": u"個性域名已被佔用",
            "Unsuccessfully obtained file or format is not allowed": u"未獲取到文件或格式不合法",
            "Image address is not valid": u"圖片地址不合法",
            "System rate-limit policy is blocked": u"系統限流策略阻止",
            "Please bind the email or phone first": u"請先綁定郵箱或手機",
            "Failed to create authorization ticket": u"創建授權令牌失敗",
        }
    }
    if isinstance(res, dict) and not "en" in language:
        if res.get("msg"):
            msg = res["msg"]
            try:
                new = trans[language][msg]
            except KeyError, e:
                logger.warn(e)
            else:
                res["msg"] = new
    return res
