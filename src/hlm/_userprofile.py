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
from utils.tool import logger, get_current_timestamp
from torndb import IntegrityError


class UserProfileManager(ServiceBase):


    def __init__(self):
        super(UserProfileManager, self).__init__()

    def getUserProfile(self, uid):
        """ 查询用户资料
        @param uid str: 用户id
        """
        res = dict(msg=None, code=1)
        key = "passport:user:profile:{}".format(uid)
        try:
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
        return True if self.redis.delete(key) == 1 else False

    def updateUserProfile(self, uid, **profiles):
        """更新userapp应用
        @param uid str: 用户id
        """
        res = dict(msg=None, code=1)
        return res
