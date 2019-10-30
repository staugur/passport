# -*- coding: utf-8 -*-
"""
    passport.hlm._usersso
    ~~~~~~~~~~~~~~

    SSO单点登录与注销

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from libs.base import ServiceBase
from utils.tool import logger, md5, gen_requestId, sso_request, gen_token, hmac_sha256, get_current_timestamp
from config import SYSTEM
from multiprocessing.dummy import Pool as ThreadPool


class UserSSOManager(ServiceBase):

    def __init__(self):
        super(UserSSOManager, self).__init__()

    def ssoCreateTicket(self, sid=None, agent=None, ip=None):
        """创建授权令牌写入redis
        说明：
            授权令牌：临时鉴别使用，有效期3min，写入令牌集合中。
        参数：
            sid str: 当None时表明未登录，此时ticket是首次产生；当真时，说明已登录，此时ticket非首次产生，其值需要设置为有效的sid
        """
        ticket = gen_requestId()
        init = dict(last=get_current_timestamp()) if sid else dict(ctime=get_current_timestamp(), agent=agent, ip=ip)
        sid = sid or md5(ticket)
        tkey = "passport:sso:ticket:{}".format(ticket)
        skey = "passport:sso:sid:{}".format(sid)
        try:
            pipe = self.redis.pipeline()
            pipe.set(tkey, sid)
            #tkey过期，ticket授权令牌过期，应当给个尽可能小的时间，并且ticket使用过后要删除(一次性有效)
            pipe.expire(tkey, 180)
            #skey初始化数据
            pipe.hmset(skey, init)
            #skey过期，即cookie过期，设置为jwt过期秒数，每次创建ticket都要更新过期时间
            pipe.expire(skey, SYSTEM["SESSION_EXPIRE"])
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
                    pipe = self.redis.pipeline()
                    pipe.hmset(skey, dict(uid=uid, sid=sid, source=source_app_name))
                    pipe.expire(skey, SYSTEM["SESSION_EXPIRE"])
                    pipe.execute()
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

    def ssoExistWithSid(self, sid):
        """查看sid的数据是否存在"""
        if sid and isinstance(sid, basestring):
            skey = "passport:sso:sid:{}".format(sid)
            return self.redis.exists(skey)
        return False

    def ssoGetWithSid(self, sid, getClients=False):
        """根据sid查询数据"""
        if sid and isinstance(sid, basestring):
            skey = "passport:sso:sid:{}".format(sid)
            data = self.redis.hgetall(skey)
            if getClients is True:
                data["clients"] = self.ssoGetRegisteredClient(sid)
            return data
        return False

    def ssoRegisterClient(self, sid, app_name):
        """ticket验证通过，向相应sid中注册app_name"""
        logger.debug("ssoRegisterClient for {}, with {}".format(sid, app_name))
        if sid and app_name:
            try:
                skey = "passport:sso:sid:{}:clients".format(sid)
                pipe = self.redis.pipeline()
                pipe.sadd(skey, app_name)
                pipe.expire(skey, SYSTEM["SESSION_EXPIRE"])
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

    def ssoGetRegisteredClient(self, sid):
        """根据sid查询已注册的应用"""
        if sid and isinstance(sid, basestring):
            skey = "passport:sso:sid:{}:clients".format(sid)
            return list(self.redis.smembers(skey))
        return []

    def ssoGetRegisteredUserSid(self, uid):
        """根据uid查询已注册的sid"""
        if uid:
            ukey = "passport:user:sid:{}".format(uid)
            return list(self.redis.smembers(ukey))
        return []

    def clearRegisteredClient(self, sid, name):
        """根据sid清除已注册的应用"""
        if sid and name and isinstance(sid, basestring):
            skey = "passport:sso:sid:{}:clients".format(sid)
            return True if int(self.redis.srem(skey, name)) == 1 else False
        return []

    def clearRegisteredUserSid(self, uid, sid):
        """清理用户sid相关数据"""
        if uid and sid:
            ukey = "passport:user:sid:{}".format(uid)
            skey = "passport:sso:sid:{}".format(sid)
            ckey = "passport:sso:sid:{}:clients".format(sid)
            pipe = self.redis.pipeline()
            pipe.srem(ukey, sid)
            pipe.delete(skey)
            pipe.delete(ckey)
            pipe.execute()

    def ssoSetUidConSyncToken(self, uid, token, expire):
        """设置uid同步到客户端的token标识，用以验证此次同步是否passport发起"""
        if uid and isinstance(uid, basestring) and isinstance(expire, int):
            tkey = "passport:user:syncToken:{}".format(uid)
            try:
                pipe = self.redis.pipeline()
                pipe.set(tkey, token)
                pipe.expire(tkey, expire)
                pipe.execute()
            except Exception,e:
                logger.error(e)
            else:
                return True
        return False

    def ssoGetUidCronSyncToken(self, uid):
        """查询uid同步到客户端的token"""
        if uid and isinstance(uid, basestring):
            tkey = "passport:user:syncToken:{}".format(uid)
            try:
                token = self.redis.get(tkey)
            except Exception,e:
                logger.error(e)
            else:
                return token

    def clientsConSync(self, getUserApp, uid, data):
        """ 向uid注册的各sid并发同步数据
        流程：
            1. 根据uid查找注册的sid，根据sid查到注册的clients，并去重
            2. 循环clients获取其sso信息组合，多线程并发回调其授权接口
            3. client时，根据token请求passport验证，通过后可以根据data中`CallbackType`处理不同类型数据
        参数：
            @param getUserApp func: userapp.UserAppManager.getUserApp
            @param uid str:用户标识
            @param data dict: 回调数据，格式如：dict(CallbackType="user_profile|user_avatar", CallbackData=dict|list|tuple|str)
                请求时json序列化传输，获取时使用json.loads(request.form.get("data")) -> 即data
        """
        # 检查参数
        if uid and data and isinstance(data, dict) and "CallbackType" in data and "CallbackData" in data:
            clients = []
            for sid in self.ssoGetRegisteredUserSid(uid):
                clients += self.ssoGetRegisteredClient(sid)
            clients = list(set(clients))
            logger.debug("callback: user all sid, get clients: {}".format(clients))
            if clients and isinstance(clients, list) and len(clients) > 0:
                # 生成验证token
                token = gen_token()
                # 向uid写入本次验证token
                self.ssoSetUidConSyncToken(uid, token, len(clients) * 10)
                # 更新传递给客户端的data参数
                data.update(uid=uid, token=token)
                kwargs = []
                for clientName in clients:
                    clientData = getUserApp(clientName)
                    if clientData and isinstance(clientData, dict):
                        kwargs.append(dict(url="{}/sso/authorized".format(clientData["app_redirect_url"].strip("/")), params=dict(Action="ssoConSync", signature=hmac_sha256("{}:{}:{}".format(clientData["name"], clientData["app_id"], clientData["app_secret"])).upper()), data=data, num_retries=0))
                logger.debug("callback: kwargs: {}".format(kwargs))
                if kwargs:
                    try:
                        pool = ThreadPool()
                        resp = pool.map_async(sso_request, kwargs)
                        resp.wait()
                        logger.debug("callback: return: %s" %resp.get())
                    except Exception,e:
                        logger.error(e, exc_info=True)
