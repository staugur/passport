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
from utils.tool import logger, md5, gen_token, Universal_pat, url_pat, get_current_timestamp
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

    def sso(self):
        pass

