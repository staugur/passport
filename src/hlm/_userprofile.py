# -*- coding: utf-8 -*-
"""
    passport.hlm._userprofile
    ~~~~~~~~~~~~~~

    用户基本资料管理

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import json
from libs.base import ServiceBase
from utils.tool import logger, get_current_timestamp, timestring_to_timestamp, timestamp_after_timestamp, domain_name_pat, avatar_check, sql_safestring_check
from utils.web import oauth2_type2name
from torndb import IntegrityError
from config import SYSTEM
from werkzeug.security import generate_password_hash, check_password_hash


class UserProfileManager(ServiceBase):

    def __init__(self):
        super(UserProfileManager, self).__init__()
        self.cache_enable = True if SYSTEM["CACHE_ENABLE"]["UserProfile"] in ("true", "True", True) else False

    def listUserBind(self, uid):
        """ 查询用户绑定的社交账号 
        @param uid str: 用户唯一id
        """
        bind = []
        if uid:
            #sql = "SELECT id,identity_type,ctime,mtime,etime FROM user_auth WHERE identity_type in (1, 2, 3, 4, 5, 6, 7, 8, 9) AND status=1 AND uid=%s"
            sql = "SELECT id,identity_type,identifier,ctime,mtime,etime FROM user_auth WHERE status=1 AND uid=%s"
            try:
                data = self.mysql.query(sql, uid)
            except Exception, e:
                logger.error(e, exc_info=True)
            else:
                # 定义map解析函数
                def parse(i):
                    if i["identity_type"] == 1:
                        # identifier = "{}****{}".format(i["identifier"][0:3], i["identifier"][7:])
                        identifier = i["identifier"]
                    elif i["identity_type"] == 2:
                        # identifier = "{}****{}@{}".format(i["identifier"].split('@')[0][0:3], i["identifier"].split('@')[0][7:], i["identifier"].split('@')[-1])
                        identifier = i["identifier"]
                    else:
                        identifier = ""
                    return {"identity_type": oauth2_type2name(i["identity_type"]), "ctime": i["ctime"], "mtime": i["mtime"], "auth_type": "lauth" if i["identity_type"] in (1, 2) else "oauth", "identifier": identifier}
                bind = map(parse, data)
                #
        return bind

    def __checkUsersetLock(self, etime):
        """检查用户某项是否加锁
        参数：
            @param etime str: 有效期，见"规则"
        规则：
            1. 10位UNIX时间戳，小于当前时间即锁失效，可以修改
            2. 结果为0表示加锁，不可以修改；结果为1表示无锁
        返回：
            True -> 加锁 -> 不可以修改（默认）
            False -> 无锁 -> 可修改
        """
        logger.debug(etime)
        logger.debug(type(etime))
        if etime and isinstance(etime, int):
            if abs(etime) == 1:
                return False
            elif etime == 0:
                return True
            else:
                if 1 < etime < get_current_timestamp():
                    return False
        return True

    def getUserProfile(self, uid, getBind=False):
        """ 查询用户资料
        @param uid str: 用户id
        """
        res = dict(msg=None, code=1)
        key = "passport:user:profile:{}".format(uid)
        try:
            if self.cache_enable is False:
                raise
            data = json.loads(self.redis.get(key))
            if data:
                logger.info("Hit getUserProfile Cache")
            else:
                raise
        except:
            sql = "SELECT register_source,register_ip,nick_name,domain_name,gender,birthday,signature,avatar,location,ctime,mtime,is_realname,is_admin,lock_nick_name,lock_domain_name FROM user_profile WHERE uid=%s"
            if uid and isinstance(uid, (str, unicode)) and len(uid) == 22:
                try:
                    data = self.mysql.get(sql, uid)
                except Exception, e:
                    logger.error(e, exc_info=True)
                    res.update(msg="System is abnormal")
                else:
                    res.update(data=data, code=0)
                    pipe = self.redis.pipeline()
                    pipe.set(key, json.dumps(data))
                    pipe.expire(key, 3600)
                    pipe.execute()
            else:
                res.update(msg="There are invalid parameters", code=2)
        else:
            res.update(data=data, code=0)
        if res.get("data") and isinstance(res.get("data"), dict):
            # 更新设置锁数据
            res['data']['lock'] = dict(
                nick_name = self.__checkUsersetLock(int(res["data"].get("lock_nick_name", -1))),
                domain_name = self.__checkUsersetLock(int(res["data"].get("lock_domain_name", -1))),
            )
            # 是否获取绑定账号数据
            if getBind is True:
                res['data']['bind'] = self.listUserBind(uid)
        return res

    def refreshUserProfile(self, uid):
        """ 刷新用户资料缓存 """
        key = "passport:user:profile:{}".format(uid)
        return True if self.cache_enable and self.redis.delete(key) == 1 else False

    def updateUserProfile(self, uid, **profiles):
        """更新用户基本资料
        @param uid str: 用户id
        @param profiles dict: 资料列表
        """
        #: TODO 决不能拼接SQL，先获取当前资料，用提交更新的部分资料覆盖
        res = dict(msg=None, code=1)
        logger.debug(profiles)
        nick_name = profiles.get("nick_name")
        domain_name = profiles.get("domain_name")
        birthday = profiles.get("birthday")
        location = profiles.get("location")
        gender = profiles.get("gender")
        signature = profiles.get("signature")
        # 定义
        checked = True
        invalid = []
        can_lock_nick_name = False
        can_lock_domain_name = False
        # 防止sql注入的安全检测
        for key, value in profiles.iteritems():
            checked = sql_safestring_check(value)
            logger.debug("check {}, value: {}, result: {}".format(key, value, checked))
            if checked is False:
                invalid.append(key)
                break
        # 至少有一项资料修改才通过检测
        if checked:
            if not nick_name and \
                not domain_name and \
                not birthday and \
                not location and \
                not gender and \
                not signature:
                checked = False
                invalid.append("all")
        if checked and uid and isinstance(uid, basestring) and len(uid) == 22:
            # 获取用户资料对比nick_name、domain_name是否修改过
            user_old_data = self.getUserProfile(uid)
            if user_old_data["code"] == 0:
                # 开始检测并组建sql
                sql = "UPDATE user_profile SET "
                # 用户旧数据
                user_old_data = user_old_data["data"]
                # 昵称
                if nick_name:
                    if len(nick_name) <= 49:
                        # nick_name可修改时拼接上sql
                        if user_old_data["lock"]["nick_name"] is False:
                            sql += "nick_name='%s'," % nick_name
                            if nick_name != user_old_data["nick_name"]:
                                # 判断昵称更改，加锁，设置其24小时后过期
                                can_lock_nick_name = True
                                sql += "lock_nick_name={},".format(timestamp_after_timestamp(hours=24))
                    else:
                        checked = False
                        invalid.append("nick_name")
                # 个性域名
                if domain_name:
                    if domain_name_pat.match(domain_name) and not domain_name.endswith('_') and not domain_name in ("admin", "system", "root", "administrator", "null", "none", "true", "false", "user"):
                        # domain_name可修改时拼接上sql
                        if user_old_data["lock"]["domain_name"] is False:
                            sql += "domain_name='%s'," % domain_name
                            if domain_name != user_old_data["domain_name"]:
                                # 判断域名更改，加锁，设置其永久有效
                                can_lock_domain_name = True
                                sql += "lock_domain_name=0,"
                    else:
                        checked = False
                        invalid.append("domain_name")
                # 生日
                if birthday:
                    try:
                        birthday = timestring_to_timestamp(birthday, format="%Y-%m-%d")
                    except:
                        checked = False
                        invalid.append("birthday")
                    else:
                        sql += "birthday=%d," % birthday
                # 性别
                if gender:
                    try:
                        gender = int(gender)
                    except:
                        checked = False
                        invalid.append("gender")
                    else:
                        if gender in (0, 1, 2):
                            sql += "gender=%d," % gender
                        else:
                            checked = False
                            invalid.append("gender")
                # 签名
                if signature:
                    sql += "signature='%s'," % signature
                # 城市
                if location:
                    sql += "location='%s'," % location
                # 更新sql
                if checked:
                    # 资料更新，设置mtime
                    sql += "mtime={}".format(get_current_timestamp())
                    sql += " WHERE uid='%s'" % uid
                    logger.debug("update profile for {}, sql is: {}".format(uid, sql))
                    try:
                        self.mysql.update(sql)
                    except IntegrityError, e:
                        logger.warn(e, exc_info=True)
                        res.update(msg="Personal domain has been occupied", code=2)
                    except Exception, e:
                        logger.error(e, exc_info=True)
                        res.update(msg="System is abnormal", code=3)
                    else:
                        res.update(code=0, refreshCache=self.refreshUserProfile(uid))
                        # 更新成功后设置锁
                        res.update(lock=dict(nick_name=can_lock_nick_name, domain_name=can_lock_domain_name))
                else:
                    res.update(msg="There are invalid parameters", code=5)
            else:
                res.update(msg="System is abnormal", code=1)
        else:
            res.update(msg="There are invalid parameters", code=4)
        if res["code"] != 0:
            res.update(invalid=invalid)
        return res

    def updateUserAvatar(self, uid, avatarUrl):
        """修改头像
        @param uid str: 用户id
        @param avatarUrl str: 头像地址
        """
        res = dict(msg=None, code=1)
        if uid and avatarUrl and sql_safestring_check(avatarUrl):
            if avatar_check(avatarUrl):
                sql = "UPDATE user_profile SET avatar=%s WHERE uid=%s"
                try:
                    self.mysql.update(sql, avatarUrl, uid)
                except Exception, e:
                    logger.error(e, exc_info=True)
                    res.update(msg="System is abnormal", code=2)
                else:
                    res.update(code=0, refreshCache=self.refreshUserProfile(uid))
            else:
                res.update(msg="Image address is not valid", code=3)
        else:
            res.update(msg="There are invalid parameters", code=4)
        return res

    def updateUserRealname(self, uid):
        """设置用户为实名"""
        res = dict(msg=None, code=1)
        if uid:
            sql = "UPDATE user_profile SET is_realname=1 WHERE uid=%s"
            try:
                self.mysql.update(sql, uid)
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal")
            else:
                res.update(code=0, refreshCache=self.refreshUserProfile(uid))
        else:
            res.update(msg="There are invalid parameters", code=4)
        return res

    def __check_modifyPass(self, uid):
        """检查是否可以修改密码，即是否存在邮箱或手机号"""
        if uid:
            sql = "SELECT count(uid) FROM user_auth WHERE identity_type IN (1,2) AND uid=%s"
            try:
                data = self.mysql.get(sql, uid)
            except Exception, e:
                logger.warn(e, exc_info=True)
            else:
                if data and isinstance(data, dict):
                    return int(data.get("count(uid)") or 0) > 0
        return False

    def __checkUserPassword(self, uid, password):
        """校验用户密码
        @param password str: 要校验的密码
        """
        if uid and len(uid) == 22 and password and 6 <= len(password) <= 30:
            sql = "SELECT certificate FROM user_auth WHERE identity_type IN (1,2) AND uid=%s"
            try:
                data = self.mysql.query(sql, uid)
            except Exception, e:
                logger.error(e, exc_info=True)
            else:
                if data and isinstance(data, (list, tuple)):
                    certificate = data[0]["certificate"]
                    return check_password_hash(certificate, password)
        return False

    def updateUserPassword(self, uid, nowpass, newpass, repass):
        """修改密码
        @param uid str: 用户id
        @param nowpass str: 当前密码
        @param newpass str: 新密码
        @param repass str: 确认新密码
        """
        res = dict(msg=None, code=1)
        if uid and nowpass and 6 <= len(nowpass) <= 30 and newpass and newpass == repass and 6 <= len(newpass) <= 30:
            if nowpass == newpass:
                res.update(msg="The new password request is inconsistent with the current password", code=5)
            else:
                if self.__check_modifyPass(uid):
                    if self.__checkUserPassword(uid, nowpass):
                        try:
                            sql = "UPDATE user_auth SET certificate=%s WHERE identity_type IN (1,2) AND uid = %s"
                            self.mysql.update(sql, generate_password_hash(newpass), uid)
                        except Exception, e:
                            logger.error(e, exc_info=True)
                            res.update(msg="System is abnormal", code=2)
                        else:
                            res.update(code=0)
                    else:
                        res.update(msg="The current password is wrong", code=3)
                else:
                    res.update(msg="Please bind the email or phone first", code=6)
        else:
            res.update(msg="There are invalid parameters", code=4)
        return res

    def listUserLoginHistory(self, uid, page=1, limit=5, sort="desc"):
        """ 查询用户登录历史 
        @param uid str: 用户唯一id
        分页参数：
        @param page int: 请求页数，从1开始
        @param limit int: 每页数据量
        @param sort str: 排序，可选值asc正序、desc倒序
        """
        res = dict(code=1, msg=None)
        # 检查参数
        try:
            page = int(page)
            limit = int(limit)
            sort = sort.upper()
            if not uid or page < 1 or limit < 1 or not sort in ("ASC", "DESC"):
                raise
        except:
            res.update(code=2, msg="There are invalid parameters")
        else:
            # mysql处分页
            # select * from xxx where xxx order by xx sort limit offset(page不为0时=(page-1)*limit),rows(limit);
            sql1 = "SELECT id,uid,login_type,login_ip,login_area,login_time,user_agent,browser_type,browser_device,browser_os,browser_family FROM user_loginlog WHERE uid=%s ORDER BY id {} LIMIT {},{}".format(sort, (page-1)*limit, limit)
            sql2 = "SELECT count(id) FROM user_loginlog WHERE uid=%s"
            try:
                data1 = self.mysql.query(sql1, uid)
                data2 = self.mysql.get(sql2, uid)
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(data=data1, code=0, count=data2.get("count(id)"))
        return res

