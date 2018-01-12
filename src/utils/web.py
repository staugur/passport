# -*- coding: utf-8 -*-
"""
    passport.utils.web
    ~~~~~~~~~~~~~~

    Common function for web.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""
import json
from functools import wraps
from flask import g, request, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.signin:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def clicklog_write(redis, data):
    """访问日志写redis(另外需要有程序或按条件异步读取redis写入到mysql中)"""
    key = "passport:sys_clicklog"
    redis.lpush(key, json.dumps(data))
