# -*- coding: utf-8 -*-
"""
    passport.libs.auth
    ~~~~~~~~~~~~~~

    登陆注册认证

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

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
            sql = "SELECT uid FROM user_auth WHERE uid=%s"
            try:
                data = self.db.get(sql, uid)
            except Exception,e:
                logger.warn(e, exc_info=True)
            else:
                logger.debug(data)
                if data and isinstance(data, dict):
                    return "uid" in data
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
        """校验邮箱验证码
        @param email str: 邮箱账号
        @param vcode str: 验证码
        @param scene int: 校验场景 signUp-注册 signIn-登录 forgot-忘记密码
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
                    sql_1 = "INSERT INTO user_auth (uid, identity_type, identifier, certificate, verified, create_time) VALUES (%s, %s, %s, %s, %s, %s)"
                    info = self.db.insert(sql_1, guid, identity_type, identifier, certificate, verified, ctime)
                    logger.debug("sql_1 info: {}".format(info))
                except IntegrityError:
                    res.update(msg=u"账户已存在")
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg=u"系统异常")
                else:
                    sql_2 = "INSERT INTO user_profile (uid, register_source, register_ip, status, create_time, is_realname, is_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    info = self.db.insert(sql_2, guid, register_source, register_ip, 1, ctime, 0, 0)
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

    def signIn(self, account, passport):
        """登录认证
        @param account str, 邮箱、手机
        @
        """
        pass