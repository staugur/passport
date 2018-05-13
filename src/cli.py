#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
    passport.cli
    ~~~~~~~~~~~~~~

    Cli Entrance

    Docstring conventions:
    http://flask.pocoo.org/docs/0.10/styleguide/#docstrings

    Comments:
    http://flask.pocoo.org/docs/0.10/styleguide/#comments

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import json
from utils.tool import cli_logger, create_redis_engine, create_mysql_engine, getIpArea, parse_userAgent

redis = create_redis_engine()
mysql = create_mysql_engine()


def execute_refresh_loginlog(times=30):
    """从redis读取登录记录刷入mysql"""
    key = "passport:loginlog"
    while times > 0:
        data = redis.lpop(key)
        try:
            data = json.loads(data)
        except:
            cli_logger.info("no loginlog")
            break
        else:
            browserType, browserDevice, browserOs, browserFamily = parse_userAgent(data["user_agent"])
            login_area = getIpArea(data["login_ip"])
            sql = "INSERT INTO user_loginlog (uid, login_type, login_ip, login_area, login_time, user_agent, browser_type, browser_device, browser_os, browser_family) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            try:
                mysql.insert(sql, data["uid"], data["identity_type"], data["login_ip"], login_area, data["login_time"], data["user_agent"], browserType, browserDevice, browserOs, browserFamily)
            except Exception, e:
                cli_logger.warn(e, exc_info=True)
            else:
                cli_logger.info("refresh_loginlog is ok")
        times -= 1


def execute_refresh_clicklog(times=30):
    """从redis读取访问记录刷入mysql"""
    key = "passport:AccessCount:clicklog"
    while times > 0:
        data = redis.lpop(key)
        try:
            data = json.loads(data)
        except:
            cli_logger.info("no clicklog")
            break
        else:
            browserType, browserDevice, browserOs, browserFamily = parse_userAgent(data["agent"])
            sql = "INSERT INTO sys_clicklog set url=%s, ip=%s, agent=%s, method=%s, status_code=%s, referer=%s, isp=%s, browserType=%s, browserDevice=%s, browserOs=%s, browserFamily=%s, clickTime=%s, TimeInterval=%s"
            try:
                mysql.insert(sql, data.get("url"), data.get("ip"), data.get("agent"), data.get("method"), data.get("status_code"), data.get("referer"), getIpArea(data.get("ip")), browserType, browserDevice, browserOs, browserFamily, int(data.get("clickTime") or 0), data.get("TimeInterval"))
            except Exception, e:
                cli_logger.warn(e, exc_info=True)
            else:
                cli_logger.info("refresh_clicklog is ok")
        times -= 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh_loginlog", help=u"刷入登录日志", default=False, action='store_true')
    parser.add_argument("--refresh_clicklog", help=u"刷入访问日志", default=False, action='store_true')
    args = parser.parse_args()
    refresh_loginlog = args.refresh_loginlog
    refresh_clicklog = args.refresh_clicklog
    if refresh_loginlog:
        execute_refresh_loginlog()
    elif refresh_clicklog:
        execute_refresh_clicklog()
    else:
        parser.print_help()
