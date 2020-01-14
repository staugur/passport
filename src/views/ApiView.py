# -*- coding: utf-8 -*-
"""
    passport.views.ApiView
    ~~~~~~~~~~~~~~

    The blueprint for api view.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""
import os
import json
import base64
from config import SYSTEM, UPYUN as Upyun
from utils.send_email_msg import SendMail
from utils.send_phone_msg import SendSms
from utils.web import email_tpl, dfr, apilogin_required, apianonymous_required, apiadminlogin_required, VaptchaApi, FastPushMessage, analysis_sessionId, set_sessionId
from utils.tool import logger, generate_verification_code, email_check, phone_check, ListEqualSplit,  gen_rnd_filename, allowed_file, timestamp_to_timestring, get_current_timestamp, parse_userAgent, getIpArea, get_today, generate_digital_verification_code, UploadImage2Upyun, comma_pat
from libs.auth import Authentication
from flask import Blueprint, request, jsonify, g, url_for
from werkzeug import secure_filename

# 初始化前台蓝图
ApiBlueprint = Blueprint("api", __name__)
#初始化手势验证码服务
vaptcha = VaptchaApi()
#文件上传文件夹, 相对于项目根目录, 请勿改动static/部分
IMAGE_FOLDER  = 'static/upload/'
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), IMAGE_FOLDER)

@ApiBlueprint.route('/miscellaneous/_sendVcode', methods=['POST'])
def misc_sendVcode():
    """发送验证码：邮箱、手机"""
    res = dict(msg=None, success=False)
    account = request.form.get("account")
    scene = request.form.get("scene") or request.args.get("scene") or "signUp"
    scenemap = dict(signUp=u"注册", bindLauth=u"绑定本地化账号", forgot=u"忘记密码")
    if email_check(account):
        # 生成验证码，校验的话，libs.auth.Authentication类中`__check_sendVcode`方法
        email = account
        key = "passport:vcode:{}:{}".format(scene, email)
        try:
            hasKey = g.redis.exists(key)
        except Exception, e:
            logger.error(e, exc_info=True)
            res.update(msg="System is abnormal")
        else:
            if hasKey:
                res.update(msg="Have sent the verification code, please check the mailbox")
            else:
                # 初始化邮箱发送服务
                sendmail = SendMail()
                vcode = generate_verification_code()
                result = sendmail.SendMessage(to_addr=email, subject=u"SaintIC Passport %s 验证码" %scenemap[scene], formatType="html", message=email_tpl % (email, scenemap[scene], vcode))
                if result["success"]:
                    try:
                        g.redis.set(key, vcode)
                        g.redis.expire(key, 300)
                    except Exception, e:
                        logger.error(e, exc_info=True)
                        res.update(msg="System is abnormal")
                    else:
                        res.update(msg="Sent verification code, valid for 300 seconds", success=True)
                else:
                    res.update(msg="Mail delivery failed, please try again later")
    elif phone_check(account):
        # 短信验证码，要求同个场景每个手机每天只能发送3次，每个场景验证码有效期5min，校验的话，libs.auth.Authentication类中`__check_sendVcode`方法
        phone = account
        key = "passport:vcode:{}:{}".format(scene, phone)
        keyTimes = "passport:sendsms:{}:{}:{}".format(scene, phone, get_today("%Y%m%d"))
        try:
            hasKey = g.redis.exists(key)
            keyData = int(g.redis.get(keyTimes) or 0)
        except Exception, e:
            logger.error(e, exc_info=True)
            res.update(msg="System is abnormal")
        else:
            if hasKey:
                res.update(msg="Have sent the verification code, please check the mobile phone")
            else:
                if keyData >= 3:
                    res.update(msg="Current scene The number of text messages sent by your mobile phone has reached the upper limit today")
                else:
                    vcode = generate_digital_verification_code()
                    result = SendSms(phone, vcode)
                    if result["success"]:
                        try:
                            pipe = g.redis.pipeline()
                            pipe.set(key, vcode)
                            pipe.expire(key, 300)
                            pipe.incrby(keyTimes, 1)
                            pipe.expire(keyTimes, 86400)
                            pipe.execute()
                        except Exception, e:
                            logger.error(e, exc_info=True)
                            res.update(msg="System is abnormal")
                        else:
                            res.update(msg="Sent verification code, valid for 300 seconds", success=True)
                    else:
                        res.update(msg="SMS failed to send, please try again later")
    else:
        res.update(msg="Invalid account")
    logger.debug(res)
    return jsonify(dfr(res))

@ApiBlueprint.route("/miscellaneous/_getDownTime")
def misc_getDownTime():
    """Vaptcha宕机模式接口"""
    return jsonify(vaptcha.getDownTime)

@ApiBlueprint.route("/miscellaneous/feedback/", methods=["POST"])
def misc_feedback():
    res = dict(msg=None, success=False)
    if request.method == "POST":
        point = request.form.get("point")
        content = request.form.get("content")
        email = request.form.get("email")
        check = True
        if point and content:
            if email:
                if not email_check(email):
                    check = False
                    res.update(msg="Bad mailbox format")
        else:
            check = False
            res.update(msg="There are invalid parameters")
        if check:
            # 初始化邮箱发送服务
            sendmail = SendMail()
            result = sendmail.SendMessage(to_addr=SYSTEM["EMAIL"], subject=u"SaintIC Passport 用户反馈: %s" %point, formatType="html", message=u"用户预留邮箱：%s<br/>用户反馈内容：<br/>%s" %(email, content))
            res.update(result)
    return jsonify(dfr(res))

@ApiBlueprint.route("/user/app/", methods=["GET", "POST", "PUT", "DELETE"])
@apiadminlogin_required
def userapp():
    """管理接口"""
    res = dict(msg=None, code=1)
    if request.method == "GET":
        # 定义参数
        sort = request.args.get("sort") or "desc"
        page = request.args.get("page") or 1
        limit = request.args.get("limit") or 10
        # 参数检查
        try:
            page = int(page)
            limit = int(limit)
            page -= 1
            if page < 0:
                raise
        except:
            res.update(code=2, msg="There are invalid parameters")
        else:
            # 从封装类中获取数据
            res.update(g.api.userapp.listUserApp())
            data = res.get("data")
            if data and isinstance(data, (list, tuple)):
                data = [i for i in sorted(data, reverse=False if sort == "asc" else True)]
                count = len(data)
                data = ListEqualSplit(data, limit)
                pageCount = len(data)
                if page < pageCount:
                    res.update(code=0, data=data[page], pageCount=pageCount, page=page, limit=limit, count=count)
                else:
                    res.update(code=3, msg="There are invalid parameters")
            else:
                res.update(code=4, msg="No data")
    elif request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        app_redirect_url = request.form.get("app_redirect_url")
        res.update(g.api.userapp.createUserApp(name=name, description=description, app_redirect_url=app_redirect_url))
    elif request.method == "PUT":
        name = request.form.get("name")
        description = request.form.get("description")
        app_redirect_url = request.form.get("app_redirect_url")
        res.update(g.api.userapp.updateUserApp(name=name, description=description, app_redirect_url=app_redirect_url))
    elif request.method == "DELETE":
        name = request.form.get("name")
        res.update(g.api.userapp.deleteUserApp(name=name))
        FastPushMessage(res, "您于<i>{}</i>删除了一个SSO客户端应用：<strong>{}</strong>".format(timestamp_to_timestring(get_current_timestamp()), name))
    logger.info(res)
    return jsonify(dfr(res))

@ApiBlueprint.route("/user/profile/", methods=["GET", "POST", "PUT"])
@apilogin_required
def userprofile():
    res = dict(msg=None, code=1)
    if request.method == "GET":
        getBind = True if request.args.get("getBind") in ("true", "True", True) else False
        res = g.api.userprofile.getUserProfile(g.uid, getBind)
    elif request.method == "POST":
        Action = request.args.get("Action")
        if Action == "bindLauth":
            account = request.form.get("account")
            vcode = request.form.get("vcode")
            password = request.form.get("password")
            auth = Authentication(g.mysql, g.redis)
            res = auth.bindLauth(uid=g.uid, account=account, vcode=vcode, password=password)
            if res["success"] == True and res["show_realname_tip"] == True:
                res['set_realname'] = g.api.userprofile.updateUserRealname(g.uid)
    elif request.method == "PUT":
        """修改个人资料，包含：基本资料、密码、头像、社交账号绑定"""
        Action = request.args.get("Action")
        if Action == "profile":
            data = {k: v for k, v in request.form.iteritems() if k in ("nick_name", "domain_name", "birthday", "location", "gender", "signature")}
            res = g.api.userprofile.updateUserProfile(uid=g.uid, **data)
            if res["code"] == 0:
                # 同步基本资料
                g.api.usersso.clientsConSync(g.api.userapp.getUserApp, g.uid, dict(CallbackType="user_profile", CallbackData=data))
        elif Action == "password":
            nowpass = request.form.get("nowpass")
            newpass = request.form.get("newpass")
            repass = request.form.get("repass")
            res = g.api.userprofile.updateUserPassword(uid=g.uid, nowpass=nowpass, newpass=newpass, repass=repass)
    logger.info(res)
    return jsonify(dfr(res))

@ApiBlueprint.route("/user/message/", methods=["GET", "POST", "DELETE"])
@apilogin_required
def usermsg():
    res = dict(msg=None, code=1)
    Action = request.args.get("Action")
    if request.method == "POST":
        if Action == "addMessage":
            res = g.api.usermsg.push_message(g.uid, request.form.get("msgContent"), request.form.get("msgType", "system"))
        elif Action == "markMessage":
            res = g.api.usermsg.markstatus_message(g.uid, request.form.get("msgId"))
    elif request.method == "GET":
        if Action == "getCount":
            res = g.api.usermsg.count_message(g.uid, request.args.get("msgStatus") or 1)
        elif Action == "getList":
            res = g.api.usermsg.pull_message(g.uid, request.args.get("msgStatus") or 1, request.args.get("msgType"), True if request.args.get("desc", True) in (True, "True", "true") else False)
    elif request.method == "DELETE":
        if Action == "delMessage":
            res = g.api.usermsg.delete_message(g.uid, request.form.get("msgId"))
        elif Action == "clearMessage":
            res = g.api.usermsg.clear_message(g.uid)
    logger.info(res)
    return jsonify(dfr(res))

@ApiBlueprint.route('/user/uploadpub/', methods=['POST', 'OPTIONS'])
def useruploadpub():
    # 通过表单形式上传图片
    res = dict(code=1, msg=None)
    logger.debug(request.files)
    f = request.files.get('file')
    callableAction = request.args.get("callableAction")
    if f and allowed_file(f.filename):
        filename = gen_rnd_filename() + "." + secure_filename(f.filename).split('.')[-1]  # 随机命名
        # 判断是否上传到又拍云还是保存到本地
        if Upyun['enable'] in ('true', 'True', True):
            basedir = Upyun['basedir'] if Upyun['basedir'].startswith('/') else "/" + Upyun['basedir']
            imgUrl = os.path.join(basedir, filename)
            try:
                # 又拍云存储封装接口
                UploadImage2Upyun(imgUrl, f.stream.read())
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(code=2, msg="System is abnormal")
            else:
                imgUrl = Upyun['dn'].strip("/") + imgUrl
                res.update(data=dict(src=imgUrl), code=0)
        else:
            if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            imgUrl = request.url_root + IMAGE_FOLDER + filename
            res.update(data=dict(src=imgUrl), code=0)
    else:
        res.update(code=3, msg="Unsuccessfully obtained file or format is not allowed")
    logger.info(res)
    return jsonify(dfr(res))

@ApiBlueprint.route('/user/upload/', methods=['POST', 'OPTIONS'])
@apilogin_required
def userupload():
    # 通过base64形式上传图片
    res = dict(code=1, msg=None)
    picStr = request.form.get('picStr')
    if picStr:
        # 判断是否上传到又拍云还是保存到本地
        if Upyun['enable'] in ('true', 'True', True):
            basedir = Upyun['basedir'] if Upyun['basedir'].startswith('/') else "/" + Upyun['basedir']
            imgUrl = os.path.join(basedir, gen_rnd_filename() + ".png")
            try:
                # 又拍云存储封装接口
                UploadImage2Upyun(imgUrl, base64.b64decode(picStr))
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(code=2, msg="System is abnormal")
            else:
                imgUrl = Upyun['dn'].strip("/") + imgUrl
                res.update(imgUrl=imgUrl, code=0)
        else:
            filename = gen_rnd_filename() + ".png"
            if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
            with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f:
                f.write(base64.b64decode(picStr))
            imgUrl = request.url_root + IMAGE_FOLDER + filename
            res.update(imgUrl=imgUrl, code=0)
        # "回调"动作
        if res.get("imgUrl"):
            imgUrl = res.get("imgUrl")
            callableAction = request.args.get("callableAction")
            if callableAction == "UpdateAvatar":
                resp = g.api.userprofile.updateUserAvatar(uid=g.uid, avatarUrl=imgUrl)
                res.update(resp)
                if resp["code"] == 0:
                    # 同步头像
                    g.api.usersso.clientsConSync(g.api.userapp.getUserApp, g.uid, dict(CallbackType="user_avatar", CallbackData=imgUrl))
    else:
        res.update(code=3, msg="Unsuccessfully obtained file or format is not allowed")
    logger.info(res)
    return jsonify(dfr(res))

@ApiBlueprint.route("/forgotpass/", methods=['POST'])
@apianonymous_required
def fgp():
    # 忘记密码页-重置密码
    res = dict(msg=None, code=1)
    if request.method == "POST":
        vcode = request.form.get("vcode")
        account = request.form.get("account")
        password = request.form.get("password")
        if vaptcha.validate:
            auth = Authentication(g.mysql, g.redis)
            result = auth.forgot(account=account, vcode=vcode, password=password)
            if result["success"]:
                res.update(code=0, nextUrl=url_for("front.signIn"))
            else:
                res.update(msg=result["msg"])
        else:
            res.update(msg="Man-machine verification failed")
    return jsonify(dfr(res))

@ApiBlueprint.route("/user/security/", methods=["GET", "POST", "DELETE"])
@apilogin_required
def usersecurity():
    res = dict(msg=None, code=1)
    Action = request.args.get("Action")
    if request.method == "GET":
        if Action == "getSessions":
            sd = analysis_sessionId(request.cookies.get("sessionId"))
            if sd:
                res.update(code=0)
                data = dict()
                # 获取当前会话
                if request.args.get("getCurrentSession", True) in (True, "True", "true"):
                    browserType, browserDevice, browserOs, browserFamily = parse_userAgent(request.headers.get("User-Agent"))
                    area = getIpArea(g.ip)
                    if len(area.split()) >= 3:
                        area = area.split()[2]
                    CurrentSession = dict(iat=sd['iat'], exp=sd['exp'], browser=dict(family=" ".join(browserFamily.split()[:-1]), os=browserOs), ip=g.ip, area=area)
                    if g.sid:
                        CurrentSession["session"] = g.api.usersso.ssoGetWithSid(g.sid, True)
                    data["CurrentSession"]=CurrentSession
                # 获取其他会话
                if request.args.get("getOtherSession") in (True, "True", "true"):
                    OtherSession = [ g.api.usersso.ssoGetWithSid(sid, True) for sid in g.api.usersso.ssoGetRegisteredUserSid(g.uid) if g.sid != sid and g.api.usersso.ssoExistWithSid(sid) ]
                    data["OtherSession"] = OtherSession
                res["data"] = data
        elif Action == "getLoginHistory":
            # 获取登录历史
            sort = request.args.get("sort") or "desc"
            page = request.args.get("page") or 1
            limit = request.args.get("limit") or 10
            res = g.api.userprofile.listUserLoginHistory(uid=g.uid, page=page, limit=limit, sort=sort)
    logger.info(res)
    return jsonify(dfr(res))


@ApiBlueprint.route("/user/login", methods=["POST"])
def userlogin():
    if request.method == 'POST':
        res = dict(code=1)
        auth = Authentication(g.mysql, g.redis)
        result = auth.signIn(
            account=request.form.get("account"),
            password=request.form.get("password")
        )
        if result["success"]:
            uid = result["uid"]
            # 记录登录日志
            auth.brush_loginlog(result, login_ip=g.ip, user_agent=g.agent)
            fields = request.form.get("fields") or "is_admin,avatar,nick_name"
            fields = [i for i in comma_pat.split(fields) if i]
            fields = list(set(fields).update(["avatar", "nick_name"]))
            infores = g.api.userprofile.getUserProfile(uid)
            data = {}
            if infores["code"] == 0:
                data = infores["data"]
            data.update(token=set_sessionId(uid, 7200))
            res.update(code=0, data={k: data[k] for k in fields if k in data})
        else:
            res.update(msg=result["msg"])
        return jsonify(dfr(res))
