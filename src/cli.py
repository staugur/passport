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

import sys, json, getpass
from utils.web import dfr
from utils.tool import cli_logger, create_redis_engine, create_mysql_engine, getIpArea, parse_userAgent, get_current_timestamp, gen_uniqueId, email_check
from werkzeug.security import generate_password_hash
from torndb import IntegrityError
reload(sys)
sys.setdefaultencoding('utf-8')

redis = create_redis_engine()
mysql = create_mysql_engine()


def printcolor(msg, color=None):
    if color == "green":
        print '\033[92m{}\033[0m'.format(str(msg))
    elif color == "blue":
        print '\033[94m{}\033[0m'.format(str(msg))
    elif color == "yellow":
        print '\033[93m{}\033[0m'.format(str(msg))
    elif color == "red":
        print '\033[91m{}\033[0m'.format(str(msg))
    else:
        print str(msg)


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


def exec_createSuperuser():
    def __check_hasUser(uid):
        """检查是否存在账号"""
        if uid and len(uid) == 22:
            sql = "SELECT count(uid) FROM user_auth WHERE uid=%s"
            try:
                data = mysql.get(sql, uid)
            except Exception, e:
                cli_logger.warn(e, exc_info=True)
            else:
                if data and isinstance(data, dict):
                    return True if data.get('count(uid)', 0) > 0 else False
        return False
    def __createSuperuser(email, password):
        ''' begin的方式使用事务注册账号，
        参数：
            @param email str: 管理员邮箱
            @param password str: 账号密码
        流程：
            1、写入`user_auth`表
            2、写入`user_profile`表
        返回字典：
            success bool 表示注册是否成功；
            msg str 表示提示信息。
        '''
        res = dict(success=False, msg=None)
        # 校验
        if email_check(email) and 6 <= len(password) <= 30:
            guid = gen_uniqueId()
            ctime = get_current_timestamp()
            try:
                mysql._db.begin()
                try:
                    mysql.insert("INSERT INTO user_auth (uid, identity_type, identifier, certificate, verified, status, ctime) VALUES (%s, %s, %s, %s, %s, %s, %s)", guid, 2, email, generate_password_hash(password), 1, 1, ctime)
                except IntegrityError:
                    res.update(msg="Account already exists")
                    raise
                except Exception, e:
                    res.update(msg="System is abnormal")
                    raise
                else:
                    try:
                        mysql.insert("INSERT INTO user_profile (uid, register_source, ctime, is_admin) VALUES (%s, %s, %s, %s)", guid, 2, ctime, 1)
                    except:
                        raise
                    mysql._db.commit()
            except Exception, e:
                printcolor(str(e), "red")
                res.update(msg="Operation failed, rolled back")
                mysql._db.rollback()
            else:
                if __check_hasUser(guid):
                    res.update(msg="Registration success", success=True)
                else:
                    res.update(msg="Registration failed")
        else:
            res.update(msg="Check failed")
        cli_logger.info(res)
        return res
    try:
        printcolor("请根据提示输入信息以创建管理员用户", "red")
        email = raw_input("请输入管理员邮箱账号：")
        password = getpass.getpass("请输入管理员账号密码：")
        repasswd = getpass.getpass("请确认管理员账号密码：")
    except KeyboardInterrupt:
        sys.stdout.write('\n')
        exit(1)
    else:
        if not email_check(email):
            printcolor("请输入正确的邮箱", "yellow")
        else:
            if password != repasswd:
                printcolor("两次密码不一致", "yellow")
            else:
                res = dfr(__createSuperuser(email, password), "zh-CN")
                if res["success"] is True:
                    printcolor("管理员注册成功，账号是<%s>，密码是<%s>，请妥善保管！" %(email, password), "green")
                else:
                    printcolor(res["msg"], "yellow")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh_loginlog", help=u"刷入登录日志", default=False, action='store_true')
    parser.add_argument("--refresh_clicklog", help=u"刷入访问日志", default=False, action='store_true')
    parser.add_argument("--createSuperuser", help=u"创建管理员用户", default=False, action='store_true')
    args = parser.parse_args()
    refresh_loginlog = args.refresh_loginlog
    refresh_clicklog = args.refresh_clicklog
    createSuperuser = args.createSuperuser
    if refresh_loginlog:
        execute_refresh_loginlog()
    elif refresh_clicklog:
        execute_refresh_clicklog()
    elif createSuperuser:
        exec_createSuperuser()
    else:
        parser.print_help()
