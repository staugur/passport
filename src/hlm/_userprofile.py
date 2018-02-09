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
            sql = "SELECT id,identity_type,ctime,mtime,etime FROM user_auth WHERE identity_type in (3, 4, 5, 6, 7, 8, 9) AND status=1 AND uid=%s"
            try:
                data = self.mysql.query(sql, uid)
            except Exception, e:
                logger.error(e, exc_info=True)
            else:
                bind = [{"identity_type": oauth2_type2name(i["identity_type"]), "ctime": i["ctime"], "mtime": i["mtime"]} for i in data]
        return bind

    def __getUserSetLock(self, uid):
        """查询用户设置锁，比如个性域名、昵称"""
        if uid:
            return dict(
                nick_name=self.__hasUserSetLock(uid, "nick_name"),
                domain_name=self.__hasUserSetLock(uid, "domain_name"),
            )
        return dict()

    def __setUserSetLock(self, uid, nick_name=False, domain_name=False):
        """查询用户设置锁，比如个性域名、昵称
        @param nick_name bool: 昵称是否设置锁过期，24h内只可以修改一次
        @param domain_name bool: 个性域名是否设置锁过期，一旦设置不可修改
        """
        if uid:
            key = "passport:user:lock:{}".format(uid)
            pipe = self.redis.pipeline()
            if nick_name is True:
                # 设置昵称24小时后过期
                pipe.hset(key, "nick_name", timestamp_after_timestamp(hours=24))
            if domain_name is True:
                # 设置个性域名永久有效
                pipe.hset(key, "domain_name", 0)
            try:
                pipe.execute()
            except:
                return False
            else:
                return True

    def __hasUserSetLock(self, uid, item):
        """检查用户某项是否加锁
        参数：
            @param item str: 有效项：`nick_name`, `domain_name`
        规则：
            1. 10位UNIX时间戳，小于当前时间即锁失效，可以修改
            2. 结果为0表示永不过期即锁有效。不可以修改
        返回：
            True -> 加锁 -> 不可以修改
            False -> 未加锁 -> 可修改
        """
        if uid:
            key = "passport:user:lock:{}".format(uid)
            now = get_current_timestamp()
            etime = self.redis.hget(key, item)
            try:
                etime = int(etime)
            except:
                return False
            else:
                if etime != 0 and etime < now:
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
            sql = "SELECT register_source,register_ip,nick_name,domain_name,gender,birthday,signature,avatar,location,ctime,mtime,is_realname FROM user_profile WHERE uid=%s"
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
                    pipe.expire(key, 300)
                    pipe.execute()
            else:
                res.update(msg="There are invalid parameters", code=2)
        else:
            res.update(data=data, code=0)
        if res.get("data") and isinstance(res.get("data"), dict):
            # 更新设置锁数据
            res['data']['lock'] = self.__getUserSetLock(uid)
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
        # 检测并组建sql
        sql = "UPDATE user_profile SET "
        if nick_name and len(nick_name) <= 49:
            if self.__hasUserSetLock(uid, "nick_name") is False:
                sql += "nick_name='%s'," % nick_name
                can_lock_nick_name = True
        else:
            checked = False
            invalid.append("nick_name")
        if domain_name:
            if domain_name_pat.match(domain_name) and not domain_name.endswith('_') and not domain_name in ("admin", "system", "root", "administrator", "null", "none", "true", "false", "user"):
                if self.__hasUserSetLock(uid, "domain_name") is False:
                    sql += "domain_name='%s'," % domain_name
                    can_lock_domain_name = True
            else:
                checked = False
                invalid.append("domain_name")
        if birthday:
            try:
                birthday = timestring_to_timestamp(birthday, format="%Y-%m-%d")
            except:
                checked = False
                invalid.append("birthday")
            else:
                sql += "birthday=%d," % birthday
        if location:
            sql += "location='%s'," % location
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
        if signature:
            sql += "signature='%s'," % signature
        if not nick_name and \
                not domain_name and \
                not birthday and \
                not location and \
                not gender and \
                not signature:
            checked = False
            invalid.append("all")
        if checked:
            # 拼接sql的安全检测
            for key, value in profiles.iteritems():
                checked = sql_safestring_check(value)
                logger.debug("check {}, value: {}, result: {}".format(key, value, checked))
                if checked is False:
                    invalid.append(key)
                    break

        if uid and checked:
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
                lock = self.__setUserSetLock(uid=uid, nick_name=can_lock_nick_name, domain_name=can_lock_domain_name)
                res.update(locked=lock)
        else:
            res.update(msg="There are invalid parameters", code=4, invalid=invalid)
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
