# -*- coding: utf-8 -*-
"""
    passport.hlm._userapp
    ~~~~~~~~~~~~~~

    SSO Client 应用管理

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import json
from libs.base import ServiceBase
from utils.tool import logger, md5, gen_token, gen_requestId, Universal_pat, url_pat, get_current_timestamp
from torndb import IntegrityError
from config import SYSTEM


class UserAppManager(ServiceBase):

    def __init__(self):
        super(UserAppManager, self).__init__()
        self.cache_enable = True if SYSTEM["CACHE_ENABLE"]["UserApps"] in ("true", "True", True) else False

    def getUserApp(self, name):
        """ 通过app_name获取应用信息 """
        if name:
            res = self.listUserApp()
            if res["code"] == 0:
                try:
                    data = ( i for i in res['data'] if i['name'] == name ).next()
                except StopIteration:
                    pass
                else:
                    return data

    def listUserApp(self):
        """ 查询userapp应用列表 """
        res = dict(msg=None, code=1)
        key = "passport:user:apps"
        try:
            if self.cache_enable is False:
                raise
            data = json.loads(self.redis.get(key))
            if data:
                logger.info("Hit listUserApps Cache")
            else:
                raise
        except:
            sql = "SELECT id,name,description,app_id,app_secret,app_redirect_url,ctime,mtime FROM sso_apps"
            try:
                data = self.mysql.query(sql)
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal")
            else:
                res.update(data=data, code=0)
                pipe = self.redis.pipeline()
                pipe.set(key, json.dumps(data))
                pipe.expire(key, 600)
                pipe.execute()
        else:
            res.update(data=data, code=0)
        return res

    def refreshUserApp(self):
        """ 刷新userapp应用列表缓存 """
        key = "passport:user:apps"
        return True if self.cache_enable and self.redis.delete(key) == 1 else False

    def createUserApp(self, name, description, app_redirect_url):
        """新建userapp应用
        @param name str: 应用名
        @param description str: 应用描述
        @param app_redirect_url str: 回调url
        """
        res = dict(msg=None, code=1)
        if name and description and app_redirect_url and Universal_pat.match(name) and url_pat.match(app_redirect_url):
            app_id = md5(name)
            app_secret = gen_token(36)
            ctime = get_current_timestamp()
            sql = "INSERT INTO sso_apps (name, description, app_id, app_secret, app_redirect_url, ctime) VALUES (%s, %s, %s, %s, %s, %s)"
            try:
                self.mysql.insert(sql, name, description, app_id, app_secret, app_redirect_url, ctime)
            except IntegrityError:
                res.update(msg="Name already exists", code=2)
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(code=0, refreshCache=self.refreshUserApp())
        else:
            res.update(msg="There are invalid parameters", code=4)
        return res

    def updateUserApp(self, name, description, app_redirect_url):
        """更新userapp应用
        @param name str: 应用名
        @param description str: 应用描述
        @param app_redirect_url str: 回调url
        """
        res = dict(msg=None, code=1)
        if name and description and app_redirect_url and Universal_pat.match(name) and url_pat.match(app_redirect_url):
            mtime = get_current_timestamp()
            sql = "UPDATE sso_apps SET description=%s, app_redirect_url=%s, mtime=%s WHERE name=%s"
            try:
                self.mysql.update(sql, description, app_redirect_url, mtime, name)
            except IntegrityError:
                res.update(msg="Name already exists", code=2)
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(code=0, refreshCache=self.refreshUserApp())
        else:
            res.update(msg="There are invalid parameters", code=4)
        return res

    def deleteUserApp(self, name):
        """删除userapp应用
        @param name str: 应用名
        """
        res = dict(msg=None, code=1)
        if name:
            sql = "DELETE FROM sso_apps WHERE name=%s"
            try:
                self.mysql.execute(sql, name)
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(code=0, refreshCache=self.refreshUserApp())
        else:
            res.update(msg="There are invalid parameters", code=4)
        return res

    def ssoCreateTicket(self, sid=None):
        """创建授权令牌写入redis
        说明：
            授权令牌：临时鉴别使用，有效期3min，写入令牌集合中。
        参数：
            sid str: 当None时表明未登录，此时ticket是首次产生；当真时，说明已登录，此时ticket非首次产生，其值需要设置为有效的sid
        """
        ticket = gen_requestId()
        sid = sid or md5(ticket)
        tkey = "passport:sso:ticket:{}".format(ticket)
        skey = "passport:sso:sid:{}".format(sid)
        pipe = self.redis.pipeline()
        pipe.set(tkey, sid)
        #tkey过期，ticket授权令牌过期，应当给个尽可能小的时间，并且ticket使用过后要删除(一次性有效)
        pipe.expire(tkey, 180)
        #skey过期，即cookie过期，设置为jwt过期秒数，以后看情况设置为7d；每次创建ticket都要更新过期时间
        pipe.expire(skey, 43200)
        try:
            pipe.execute()
        except Exception,e:
            logger.error(e, exc_info=True)
        else:
            return (ticket, sid)

    def ssoCreateSid(self, ticket, uid, source_app_name):
        """创建sid并写入redis
        说明：
            sid：可以理解为user-agent，sso server cookie(jwt payload)中携带
        参数：
            ticket str: 授权令牌
            uid str: 用户唯一id
            source_app_name str: sso应用名，本次sid对应的首个应用
        """
        if ticket and isinstance(ticket, basestring) and uid and source_app_name:
            tkey = "passport:sso:ticket:{}".format(ticket)
            sid = self.redis.get(tkey)
            if sid:
                skey = "passport:sso:sid:{}".format(sid)
                try:
                    self.redis.hmset(skey, dict(uid=uid, sid=sid, source=source_app_name))
                except Exception,e:
                    logger.error(e, exc_info=True)
                else:
                    return True
        return False

    def ssoGetWithTicket(self, ticket):
        """根据ticket查询对应sid数据"""
        if ticket and isinstance(ticket, basestring):
            tkey = "passport:sso:ticket:{}".format(ticket)
            sid = self.redis.get(tkey)
            if sid:
                skey = "passport:sso:sid:{}".format(sid)
                try:
                    data = self.redis.hgetall(skey)
                except Exception,e:
                    logger.error(e, exc_info=True)
                else:
                    if data and isinstance(data, dict):
                        self.redis.delete(tkey)
                        return data
        return False

    def ssoGetWithSid(self, sid):
        """根据sid查询数据"""
        if sid and isinstance(sid, basestring):
            skey = "passport:sso:sid:{}".format(sid)
            return self.redis.hgetall(skey)
        return False

    def ssoRegisterClient(self, sid, app_name):
        """ticket验证通过，向相应sid中注册app_name系统地址"""
        logger.debug("ssoRegisterClient for {}, with {}".format(sid, app_name))
        if sid and app_name:
            try:
                skey = "passport:sso:sid:{}:clients".format(sid)
                pipe = self.redis.pipeline()
                pipe.sadd(skey, app_name)
                pipe.expire(skey, 43200)
                pipe.execute()
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                return True
        return False

    def ssoRegisterUserSid(self, uid, sid):
        """记录uid已登录的sso应用的sid"""
        logger.debug("ssoRegisterUserSid for uid: {}, with sid: {}".format(uid, sid))
        if uid and sid:
            try:
                ukey = "passport:user:sid:{}".format(uid)
                self.redis.sadd(ukey, sid)
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                return True
        return False