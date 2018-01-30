# -*- coding: utf-8 -*-
"""
    passport.views.ApiView
    ~~~~~~~~~~~~~~

    The blueprint for api view.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""
import json
from config import VAPTCHA
from utils.send_email_msg import SendMail
from utils.web import email_tpl, dfr, apilogin_required, apiadminlogin_required
from utils.tool import logger, generate_verification_code, email_check, phone_check, ListEqualSplit, md5, gen_token, Universal_pat, url_pat, get_current_timestamp
from vaptchasdk import vaptcha as VaptchaApi
from flask import Blueprint, request, jsonify, g
from torndb import IntegrityError


#初始化前台蓝图
ApiBlueprint = Blueprint("api", __name__)
#初始化邮箱发送服务
sendmail = SendMail()
#初始化手势验证码服务
vaptcha = VaptchaApi(VAPTCHA["vid"], VAPTCHA["key"])

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
        except:
            res.update(code=2, msg="There are invalid parameters")
        else:
            sql = "SELECT id,uid,name,description,app_id,app_secret,app_redirect_url,ctime,mtime FROM sso_apps WHERE uid=%s"
            data = g.mysql.query(sql, g.uid)
            if data:
                data = [ i for i in sorted(data, reverse=False if sort == "asc" else True) ]
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
        logger.debug("name: {}, redirect: {}".format(name, app_redirect_url))
        if name and description and app_redirect_url and Universal_pat.match(name) and url_pat.match(app_redirect_url):
            app_id = md5(name)
            app_secret = gen_token(36)
            ctime = get_current_timestamp()
            sql = "INSERT INTO sso_apps (uid, name, description, app_id, app_secret, app_redirect_url, ctime) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            try:
                g.mysql.insert(sql, g.uid, name, description, app_id, app_secret, app_redirect_url, ctime)
            except IntegrityError:
                res.update(msg="Name already exists", code=2)
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(code=0)
        else:
            res.update(msg="There are invalid parameters", code=4)
    elif request.method == "PUT":
        name = request.form.get("name")
        description = request.form.get("description")
        app_redirect_url = request.form.get("app_redirect_url")
        logger.debug("name: {}, redirect: {}".format(name, app_redirect_url))
        if name and description and app_redirect_url and Universal_pat.match(name) and url_pat.match(app_redirect_url):
            mtime = get_current_timestamp()
            sql = "UPDATE sso_apps SET description=%s, app_redirect_url=%s, mtime=%s WHERE name=%s"
            try:
                g.mysql.update(sql, description, app_redirect_url, mtime, name)
            except IntegrityError:
                res.update(msg="Name already exists", code=2)
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(code=0)
        else:
            res.update(msg="There are invalid parameters", code=4)
    elif request.method == "DELETE":
        name = request.form.get("name")
        if name:
            sql = "DELETE FROM sso_apps WHERE name=%s"
            try:
                g.mysql.execute(sql, name)
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(code=0)
        else:
            res.update(msg="There are invalid parameters", code=4)
    logger.info(res)
    return jsonify(dfr(res))
