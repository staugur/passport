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
from user_agents import parse as user_agents_parse


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

    def __signUp_transacion(self, guid, identifier, identity_type, certificate, verified, register_ip, register_source):
        ''' begin的方式使用事务注册账号，
        参数：
            @param identifier str: 手机号或邮箱号
            @param identity_type int: 账号类型，1-手机 2-邮箱
            @param certificate str: 加盐密码
            @param verified int: 是否已验证 0-未验证 1-已验证
            @param register_ip str: 注册IP地址
            @param register_source int: 注册来源：1手机号 2邮箱 3GitHub 4qq 5微信 6腾讯微博 7新浪微博
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
            register_source and \
            isinstance(guid, (str, unicode)) and \
            len(guid) == 22 and \
            identity_type in (1, 2) and \
            verified in (1, 0) and \
            register_source in (1, 2, 3, 4, 5, 6, 7):
            ctime = get_current_timestamp()
            try:
                logger.debug("transaction, start")
                self.db._db.begin()
                try:
                    sql_1 = "INSERT INTO user_auth (uid, identity_type, identifier, certificate, verified, status, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    info = self.db.insert(sql_1, guid, identity_type, identifier, certificate, verified, 1, ctime)
                    logger.debug("sql_1 info: {}".format(info))
                except IntegrityError:
                    res.update(msg=u"账户已存在")
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg=u"系统异常")
                else:
                    sql_2 = "INSERT INTO user_profile (uid, register_source, register_ip, create_time, is_realname, is_admin) VALUES (%s, %s, %s, %s, %s, %s)"
                    info = self.db.insert(sql_2, guid, register_source, register_ip, ctime, 0, 0)
                    logger.debug("sql_2 info: {}".format(info))
                    logger.debug('transaction, commit')
                    self.db._db.commit()
            except Exception, e:
                logger.debug('transaction, rollback', exc_info=True)
                self.db._db.rollback()
            else:
                logger.debug("transaction, over")
                if self.__check_hasUser(guid):
                    res.update(msg=u"注册成功", success=True)
                else:
                    res.update(msg=u"注册失败")
        else:
            res.update(msg=u"校验失败")
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
            if password and repassword and password == repassword and 6 <= len(password) < 30:
                certificate = generate_password_hash(password)
                if vcode and len(vcode) == 6 and self.__check_sendEmailVcode(account, vcode, scene="signUp"):
                    # NO.3 检查账号是否存在
                    if self.__check_hasEmail(account):
                        res.update(msg=u"邮箱已存在")
                    else:
                        guid = gen_uniqueId()
                        upts = self.__signUp_transacion(guid=guid, identifier=account, identity_type=2, certificate=certificate, verified=1, register_ip=register_ip, register_source=2)
                        logger.debug(upts)
                        res.update(upts)
                else:
                    res.update(msg=u"无效的验证码")
            else:
                res.update(msg=u"无效的密码：两次密码不一致或长度不合格")
        elif phone_check(account):
            # 账号类型：手机
            res.update(msg=u"暂不支持手机号注册")
        else:
            # 账号类型：非法，拒绝
            res.update(msg=u"无效的账号")
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
                    res.update(msg=u"系统异常")
                else:
                    if data and isinstance(data, dict):
                        uid = data["uid"]
                        certificate = data["certificate"]
                        if check_password_hash(certificate, password):
                            res.update(success=True, uid=uid, identity_type=identity_type)
                        else:
                            res.update(msg=u"密码错误")
                    else:
                        res.update(msg=u"无效的账号：不存在或已禁用")
            else:
                res.update(msg=u"无效的密码：长度不合格")
        elif phone_check(account):
            # 账号类型：手机
            res.update(msg=u"暂不支持手机号登录")
        else:
            # 账号类型：非法，拒绝
            res.update(msg=u"无效的账号")
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
