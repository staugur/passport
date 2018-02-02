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
from utils.tool import logger, get_current_timestamp, timestring_to_timestamp, domain_name_pat, avatar_check, sql_safestring_check
from torndb import IntegrityError
from config import SYSTEM


class UserProfileManager(ServiceBase):


    def __init__(self):
        super(UserProfileManager, self).__init__()
        self.cache_enable = True if SYSTEM["CACHE_ENABLE"]["UserProfile"] in ("true", "True", True) else False

    def getUserProfile(self, uid):
        """ 查询用户资料
        @param uid str: 用户id
        """
        res = dict(msg=None, code=1)
        key = "passport:user:profile:{}".format(uid)
        try:
            if self.cache_enable is False: raise
            data = json.loads(self.redis.get(key))
            logger.info("Hit getUserProfile Cache")
        except:
            sql = "SELECT uid,register_source,register_ip,nick_name,domain_name,gender,birthday,signature,avatar,location,ctime,mtime,is_realname FROM user_profile WHERE uid=%s"
            #sql2 = "SELECT uid,identity_type,identifier,certificate,verified,status,create_time,update_time,expire_time FROM user_auth"
            if uid and isinstance(uid, (str, unicode)) and len(uid) == 22:
                try:
                    data = self.mysql.get(sql, uid)
                except Exception,e:
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
        # 检测并组建sql
        sql = "UPDATE user_profile SET "
        checked = True
        invalid = []
        nick_name = profiles.get("nick_name")
        domain_name = profiles.get("domain_name")
        birthday = profiles.get("birthday")
        location = profiles.get("location")
        gender = profiles.get("gender")
        signature = profiles.get("signature")
        if nick_name and len(nick_name) <= 49:
            sql += "nick_name='%s'," %nick_name
        else:
            checked = False
            invalid.append("nick_name")
        if domain_name:
            if domain_name_pat.match(domain_name) and not domain_name.endswith('_') and not domain_name in ("admin", "system", "root", "administrator", "null", "none", "true", "false", "user"):
                sql += "domain_name='%s'," %domain_name
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
                sql += "birthday=%d," %birthday
        if location:
            sql += "location='%s'," %location
        if gender:
            try:
                gender = int(gender)
            except:
                checked = False
                invalid.append("gender")
            else:
                if gender in (0, 1, 2):
                    sql += "gender=%d," %gender
                else:
                    checked = False
                    invalid.append("gender")
        if signature:
            sql += "signature='%s'," %signature
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
            for key,value in profiles.iteritems():
                checked = sql_safestring_check(value)
                logger.debug("check {}, value: {}, result: {}".format(key, value, checked))
                if checked is False:
                    invalid.append(key)
                    break

        if uid and checked:
            sql += "mtime={}".format(get_current_timestamp())
            sql += " WHERE uid='%s'" %uid
            logger.debug("update profile for {}, sql is: {}".format(uid, sql))
            try:
                self.mysql.update(sql)
            except IntegrityError,e:
                logger.warn(e, exc_info=True)
                res.update(msg="Personal domain has been occupied", code=2)
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(code=0, refreshCache=self.refreshUserProfile(uid))
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
