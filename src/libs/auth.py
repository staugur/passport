# -*- coding: utf-8 -*-
"""
    passport.libs.auth
    ~~~~~~~~~~~~~~

    登陆注册认证

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import json
from utils.tool import logger, get_current_timestamp, gen_uniqueId, email_check, phone_check
from torndb import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


class Authentication(object):
    """ 登陆注册类 """

    def __init__(self, mysql, redis):
        self.db = mysql
        self.rc = redis

    def __check_hasUser(self, uid):
        """检查是否存在账号"""
        if uid and len(uid) == 22:
            sql = "SELECT count(uid) FROM user_auth WHERE uid=%s"
            try:
                data = self.db.get(sql, uid)
            except Exception,e:
                logger.warn(e, exc_info=True)
            else:
                logger.debug(data)
                if data and isinstance(data, dict):
                    return True if data.get('count(uid)', 0) > 0 else False
        return False

    def __check_hasEmail(self, email):
        """检查是否存在邮箱账号"""
        if email_check(email):
            sql = "SELECT uid FROM user_auth WHERE identity_type=%s AND identifier=%s"
            try:
                data = self.db.get(sql, 2, email)
            except Exception,e:
                logger.warn(e, exc_info=True)
            else:
                logger.debug(data)
                if data and isinstance(data, dict):
                    return "uid" in data
        return False

    def __check_sendEmailVcode(self, email, vcode, scene="signUp"):
        """校验发送给邮箱的验证码
        @param email str: 邮箱账号
        @param vcode str: 验证码
        @param scene str: 校验场景 signUp-注册 signIn-登录 forgot-忘记密码
        """
        if email_check(email) and vcode and scene in ("signUp", "signIn", "forgot"):
            key = "passport:{}:vcode:{}".format(scene, email)
            if self.rc.exists(key):
                return self.rc.get(key) == vcode
        return False

    def __signUp_transacion(self, guid, identifier, identity_type, certificate, verified, register_ip, expire_time="", define_profile_sql=None):
        ''' begin的方式使用事务注册账号，
        参数：
            @param guid str: 系统账号唯一标识
            @param identifier str: 手机号、邮箱或第三方openid
            @param identity_type int: 账号类型，1手机号 2邮箱 3GitHub 4qq 5微信 6腾讯微博 7新浪微博
            @param certificate str: 加盐密码或第三方access_token
            @param verified int: 是否已验证 0-未验证 1-已验证
            @param register_ip str: 注册IP地址
            @param define_profile_sql str: 自定义写入`user_profile`表的sql(需要完整可直接执行SQL)
            @param expire_time int: 特指OAuth过期时间戳，暂时保留
        流程：
            1、写入`user_auth`表
            2、写入`user_profile`表
        返回字典：
            success bool 表示注册是否成功；
            msg str 表示提示信息。
        '''
        res = dict(success=False, msg=None)
        # 校验
        if guid and identifier and \
            identity_type and \
            certificate and \
            verified and \
            register_ip and \
            isinstance(guid, (str, unicode)) and \
            len(guid) == 22 and \
            identity_type in (1, 2, 3, 4, 5, 6, 7) and \
            verified in (1, 0):
            ctime = get_current_timestamp()
            try:
                logger.debug("transaction, start")
                self.db._db.begin()
                try:
                    sql_1 = "INSERT INTO user_auth (uid, identity_type, identifier, certificate, verified, status, create_time, expire_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    info = self.db.insert(sql_1, guid, identity_type, identifier, certificate, verified, 1, ctime, expire_time)
                    logger.debug("sql_1 info: {}".format(info))
                except IntegrityError:
                    res.update(msg="Account already exists")
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg="System is abnormal")
                else:
                    if define_profile_sql:
                        sql_2 = define_profile_sql
                        info = self.db.insert(sql_2)
                    else:
                        sql_2 = "INSERT INTO user_profile (uid, register_source, register_ip, create_time, is_realname, is_admin) VALUES (%s, %s, %s, %s, %s, %s)"
                        info = self.db.insert(sql_2, guid, identity_type, register_ip, ctime, 0, 0)
                    logger.debug("sql_2: {}, return info: {}".format(sql_2, info))
                    logger.debug('transaction, commit')
                    self.db._db.commit()
            except Exception, e:
                logger.debug('transaction, rollback', exc_info=True)
                res.update(msg="Operation failed, rolled back")
                self.db._db.rollback()
            else:
                logger.debug("transaction, over")
                if self.__check_hasUser(guid):
                    res.update(msg="Registration success", success=True)
                else:
                    res.update(msg="Registration failed")
        else:
            res.update(msg="Check failed")
        logger.info(res)
        return res

    def signUp(self, account, vcode, password, repassword, register_ip):
        """注册接口，面向前端
        参数：
            @param account str: 注册的账号，邮箱/手机号
            @param vcode str: 使用手机或邮箱的验证码
            @param password str: 密码
            @param repassword str: 重复密码
            @param register_ip str: 注册IP地址
        流程：
            1. 判断账号类型，仅支持邮箱、手机号两种本地账号。
            2. 校验密码、验证码是否合格、正确。
            3. 密码、验证码通过后，当为邮箱时，校验邮箱是否存在；当为手机时，校验手机是否存在。
            4. 生成guid，注册并响应事务结果。
        """
        res = dict(msg=None, success=False)
        # NO.1 检查账号类型
        if email_check(account):
            # 账号类型：邮箱
            # NO.2 检查密码、验证码
            if password and repassword and password == repassword and 6 <= len(password) <= 30:
                certificate = generate_password_hash(password)
                if vcode and len(vcode) == 6 and self.__check_sendEmailVcode(account, vcode, scene="signUp"):
                    # NO.3 检查账号是否存在
                    if self.__check_hasEmail(account):
                        res.update(msg="Email already exists")
                    else:
                        guid = gen_uniqueId()
                        upts = self.__signUp_transacion(guid=guid, identifier=account, identity_type=2, certificate=certificate, verified=1, register_ip=register_ip)
                        res.update(upts)
                else:
                    res.update(msg="Invalid verification code")
            else:
                res.update(msg="Invalid password: Inconsistent password or length failed twice")
        elif phone_check(account):
            # 账号类型：手机
            res.update(msg="Not support phone number registration")
        else:
            # 账号类型：非法，拒绝
            res.update(msg="Invalid account")
        logger.info(res)
        return res

    def signIn(self, account, password):
        """登录接口，面向前端
        参数：
            @param account str: 注册时的账号，邮箱/手机号
            @param password str: 密码
        流程：
            1. 判断账号类型，仅支持邮箱、手机号两种本地账号。
            2. 校验账号(是否合法、启用状态等)。
            3. 校验密码(是否合格、正确)。
        """
        res = dict(msg=None, success=False)
        # NO.1 检查账号类型
        if email_check(account):
            # 账号类型：邮箱
            identity_type = 2
            # NO.2 检查账号
            if password and 6 <= len(password) < 30:
                sql = "SELECT uid,certificate FROM user_auth WHERE identity_type=%s AND identifier=%s AND status=1"
                try:
                    data = self.db.get(sql, identity_type, account)
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg="System is abnormal")
                else:
                    if data and isinstance(data, dict):
                        uid = data["uid"]
                        certificate = data["certificate"]
                        if check_password_hash(certificate, password):
                            res.update(success=True, uid=uid, identity_type=identity_type)
                        else:
                            res.update(msg="Wrong password")
                    else:
                        res.update(msg="Invalid account: does not exist or has been disabled")
            else:
                res.update(msg="Invalid password: length unqualified")
        elif phone_check(account):
            # 账号类型：手机
            res.update(msg="Temporarily do not support phone number login")
        else:
            # 账号类型：非法，拒绝
            res.update(msg="Invalid account")
        logger.info(res)
        return res

    def brush_loginlog(self, signInResult, login_ip, user_agent):
        """ 将登录日志写入redis，需有定时任务每分钟解析入库
        @param signInResult dict: 登录接口返回
            @param uid str: 用户全局唯一标识id
            @param identity_type int: 登录类型，1手机号 2邮箱 3GitHub 4qq 5微信 6腾讯微博 7新浪微博
        @param login_ip str: 登录IP
        @param user_agent str: 用户代理
        """
        if isinstance(signInResult, dict):
            if signInResult["success"]:
                data = dict(
                    uid = signInResult["uid"],
                    identity_type = signInResult["identity_type"],
                    login_ip = login_ip,
                    user_agent = user_agent,
                    login_time = get_current_timestamp()
                )
                key = "passport:loginlog"
                return self.rc.rpush(key, json.dumps(data))

    def __oauth2_getUid(self, openid):
        """根据openid获取uid"""
        sql = "SELECT uid FROM user_auth WHERE identifier=%s"
        try:
            data = self.db.get(sql, openid)
        except Exception,e:
            logger.error(e, exc_info=True)
        else:
            if data and isinstance(data, dict):
                return data.get("uid") or None

    def oauth2_go(self, name, signin, tokeninfo, userinfo, register_ip, uid=None):
        """第三方账号登录入口
        参数：
            @param name str: 开放平台标识，3GitHub 4qq 5微信 6腾讯微博 7新浪微博
            @param signin bool: 是否已登录
            @param tokeninfo dict: access_token数据，格式：
                {
                    "access_token": "ACCESS_TOKEN",
                    "expires_in": "可选，到期时间戳，默认0不限制",
                    "refresh_token": "可选，刷新TOKEN"
                }
            @param userinfo dict: 用户数据，包含用户基本信息及用户在第三方网站唯一标识，格式：
                {
                    "openid": "用户唯一标识",
                    "gender": "性别",
                    "nick_name": "昵称",
                    "avatar": "头像地址",
                    "domain_name": "可选，个性域名，针对weibo"
                    "signature": "可选，签名，针对github"
                }
            @param register_ip str: 注册IP地址
            @param uid str: 系统本地用户id，当`signin=True`时，此值必须为实际用户id
        流程：
            1. signin字段判断是否登录
            - 已登录，说明已有账号，只需绑定账号即可
                1. 判断uid参数，有意义则查询openid是否绑定uid，否则返回失败信息。
                2. 如果openid返回uid，说明已经绑定，然后判断绑定账号与uid参数是否一致，一致则尝试更新绑定数据，完成绑定；不一致表示已经绑定其他账号，拒绝操作并返回原页面。
                3. 如果openid返回None，说明没有绑定，则直接注册并绑定uid参数。
            - 未登录，可能无账号、可能有账号
                1. 查询openid是否绑定uid。
                2. 如果openid返回uid，说明已经绑定，转入登录流程，需要设置cookie登录状态。
                3. 如果openid返回None，说明没有绑定，此时需要设置是否页面绑定本地账号或直接注册。
        """
        res = dict(msg=None, success=False, pageAction=None)
        if isinstance(name, (str, unicode)) and \
            signin in (True, False) and \
            isinstance(tokeninfo, dict) and \
            isinstance(userinfo, dict) and \
            "access_token" in tokeninfo and \
            "openid" in userinfo and \
            "nick_name" in userinfo and \
            "gender" in userinfo and \
            "avatar" in userinfo:
            # openid是第三方平台用户唯一标识，微博是uid，QQ是openid，Github是id，统一更新为openid
            openid = userinfo["openid"]
            access_token = tokeninfo["access_token"]
            expires_in = tokeninfo.get("expires_in") or 0
            gender = userinfo["gender"]
            nick_name = userinfo["nick_name"]
            avatar = userinfo["avatar"]
            domain_name = userinfo.get("domain_name", "")
            signature = userinfo.get("signature", "")
            if signin is True:
                # 已登录流程
                if uid:
                    guid = self.__oauth2_getUid(openid)
                    if guid:
                        if uid == guid:
                            # 更新绑定的数据
                            res.update(success=True)
                        else:
                            res.update(msg="Has been bound to other accounts")
                    else:
                        # 此openid没有绑定任何本地账号
                        define_profile_sql = "INSERT INTO user_profile (uid, register_source, register_ip, nick_name, domain_name, gender, signature, avatar, create_time, is_realname, is_admin) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %(uid, self.oauth2_name2type(name), register_ip, nick_name, domain_name, gender, signature, avatar, get_current_timestamp(), 0, 0)
                        UPDATE user_profile SET uid='2XyKu82nFWoT9HUoKUwhVQ', register_source='2', register_ip='127.0.0.1', nick_name='', domain_name='', gender='2', birthday='0', signature='', avatar='', curr_nation=NULL, curr_province=NULL, curr_city=NULL, create_time='1516075478', update_time=NULL, is_realname='0', is_admin='0', retain=NULL WHERE (uid='2XyKu82nFWoT9HUoKUwhVQ');

                        print define_profile_sql
                        upts = self.__signUp_transacion(uid, openid, self.oauth2_name2type(name), access_token, 1, register_ip, expires_in, define_profile_sql)
                        res.update(upts)
                else:
                    res.update(msg="Third-party login binding failed")
            else:
                # 未登录流程
                guid = self.__oauth2_getUid(openid)
                if guid:
                    # 已经绑定过账号，需要设置登录态
                    res.update(pageAction="goto_signIn")
                else:
                    # 尚未绑定，需要绑定注册
                    res.update(pageAction="goto_signUp")
        else:
            res.update(msg="Check failed")
        logger.info(res)
        return res

    def oauth2_name2type(self, name):
        """将第三方登录根据name转化为对应数字
        @param name str: OAuth name
        1手机号 2邮箱 3GitHub 4qq 5微信 6腾讯微博 7新浪微博
        """
        BIND = dict(
            mobile = 1,
            email = 2,
            github = 3,
            qq = 4,
            wechat = 5,
            wexin = 5,
            tencentweibo = 6,
            weibo = 7,
            sinaweibo = 7
        )
        return BIND[name]
