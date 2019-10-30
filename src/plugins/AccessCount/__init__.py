# -*- coding: utf-8 -*-
"""
    Passport.plugins.AccessCount
    ~~~~~~~~~~~~~~

    PV and IP plugins for statistical access.

    :copyright: (c) 2018 by taochengwei.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import
from utils.tool import plugin_logger, get_current_timestamp
from libs.base import PluginBase
from config import PLUGINS
from flask import request, g
import datetime, time, json

__plugin_name__ = "AccessCount"
__description__ = "IP、PV、UV统计插件"
__author__ = "staugur"
__version__ = "0.1.0"
__license__ = "MIT"
if PLUGINS["AccessCount"] in ("true", "True", True):
    __state__ = "enabled"
else:
    __state__ = "disabled"


def getPluginClass():
    return AccessCount


class AccessCount(PluginBase):
    """ 记录与统计每天访问数据 """

    @property
    def get_today(self):
        """ 获取现在时间可见串 """
        return datetime.datetime.now().strftime("%Y%m%d")

    def Record_ip_pv(self, *args, **kwargs):
        """ 记录ip、ip、uv """
        resp = kwargs.get("response") or args[0]
        data = {
            "status_code": resp.status_code,
            "method": request.method,
            "ip": g.ip,
            "url": request.url,
            "referer": request.headers.get('Referer'),
            "agent": request.headers.get("User-Agent"),
            "TimeInterval": "%0.2fs" %float(time.time() - g.startTime),
            "clickTime": get_current_timestamp()
        }
        pvKey = "passport:AccessCount:pv"
        uvKey = "passport:AccessCount:uv"
        clickKey = "passport:AccessCount:clicklog"
        pipe = self.redis.pipeline()
        pipe.hincrby(pvKey, self.get_today, 1)
        pipe.hincrby(uvKey, request.base_url, 1)
        #pipe.rpush(clickKey, json.dumps(data))
        try:
            pipe.execute()
        except:
            pass

    def register_hep(self):
        return {"after_request_hook": self.Record_ip_pv}

def register():
    return dict(
        hep=dict(after_request=AccessCount().Record_ip_pv)
    )
