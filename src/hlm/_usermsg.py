# -*- coding: utf-8 -*-
"""
    passport.hlm._usermsg
    ~~~~~~~~~~~~~~

    用户消息管理

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import json, bleach
from utils.tool import logger, gen_token, get_current_timestamp
from libs.base import ServiceBase


class UserMsgManager(ServiceBase):
    """ 用户消息管理：按照用户及消息类型的规则
    消息类型：
        -- 系统消息 -> system
        -- 产品消息 -> product
    状态类型：
        -- 1 -> 未读消息
        -- 0 -> 已读消息
    消息规则：
        -- 内容
            msgId=xxx, msgContent=xxx, msgTime=时间戳, msgType=消息类型, msgStatus=0|1
        -- 存储
           格式 -> 按用户 -> passport:user:messages:uid；具体消息条目 -> passport:user:message:msgId
           类型 -> zset（有序集合，按时间戳为分数）
    未读消息示例（uid=demo）：
        msgId, msgTime = xx, xx
        zadd("passport:user:messages:demo", msgId, msgTime)
        hmset("passport:user:message:msgId", 内容)
    """

    def __init__(self):
        super(UserMsgManager, self).__init__()
        # 生成用户消息键
        self.gen_usermsgKey = lambda uid: "passport:user:messages:{}".format(uid)
        # 生成消息内容键
        self.gen_usermsgIdKey = lambda msgId: "passport:user:message:{}".format(msgId)
        # 允许解析的HTML标签-标签白名单
        self.ALLOWED_TAGS = [u'a', u'abbr', u'acronym', u'b', u'code', u'em', u'i', u'strong', u'img']
        # 允许解析的HTML标签属性-属性白名单
        self.ALLOWED_ATTRIBUTES = {u'a': [u'href', u'title'], u'acronym': [u'title'], u'abbr': [u'title'], u'img': [u'title', u'alt', u'src', u'width', u'height'], u'*': [u'style']}
        # 允许解析的HTML标签内联样式-CSS白名单
        self.ALLOWED_STYLES = ['color']
        # 允许的消息类型
        self.ALLOWED_MSGTYPE = ("system", "product")

    def count_message(self, uid, msgStatus=2):
        """统计消息
        @param uid str: 用户id
        @param msgStatus int: 消息状态 1-未读 0-已读, 默认2代表统计所有状态消息
        """
        res = dict(msg=None, code=1)
        if uid:
            try:
                msgStatus = int(msgStatus)
            except (TypeError,ValueError):
                res.update(msg="There are invalid parameters", code=2)
            else:
                try:
                    if msgStatus in (0, 1):
                        msgIds = self.redis.zrange(self.gen_usermsgKey(uid), 0, -1)
                        if msgIds:
                            pipe = self.redis.pipeline()
                            for msgId in msgIds:
                                pipe.hget(self.gen_usermsgIdKey(msgId), "msgStatus")
                            data = pipe.execute()
                            count = sum(map(lambda _status: 1 if int(_status) == msgStatus else 0, data))
                        else:
                            count = 0
                    else:
                        count = self.redis.zcard(self.gen_usermsgKey(uid))
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg="System is abnormal", code=3)
                else:
                    res.update(code=0, count=count)
        else:
            res.update(msg="There are invalid parameters", code=4)
        return res

    def push_message(self, uid, msgContent, msgType="system"):
        """ 推送一条站内消息
        @param msgContent str: 消息内容，允许部分html标签，参见`ALLOWED_TAGS`
        @param msgType str: 消息类型
        """
        res = dict(code=1, msg=None)
        if uid and msgContent and msgType and isinstance(msgContent, (unicode, str)) and msgType in self.ALLOWED_MSGTYPE:
            msgId = gen_token().lower()
            msgTime = get_current_timestamp()
            msgContent = bleach.clean(msgContent, tags=self.ALLOWED_TAGS, attributes=self.ALLOWED_ATTRIBUTES, styles=self.ALLOWED_STYLES)
            try:
                pipe = self.redis.pipeline()
                pipe.zadd(self.gen_usermsgKey(uid), msgId, msgTime)
                pipe.hmset(self.gen_usermsgIdKey(msgId), dict(msgId=msgId, msgContent=msgContent, msgTime=msgTime, msgType=msgType, msgStatus=1))
                pipe.execute()
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=2)
            else:
                res.update(code=0)
        else:
            res.update(msg="There are invalid parameters", code=3)
        return res

    def pull_message(self, uid, msgStatus=2, msgType=None, desc=True):
        """ 拉取站内消息(私信)
        @param msgStatus int: 消息状态 1-未读 0-已读, 默认2代表统计所有状态消息
        @param msgType str: 消息类型，默认None代表所有类型
        @param desc bool: 是否倒序
        """
        res = dict(msg=None, code=1)
        if uid:
            try:
                msgStatus = int(msgStatus)
            except (TypeError,ValueError):
                res.update(msg="There are invalid parameters", code=2)
            else:
                try:
                    msgIds = self.redis.zrange(self.gen_usermsgKey(uid), 0, -1, desc=desc)
                    if msgIds:
                        pipe = self.redis.pipeline()
                        for msgId in msgIds:
                            pipe.hgetall(self.gen_usermsgIdKey(msgId))
                        data = pipe.execute()
                    else:
                        data = []
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg="System is abnormal", code=4)
                else:
                    if isinstance(data, (list, tuple)):
                        if msgStatus in (0, 1):
                            data = [ _ for _ in data if int(_['msgStatus']) == msgStatus ]
                        if msgType in self.ALLOWED_MSGTYPE:
                            data = [ _ for _ in data if _['msgType'] == msgType ]
                        def convertion(md):
                            md['msgStatus'] = int(md['msgStatus'])
                            md['msgTime'] = int(md['msgTime'])
                            return md
                        res.update(code=0, data=map(convertion, data))
        else:
            res.update(msg="There are invalid parameters", code=6)
        return res

    def markstatus_message(self, uid, msgId):
        """ [反向]标记消息状态，如果当前状态是1则标记为0，反之亦然。
        @param msgId str: 消息唯一id
        """
        res = dict(code=1, msg=None)
        if uid and msgId:
            try:
                msgStatus = self.redis.hget(self.gen_usermsgIdKey(msgId), 'msgStatus')
                if msgStatus in (0, 1, '0', '1'):
                    status = 0 if msgStatus in (1, '1') else 1
                    self.redis.hset(self.gen_usermsgIdKey(msgId), "msgStatus", status)
                else:
                    res.update(msg="No such message", code=5)
            except (TypeError,ValueError):
                res.update(msg="There are invalid parameters", code=2)
            except Exception:
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(code=0)
        else:
            res.update(msg="There are invalid parameters", code=4)
        return res

    def delete_message(self, uid, msgId):
        """ 删除站内消息
        @param msgId str: 消息唯一id
        """
        res = dict(code=1, msg=None)
        if uid and msgId:
            try:
                pipe = self.redis.pipeline()
                pipe.zrem(self.gen_usermsgKey(uid), msgId)
                pipe.delete(self.gen_usermsgIdKey(msgId))
                pipe.execute()
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=2)
            else:
                res.update(code=0)
        else:
            res.update(msg="There are invalid parameters", code=3)
        return res

    def clear_message(self, uid):
        """ 清空站内消息 """
        res = dict(code=1, msg=None)
        if uid:
            try:
                ukey = self.gen_usermsgKey(uid)
                msgIds = self.redis.zrange(ukey, 0, -1)
                pipe = self.redis.pipeline()
                if msgIds:
                    for msgId in msgIds:
                        pipe.delete(self.gen_usermsgIdKey(msgId))
                pipe.delete(ukey)
                pipe.execute()
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=2)
            else:
                res.update(code=0)
        else:
            res.update(msg="There are invalid parameters", code=3)
        return res
