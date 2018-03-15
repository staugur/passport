# -*- coding: utf-8 -*-
"""
    passport.views.ApiView
    ~~~~~~~~~~~~~~

    The blueprint for api view.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""
import json
import os.path
from config import VAPTCHA, UPYUN as Upyun
from utils.send_email_msg import SendMail
from utils.upyunstorage import CloudStorage
from utils.web import email_tpl, dfr, apilogin_required, apiadminlogin_required
from utils.tool import logger, generate_verification_code, email_check, phone_check, ListEqualSplit,  gen_rnd_filename, allowed_file
from vaptchasdk import vaptcha as VaptchaApi
from flask import Blueprint, request, jsonify, g
from werkzeug import secure_filename


# 初始化前台蓝图
ApiBlueprint = Blueprint("api", __name__)
# 初始化邮箱发送服务
sendmail = SendMail()
# 初始化手势验证码服务
vaptcha = VaptchaApi(VAPTCHA["vid"], VAPTCHA["key"])
# 又拍云存储封装接口
upyunapi = CloudStorage()


@ApiBlueprint.route('/miscellaneous/_sendVcode', methods=['POST'])
def misc_sendVcode():
    """发送验证码：邮箱、手机"""
    res = dict(msg=None, success=False)
    account = request.form.get("account")
    if email_check(account):
        email = account
        key = "passport:signUp:vcode:{}".format(email)
        try:
            hasKey = g.redis.exists(key)
        except Exception, e:
            logger.error(e, exc_info=True)
            res.update(msg="System is abnormal")
        else:
            if hasKey:
                res.update(msg="Have sent the verification code, please check the mailbox")
            else:
                vcode = generate_verification_code()
                result = sendmail.SendMessage(to_addr=email, subject=u"Passport邮箱注册验证码", formatType="html", message=email_tpl % (email, u"注册", vcode))
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
        res.update(msg="Not support phone number registration")
    else:
        res.update(msg="Invalid account")
    logger.debug(res)
    return jsonify(dfr(res))


@ApiBlueprint.route("/miscellaneous/_getChallenge")
def misc_getChallenge():
    """Vaptcha获取流水
    @param sceneid str: 场景id，如01登录、02注册
    """
    sceneid = request.args.get("sceneid") or ""
    return jsonify(json.loads(vaptcha.get_challenge(sceneid)))


@ApiBlueprint.route("/miscellaneous/_getDownTime")
def misc_getDownTime():
    """Vaptcha宕机模式
    like: ?data=request&_t=1516092685906
    """
    data = request.args.get("data")
    logger.info("vaptcha into downtime, get data: {}, query string: {}".format(data, request.args.to_dict()))
    return jsonify(json.loads(vaptcha.downtime(data)))


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
    logger.info(res)
    return jsonify(dfr(res))


@ApiBlueprint.route("/user/profile/", methods=["GET", "POST", "PUT"])
@apilogin_required
def userprofile():
    res = dict()
    if request.method == "GET":
        getBind = True if request.args.get("getBind") in ("true", "True", True) else False
        res = g.api.userprofile.getUserProfile(g.uid, getBind)
    elif request.method == "PUT":
        """修改个人资料，包含：基本资料、密码、头像、社交账号绑定"""
        Action = request.args.get("Action")
        if Action == "profile":
            data = {k: v for k, v in request.form.iteritems() if k in ("nick_name", "domain_name", "birthday", "location", "gender", "signature")}
            res = g.api.userprofile.updateUserProfile(uid=g.uid, **data)
            g.api.usersso.clientsConSync(g.api.userapp.getUserApp, g.sid, dict(CallbackType="user_profile", CallbackData=data))
        elif Action == "password":
            pass
            #res = g.api.user_update_password(g.token["username"], request.form.get("OldPassword"), request.form.get("NewPassword"))
    logger.info(res)
    return jsonify(dfr(res))


@ApiBlueprint.route('/user/upload/', methods=['POST', 'OPTIONS'])
@apilogin_required
def userupload():
    res = dict(code=1, msg=None)
    logger.debug(request.files)
    f = request.files.get('file')
    callableAction = request.args.get("callableAction")
    if f and allowed_file(f.filename):
        filename = secure_filename(gen_rnd_filename() + "." + f.filename.split('.')[-1])  # 随机命名
        basedir = Upyun['basedir'] if Upyun['basedir'].startswith('/') else "/" + Upyun['basedir']
        imgUrl = os.path.join(basedir, filename)
        try:
            upyunapi.put(imgUrl, f.stream.read())
        except Exception, e:
            logger.error(e, exc_info=True)
            res.update(code=2, msg="System is abnormal")
        else:
            imgUrl = Upyun['dn'].strip("/") + imgUrl
            res.update(imgUrl=imgUrl, code=0)
            if callableAction == "UpdateAvatar":
                res.update(g.api.userprofile.updateUserAvatar(uid=g.uid, avatarUrl=imgUrl))
    else:
        res.update(code=3, msg="Unsuccessfully obtained file or format is not allowed")
    logger.info(res)
    return jsonify(dfr(res))
