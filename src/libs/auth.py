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


class LAuth(object):
    """ 本地登陆注册类 """

    def __init__(self, db):
        self.db = db
        self._auth_method = 'lauth'

    def __signUp_transacion(self, guid, identifier, identity_type, certificate, verified):
        ''' begin的方式使用事务注册账号，
        参数：
            @param identifier str: 手机号或邮箱号
            @param identity_type int: 账号类型，1-手机 2-邮箱
            @param certificate str: 密码
            @param verified int: 是否已验证 0-未验证 1-已验证
        需要：
            1. guid
            2. 类型：邮箱/手机号(需要验证)，以及密码
            3. 注册时ip、时间、方法
        流程：
            1、写入`user_auth`表
            2、写入`user_profile`表
        返回字典：
            success bool 表示注册是否成功；
            msg str 表示提示信息。
        '''
        res = dict(success=False, msg=None)
        # 校验
        checked = False
        if guid and identifier and identity_type and certificate and verified:
            if instance(guid, (str, unicode)) and \
                len(guid) == 22 and \
                identity_type in (1, 2) and \
                verified in (1, 0)
        try:
            self.db._db.begin()
            try:
                sql_1 = "INSERT INTO user_auth (uid, identity_type, identifier, certificate, method, verified, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                print "sql1", self.db.insert(sql_1, )
            except IntegrityError:
                res.update(msg=u"账户已存在")
            else:
                sql_2 = "INSERT INTO user_profile (uid, register_source, register_ip, status, create_time, is_realname, is_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                print "sql2", self.db.insert(sql_2)
                print '提交事务'
                db._db.commit()
        except Exception, e:
            print "回滚事务"
            db._db.rollback()
            print "error",str(e)
            return False
        return True

    def signUp(self, account, vcode, password, repassword):
        """注册接口，面向前端
        参数：
            @param account str: 注册的账号，邮箱/手机号
            @param vcode str: 使用手机或邮箱的验证码
            @param password str: 密码
            @param repassword str: 重复密码
        流程：
        """
        pass
        # chck username and password value
        if not username or not password or not email:
            res.update(msg="Invaild username or password or email")
            return res

        # check username and password length
        if 5 <= len(username) < 30 and 5 <= len(password) < 30:
            EncryptedPassword = generate_password_hash(password)
        else:
            res.update({'msg': 'username or password length requirement is greater than or equal to 5 less than 30'})
            return res

        # check username pattern
        if not user_pat.match(username):
            res.update({'msg': 'username is not valid'})
            return res

        if email and mail_pat.match(email) == None:
            res.update({'msg': "email format error"})
            return res