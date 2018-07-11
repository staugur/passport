# -*- coding: utf-8 -*-
"""
    passport.libs.auth
    ~~~~~~~~~~~~~~

    登陆注册认证

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import json
from utils.tool import logger, get_current_timestamp, gen_uniqueId, email_check, phone_check, create_redis_engine, create_mysql_engine
from utils.web import oauth2_name2type, cbc
from torndb import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


class Authentication(object):
    """ 登陆注册类 """

    def __init__(self, mysql=None, redis=None):
        self.db = mysql or create_mysql_engine()
        self.rc = redis or create_redis_engine()

    def __check_hasUser(self, uid):
        """检查是否存在账号"""
        if uid and len(uid) == 22:
            sql = "SELECT count(uid) FROM user_auth WHERE uid=%s"
            try:
                data = self.db.get(sql, uid)
            except Exception, e:
                logger.warn(e, exc_info=True)
            else:
                logger.debug(data)
                if data and isinstance(data, dict):
                    return True if data.get('count(uid)', 0) > 0 else False
        return False

    def __check_hasEmail(self, email, getUid=False):
        """检查是否存在邮箱账号，不检测账号状态"""
        if email_check(email):
            sql = "SELECT uid FROM user_auth WHERE identity_type=2 AND identifier=%s"
            try:
                data = self.db.get(sql, email)
            except Exception, e:
                logger.warn(e, exc_info=True)
            else:
                logger.debug(data)
                if data and isinstance(data, dict):
                    success = "uid" in data
                    return data["uid"] if success and getUid else success
        return False

    def __check_hasPhone(self, phone, getUid=False):
        """检查是否存在手机账号，不检测账号状态"""
        if phone_check(phone):
            sql = "SELECT uid FROM user_auth WHERE identity_type=1 AND identifier=%s"
            try:
                data = self.db.get(sql, phone)
            except Exception, e:
                logger.warn(e, exc_info=True)
            else:
                logger.debug(data)
                if data and isinstance(data, dict):
                    success = "uid" in data
                    return data["uid"] if success and getUid else success
        return False

    def __check_sendVcode(self, account, vcode, scene="signUp"):
        """校验发送的验证码
        @param account str: 邮箱或手机号
        @param vcode str: 验证码
        @param scene str: 校验场景 signUp-注册 bindLauth-绑定本地账号 forgot-忘记密码
        """
        if email_check(account) or phone_check(account):
            if vcode and len(vcode) == 6 and scene in ("signUp", "bindLauth", "forgot"):
                key = "passport:vcode:{}:{}".format(scene, account)
                return self.rc.get(key) == vcode
        return False

    def __checkUserPassword(self, uid, password):
        """校验用户密码 <- hlm._userprofile.__checkUserPassword
        @param password str: 要校验的密码
        """
        if uid and len(uid) == 22 and password and 6 <= len(password) <= 30:
            sql = "SELECT certificate FROM user_auth WHERE identity_type IN (1,2) AND uid=%s"
            try:
                data = self.db.query(sql, uid)
            except Exception, e:
                logger.error(e, exc_info=True)
            else:
                if data and isinstance(data, (list, tuple)):
                    certificate = data[0]["certificate"]
                    return check_password_hash(certificate, password)
        return False

    def bindLauth(self, uid, account, vcode, password):
        """绑定本地化账号，需要密码做校验或重置
        参数：
            @param account str: 注册时的账号，邮箱/手机号
            @param vcode str: 验证码
            @param password str: 密码
        流程：
            1. 检查参数是否合法
            2. 检查账号类型、验证码
            3. 检查用户是否有本地化账号
                3.1 无本地化账号时，需要password参数生成密码，并且插入数据；
                3.2 有本地化账号时，需要校验password是否匹配，匹配后：
                    3.3 如果账号类型已经绑定，则修改，否则插入
        """
        res = dict(msg=None, success=False, show_realname_tip=False)
        # NO.1
        if uid and len(uid) == 22 and account and vcode and len(vcode) == 6 and password and 6 <= len(password) <= 30:
            # NO.2
            if email_check(account) or phone_check(account):
                if self.__check_sendVcode(account, vcode, "bindLauth"):
                    # NO.3
                    user_its = self.__list_identity_type(uid)
                    identity_type = 1 if phone_check(account) else 2
                    # `绑定邮箱或手机`函数
                    def bindEmailOrPhone():
                        res = dict(success=False)
                        sql = "INSERT INTO user_auth (uid, identity_type, identifier, certificate, verified, status, ctime) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        try:
                            self.db.insert(sql, uid, identity_type, account, generate_password_hash(password), 1, 1, get_current_timestamp())
                        except IntegrityError:
                            res.update(msg="Account already bind")
                        except Exception,e:
                            logger.error(e, exc_info=True)
                            res.update(msg="System is abnormal")
                        else:
                            res.update(success=True)
                        if res["success"] and identity_type == 1:
                            # 只有第一次绑定手机成功时设置为实名用户
                            res.update(show_realname_tip=True)
                        return res
                    # 用户的所有账号类型中包含1或2即存在本地化账号
                    if 1 in user_its or 2 in user_its:
                        # NO3.2 有本地化账号
                        if self.__checkUserPassword(uid, password):
                            # NO3.3
                            if identity_type in user_its:
                                # 修改邮箱或手机
                                sql = "UPDATE user_auth SET identifier=%s,mtime=%s WHERE identity_type=%s AND uid=%s"
                                try:
                                    self.db.update(sql, account, get_current_timestamp(), identity_type, uid)
                                except Exception,e:
                                    logger.error(e, exc_info=True)
                                    res.update(msg="System is abnormal")
                                else:
                                    res.update(success=True)
                            else:
                                # 绑定邮箱或手机
                                res.update(bindEmailOrPhone())
                        else:
                            res.update(msg="Wrong password")
                    else:
                        # NO3.1 无本地化账号, 绑定邮箱或手机
                        res.update(bindEmailOrPhone())

                else:
                    res.update(msg="Invalid verification code")
            else:
                res.update(msg="Invalid account")
        else:
            res.update(msg="There are invalid parameters")
        logger.info(res)
        return res

    def __list_identity_type(self, uid):
        """查询用户id绑定的所有账号类型，不检测账号状态
        @param uid str:用户id
        """
        if uid:
            sql = "SELECT identity_type FROM user_auth WHERE uid=%s"
            try:
                data = self.db.query(sql, uid)
            except Exception, e:
                logger.error(e, exc_info=True)
            else:
                if data and isinstance(data, (list, tuple)):
                    return tuple([ int(i["identity_type"]) for i in data ])
        return tuple()

    def __remove_identity_type(self, uid, identity_type):
        """删除用户某个绑定的`identity_type`
        @param uid str:用户id
        @param identity_type int: 账号类型，参见`oauth2_name2type`函数 
        """
        res = dict(msg=None)
        if uid and identity_type in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9):
            sql = "DELETE FROM user_auth WHERE identity_type={} AND uid=%s".format(identity_type)
            try:
                data = self.db.execute(sql, uid)
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal")
            else:
                res.update(code=0)
        else:
            res.update(msg="Check failed")
        return res

    def __get_registerSource(self, uid):
        """获取用户的注册源"""
        sql = "SELECT register_source FROM user_profile where uid=%s"
        if uid:
            try:
                data = self.db.get(sql, uid)
            except Exception, e:
                logger.error(e, exc_info=True)
            else:
                if data and isinstance(data, dict):
                    return int(data["register_source"])

    def __signUp_transacion(self, guid, identifier, identity_type, certificate, verified=1, register_ip="", expire_time=0, is_realname=0, use_profile_sql=True, define_profile_sql=None):
        ''' begin的方式使用事务注册账号，
        参数：
            @param guid str: 系统账号唯一标识
            @param identifier str: 手机号、邮箱或第三方openid
            @param identity_type int: 账号类型，参见`oauth2_name2type`函数
            @param certificate str: 加盐密码或第三方access_token
            @param verified int: 是否已验证 0-未验证 1-已验证
            @param register_ip str: 注册IP地址
            @param expire_time int: 特指OAuth过期时间戳，暂时保留
            @param is_realname int: 是否实名，1-实名(手机注册或绑定)， 0-未实名
            @param use_profile_sql bool: 定义是否执行define_profile_sql
            @param define_profile_sql str: 自定义写入`user_profile`表的sql(需要完整可直接执行SQL)
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
                isinstance(guid, (str, unicode)) and \
                len(guid) == 22 and \
                identity_type in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9) and \
                verified in (1, 0) and \
                is_realname in (1, 0):
            ctime = get_current_timestamp()
            try:
                logger.debug("transaction, start")
                self.db._db.begin()
                try:
                    sql_1 = "INSERT INTO user_auth (uid, identity_type, identifier, certificate, verified, status, ctime, etime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    info = self.db.insert(sql_1, guid, identity_type, identifier, certificate, verified, 1, ctime, expire_time)
                except IntegrityError:
                    res.update(msg="Account already exists")
                except Exception, e:
                    logger.error(e, exc_info=True)
                    res.update(msg="System is abnormal")
                else:
                    if use_profile_sql is True:
                        if define_profile_sql:
                            sql_2 = define_profile_sql
                            logger.info("execute define_profile_sql: {}".format(sql_2))
                            try:
                                info = self.db.execute(sql_2)
                            except:
                                raise
                        else:
                            sql_2 = "INSERT INTO user_profile (uid, register_source, register_ip, ctime, is_realname, is_admin) VALUES (%s, %s, %s, %s, %s, %s)"
                            try:
                                info = self.db.insert(sql_2, guid, identity_type, register_ip, ctime, is_realname, 0)
                            except:
                                raise
                    logger.debug('transaction, commit')
                    self.db._db.commit()
            except Exception, e:
                logger.error(e, exc_info=True)
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
            # 2、1调整下顺序可以减少代码或者参考signIn合并
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
                if vcode and len(vcode) == 6 and self.__check_sendVcode(account, vcode, "signUp"):
                    # NO.3 检查账号是否存在
                    if self.__check_hasEmail(account):
                        res.update(msg="Email already exists")
                    else:
                        guid = gen_uniqueId()
                        upts = self.__signUp_transacion(guid=guid, identifier=account, identity_type=2, certificate=certificate, verified=1, register_ip=register_ip)
                        res.update(upts)
                        res.update(uid=guid)
                else:
                    res.update(msg="Invalid verification code")
            else:
                res.update(msg="Invalid password: Inconsistent password or length failed twice")
        elif phone_check(account):
            # 账号类型：手机
            # NO.2 检查密码、验证码
            if password and repassword and password == repassword and 6 <= len(password) <= 30:
                certificate = generate_password_hash(password)
                if vcode and len(vcode) == 6 and self.__check_sendVcode(account, vcode, "signUp"):
                    # NO.3 检查账号是否存在
                    if self.__check_hasPhone(account):
                        res.update(msg="Phone already exists")
                    else:
                        guid = gen_uniqueId()
                        upts = self.__signUp_transacion(guid=guid, identifier=account, identity_type=1, certificate=certificate, verified=1, register_ip=register_ip, is_realname=1)
                        res.update(upts)
                        res.update(uid=guid)
                else:
                    res.update(msg="Invalid verification code")
            else:
                res.update(msg="Invalid password: Inconsistent password or length failed twice")
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
        if email_check(account) or phone_check(account):
            # 账号类型：邮箱、手机
            identity_type = 2 if email_check(account) else 1
            # NO.2 检查账号
            if password and 6 <= len(password) < 30:
                sql = "SELECT uid,certificate FROM user_auth WHERE identity_type={} AND identifier=%s AND status=1".format(identity_type)
                try:
                    data = self.db.get(sql, account)
                except Exception, e:
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
        else:
            # 账号类型：非法，拒绝
            res.update(msg="Invalid account")
        logger.info(res)
        return res

    def brush_loginlog(self, signInResult, login_ip, user_agent):
        """ 将登录日志写入redis，需有定时任务每分钟解析入库
        @param signInResult dict: 登录接口返回
            @param uid str: 用户全局唯一标识id
            @param identity_type int: 登录类型，参见`oauth2_name2type`函数
        @param login_ip str: 登录IP
        @param user_agent str: 用户代理
        """
        if isinstance(signInResult, dict):
            if signInResult["success"]:
                data = dict(
                    uid=signInResult["uid"],
                    identity_type=signInResult["identity_type"],
                    login_ip=login_ip,
                    user_agent=user_agent,
                    login_time=get_current_timestamp()
                )
                key = "passport:loginlog"
                return self.rc.rpush(key, json.dumps(data))

    def __oauth2_getUid(self, openid):
        """根据openid获取uid"""
        sql = "SELECT uid FROM user_auth WHERE identifier=%s"
        try:
            data = self.db.get(sql, openid)
        except Exception, e:
            logger.error(e, exc_info=True)
        else:
            if data and isinstance(data, dict):
                return data.get("uid") or None

    def __oauth2_setUserinfo(self, userinfo):
        """缓存`oauth2_go返回pageAction=goto_signUp时的goto_signUp_data`数据
        @param userinfo dict: 同`oauth2_go`的userinfo
        """
        if userinfo and isinstance(userinfo, dict) and "openid" in userinfo and "identity_type" in userinfo and "avatar" in userinfo and "nick_name" in userinfo:
            key = "passport:oauth2_cachedUserinfo:{}".format(userinfo["openid"])
            success = self.rc.hmset(key, userinfo)
            if success:
                self.rc.expire(key, 600)
            return success

    def __oauth2_getUserinfo(self, openid):
        """查询`__oauth2_cacheUserinfo`接口缓存的数据
        @param openid str: 加密后的openid
        """
        try:
            openid = cbc.decrypt(openid)
        except:
            return None
        else:
            key = "passport:oauth2_cachedUserinfo:{}".format(openid)
            return self.rc.hgetall(key) or None

    def __oauth2_delUserinfo(self, openid):
        """删除`__oauth2_cacheUserinfo`接口缓存的数据
        @param openid str: 未加密的openid
        """
        if openid:
            key = "passport:oauth2_cachedUserinfo:{}".format(openid)
            return self.rc.delete(key) or None

    def oauth2_go(self, name, signin, tokeninfo, userinfo, uid=None):
        """第三方账号登录入口
        参数：
            @param name str: 开放平台标识，参见`oauth2_name2type`函数
            @param signin bool: 是否已登录
            @param tokeninfo dict: access_token数据，格式：
                {
                    "access_token": "ACCESS_TOKEN",
                    "expires_in": "可选，到期时间戳，默认0不限制",
                    "refresh_token": "可选，刷新TOKEN"
                }
            @param userinfo dict: 用户数据，包含用户基本信息及用户在第三方网站唯一标识，主要用于注册流程，格式：
                {
                    "openid": "用户唯一标识",
                    "nick_name": "昵称",
                    "avatar": "头像地址",
                    "gender": "可选，性别"，默认2,
                    "signature": "可选，签名，针对github"
                }
            @param uid str: 系统本地用户id，当`signin=True`时，此值必须为实际用户id
        流程：
            1. signin字段判断是否登录
            - 已登录，说明已有账号，只需绑定账号即可
                1. 判断uid参数，有意义则查询openid是否绑定uid，否则返回失败信息。
                2. 如果openid返回uid，说明已经绑定，然后判断绑定账号与uid参数是否一致，一致则尝试更新绑定数据，完成绑定；不一致表示已经绑定其他账号，拒绝操作并返回原页面。
                3. 如果openid返回None，说明没有绑定，则直接注册并绑定uid参数。
            - 未登录，可能无账号、可能有账号，需要直接注册或绑定已有
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
                "avatar" in userinfo:
            # openid是第三方平台用户唯一标识，微博是uid，QQ是openid，Github是id，统一更新为openid
            access_token = tokeninfo["access_token"]
            expires_in = tokeninfo.get("expires_in") or 0
            # 重新定义openid规则->加上开放平台前缀
            openid = "{}.{}".format(oauth2_name2type(name), userinfo["openid"])
            # 覆盖原openid
            userinfo.update(openid=openid)
            if signin is True:
                # 已登录->绑定流程
                logger.debug("signin true, uid: {}".format(uid))
                if uid:
                    guid = self.__oauth2_getUid(openid)
                    logger.debug("signin true, openid: {}, guid: {}, is equal: {}".format(openid, guid, uid == guid))
                    if guid:
                        if uid == guid:
                            # 更新绑定的数据
                            res.update(success=True)
                        else:
                            res.update(msg="Has been bound to other accounts")
                    else:
                        # 此openid没有绑定任何本地账号，更新用户资料
                        upts = self.__signUp_transacion(guid=uid, identifier=openid, identity_type=oauth2_name2type(name), certificate=access_token, verified=1, expire_time=expires_in, use_profile_sql=False)
                        res.update(upts)
                else:
                    res.update(msg="Third-party login binding failed")
            else:
                # 未登录->注册绑定流程
                guid = self.__oauth2_getUid(openid)
                if guid:
                    # 已经绑定过账号，需要设置登录态
                    res.update(pageAction="goto_signIn", goto_signIn_data=dict(guid=guid))
                else:
                    # 尚未绑定，需要绑定注册
                    userinfo.update(identity_type=oauth2_name2type(name), access_token=access_token, expires_in=expires_in)
                    if self.__oauth2_setUserinfo(userinfo):
                        res.update(pageAction="goto_signUp", goto_signUp_data=dict(openid=cbc.encrypt(openid)))
                    else:
                        res.update(msg="System is abnormal")
        else:
            res.update(msg="Check failed")
        logger.info(res)
        return res

    def oauth2_signUp(self, openid, register_ip):
        """OAuth直接登录时注册入系统
        @param openid str: 加密的openid，用以获取缓存中数据userinfo，格式是：
            userinfo dict: 用户信息，必须包含`openid`,`identity_type`,`avatar`,`nick_name`
        @param register_ip str: 注册IP地址
        """
        res = dict(msg=None, success=False)
        userinfo = self.__oauth2_getUserinfo(openid)
        logger.debug(userinfo)
        logger.debug(type(userinfo))
        if userinfo and isinstance(userinfo, dict) and "avatar" in userinfo and "nick_name" in userinfo and "openid" in userinfo and "access_token" in userinfo and "identity_type" in userinfo:
            openid = userinfo["openid"]
            access_token = userinfo["access_token"]
            identity_type = int(userinfo["identity_type"])
            avatar = userinfo["avatar"]
            nick_name = userinfo["nick_name"]
            gender = int(userinfo.get("gender") or 2)
            signature = userinfo.get("signature") or ""
            location = userinfo.get("location") or ""
            expire_time = userinfo.get("expire_time") or 0
            guid = gen_uniqueId()
            logger.debug("check test: guid length: {}, identifier: {}, identity_type:{}, identity_type: {}, certificate: {}".format(len(guid), openid, identity_type, type(identity_type), access_token))
            define_profile_sql = "INSERT INTO user_profile (uid, register_source, register_ip, nick_name, gender, signature, avatar, location, ctime, is_realname, is_admin) VALUES ('%s', %d, '%s', '%s', %d, '%s', '%s', '%s', %d, %d, %d)" % (guid, identity_type, register_ip, nick_name, gender, signature, avatar, location, get_current_timestamp(), 0, 0)
            upts = self.__signUp_transacion(guid=guid, identifier=openid, identity_type=identity_type, certificate=access_token, verified=1, register_ip=register_ip, expire_time=expire_time, define_profile_sql=define_profile_sql)
            res.update(upts)
            if res["success"]:
                self.__oauth2_delUserinfo(openid)
                res.update(identity_type=identity_type, uid=guid)
        else:
            res.update(msg="Check failed")
        logger.info(res)
        return res

    def oauth2_bindLogin(self, openid, account, password):
        """OAuth绑定账号并登录系统
        @param openid str: 加密的openid
        @param account str: 同`signIn`中account
        @param password str: 同`signIn`中password
        """
        res = dict(msg=None, success=False)
        userinfo = self.__oauth2_getUserinfo(openid)
        logger.debug(userinfo)
        logger.debug(type(userinfo))
        if userinfo and isinstance(userinfo, dict) and "avatar" in userinfo and "nick_name" in userinfo and "openid" in userinfo and "access_token" in userinfo and "identity_type" in userinfo:
            res = self.signIn(account, password)
            openid = userinfo["openid"]
            logger.debug(res)
            if res["success"] is True:
                # 登录成功，即可绑定openid到uid，无需校验(goto_signUp已经校验)
                uid = res["uid"]
                access_token = userinfo["access_token"]
                identity_type = int(userinfo["identity_type"])
                expire_time = userinfo.get("expire_time") or 0
                upts = self.__signUp_transacion(guid=uid, identifier=openid, identity_type=identity_type, certificate=access_token, verified=1, expire_time=expire_time, use_profile_sql=False)
                res.update(upts)
                if res["success"] is True:
                    self.__oauth2_delUserinfo(openid)
        else:
            res.update(msg="Check failed")
        logger.info(res)
        return res

    def unbind(self, uid, identity_type):
        """解绑OAuth账号，要求已经登录系统
        参数：
            @param uid str: 用户id
            @param identity_type int: 账号类型，参见`oauth2_name2type`函数
        流程：
            1. 检测此`identity_type`是否是否为注册源
            2. 是注册源（使用此`identity_type`直接登录用户）：
                2.1 只有绑定了邮箱、手机以及设置了密码才允许解绑；
                2.2 上一条校验通过，则删除`user_auth`中`identity_type`对应条目
            3. 不是注册源（使用此`identity_type`绑定的用户）：
                3.1 直接删除`user_auth`中`identity_type`对应条目
        """
        res = dict(msg=None, code=1)
        if uid and identity_type and identity_type in (3, 4, 5, 6, 7, 8, 9):
            register_source = self.__get_registerSource(uid)
            if register_source and isinstance(register_source, int):
                if register_source == identity_type:
                    # 是注册源流程
                    identity_types = self.__list_identity_type(uid)
                    if 2 in identity_types or 1 in identity_types:
                        # 这里需设计为绑定了2-email、1-mobile时已经设置密码
                        res.update(self.__remove_identity_type(uid, identity_type))
                    else:
                        res.update(msg="Please bind the email or phone first", code=2)
                else:
                    # 非注册源流程
                    res.update(self.__remove_identity_type(uid, identity_type))
            else:
                res.update(msg="System is abnormal")
        else:
            res.update(msg="Check failed")
        logger.info(res)
        return res

    def forgot(self, account, vcode, password):
        """忘记密码接口
        参数：
            @param account str: 注册时的账号，邮箱/手机号
            @param vcode str: 验证码
            @param password str: 新设置的密码
        流程：
            1. 判断账号类型，仅支持邮箱、手机号两种本地账号。
            2. 校验账号是否存在。
            3. 校验验证码。
            4. 以上3步验证通过重置uid所有类型密码
        """
        res = dict(msg=None, success=False)
        # NO.1 检查账号类型
        if email_check(account):
            # NO.2 检查账号
            uid = self.__check_hasEmail(account, getUid=True)
            if uid:
                # NO.3 检查验证码
                if vcode and len(vcode) == 6 and self.__check_sendVcode(account, vcode, "forgot"):
                    # NO.4 重置密码
                    if password and 6 <= len(password) <= 30:
                        certificate = generate_password_hash(password)
                        try:
                            sql = "UPDATE user_auth SET certificate=%s WHERE identity_type in (1,2) AND uid=%s"
                            data = self.db.update(sql, certificate, uid)
                        except Exception, e:
                            logger.error(e, exc_info=True)
                            res.update(msg="System is abnormal")
                        else:
                            res.update(success=True)
                    else:
                        res.update(msg="Invalid password: length unqualified")
                else:
                    res.update(msg="Invalid verification code")
            else:
                res.update(msg="Invalid account")
        elif phone_check(account):
            # 账号类型：手机
            uid = self.__check_hasPhone(account, getUid=True)
            if uid:
                # NO.3 检查验证码
                if vcode and len(vcode) == 6 and self.__check_sendVcode(account, vcode, "forgot"):
                    # NO.4 重置密码
                    if password and 6 <= len(password) <= 30:
                        certificate = generate_password_hash(password)
                        try:
                            sql = "UPDATE user_auth SET certificate=%s WHERE identity_type in (1,2) AND uid=%s"
                            data = self.db.update(sql, certificate, uid)
                        except Exception, e:
                            logger.error(e, exc_info=True)
                            res.update(msg="System is abnormal")
                        else:
                            res.update(success=True)
                    else:
                        res.update(msg="Invalid password: length unqualified")
                else:
                    res.update(msg="Invalid verification code")
            else:
                res.update(msg="Invalid account")
        else:
            # 账号类型：非法，拒绝
            res.update(msg="Invalid account")
        logger.info(res)
        return res

