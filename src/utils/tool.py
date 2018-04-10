# -*- coding: utf-8 -*-
"""
    passport.utils.tool
    ~~~~~~~~~~~~~~

    Common function.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import re
import json
import hashlib
import random
import hmac
import shortuuid
import requests
import time
import datetime
from uuid import uuid4
from log import Logger
from base64 import b32encode
from redis import from_url
from torndb import Connection
from user_agents import parse as user_agents_parse
from config import SYSTEM, REDIS as REDIS_URL, MYSQL as MYSQL_URL
from version import __version__


ip_pat = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
mail_pat = re.compile(r"([0-9a-zA-Z\_*\.*\-*]+)@([a-zA-Z0-9\-*\_*\.*]+)\.([a-zA-Z]+$)")
mobilephone_pat = re.compile(r'1[3,4,5,7,8]\d{9}')
Universal_pat = re.compile(r'^[a-zA-Z\_][0-9a-zA-Z\_]*$')
domain_name_pat = re.compile(r'^[a-z][0-9a-z\_]{4,32}$')
comma_pat = re.compile(r"\s*,\s*")
url_pat = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
logger = Logger("sys").getLogger
cli_logger = Logger("cli").getLogger
err_logger = Logger("error").getLogger
plugin_logger = Logger("plugin").getLogger
access_logger = Logger("access").getLogger
md5 = lambda pwd: hashlib.md5(pwd).hexdigest()
hmac_sha256 = lambda message: hmac.new(key=SYSTEM["HMAC_SHA256_KEY"], msg=message, digestmod=hashlib.sha256).hexdigest()
gen_token = lambda n=32: b32encode(uuid4().hex)[:n]
gen_requestId = lambda: str(uuid4())
gen_fingerprint = lambda n=16, s=2: ":".join(["".join(random.sample("0123456789abcdef", s)) for i in range(0, n)])
gen_uniqueId = lambda: shortuuid.uuid()
# 列表按长度切割
ListEqualSplit = lambda l, n=5: [l[i:i+n] for i in range(0, len(l), n)]
# 无重复随机数
gen_rnd_filename = lambda: "%s%s" % (datetime.datetime.now().strftime('%Y%m%d%H%M%S'), str(random.randrange(1000, 10000)))
# 文件名合法性验证
allowed_file = lambda filename: '.' in filename and filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg', 'gif'])


def ip_check(ip):
    if ip and isinstance(ip, (str, unicode)):
        return ip_pat.match(ip)


def email_check(email):
    if email and isinstance(email, (str, unicode)):
        return mail_pat.match(email)


def phone_check(phone):
    if phone and isinstance(phone, (str, unicode)):
        return mobilephone_pat.match(phone)


def avatar_check(avatar):
    if avatar:
        if avatar.startswith("/") and allowed_file(avatar):
            return True
        elif url_pat.match(avatar):
            return True
    return False


def sql_safestring_check(string):
    """检查拼接sql的字符串是否安全，另外有`MySQLdb.escape_string`
    诸如：含有问号、逗号、分号、百分号、转义符不予通过
    返回：True代表安全，False表示不安全
    """
    if string:
        if "'" in string or '"' in string or '?' in string or '%' in string or ';' in string or '*' in string or '=' in string or "\\" in string:
            return False
    return True


def parse_phone(phone):
    """判断并解析手机号所属运营商
    返回：1-中国移动 2-中国联通 3-中国电信 0-未知或无效手机号
    """
    phone = str(phone)
    if phone_check(phone):
        # 中国移动
        # 134, 135 , 136, 137, 138, 139, 147, 150, 151,
        # 152, 157, 158, 159, 178, 182, 183, 184, 187, 188；
        if re.match(r"13[4,5,6,7,8,9]\d{8}", phone) or re.match(r"147\d{8}|178\d{8}", phone) or re.match(r"15[0,1,2,7,8,9]\d{8}", phone) or re.match(r"18[2,3,4,7,8]\d{8}", phone):
            return 1
        # 中国联通：
        # 130，131，132，155，156，185，186，145，176
        elif re.match(r'13[0,1,2]\d{8}', phone) or re.match(r"15[5,6]\d{8}", phone) or re.match(r"18[5,6]", phone) or re.match(r"145\d{8}", phone) or re.match(r"176\d{8}", phone):
            return 2
        else:
            # 中国电信
            # 133,153,189
            return 3
    else:
        return 0


def ParseMySQL(mysql, callback="dict"):
    """解析MYSQL配置段"""
    protocol, dburl = mysql.split("://")
    if "?" in mysql:
        dbinfo, dbargs = dburl.split("?")
    else:
        dbinfo, dbargs = dburl, "charset=utf8&timezone=+8:00"
    host, port, user, password, database = dbinfo.split(":")
    charset, timezone = dbargs.split("&")[0].split("charset=")[-1] or "utf8", dbargs.split("&")[-1].split("timezone=")[-1] or "+8:00"
    if callback in ("list", "tuple"):
        return protocol, host, port, user, password, database, charset, timezone
    else:
        return {"protocol": protocol, "host": host, "port": port, "database": database, "user": user, "password": password, "charset": charset, "time_zone": timezone}


def create_redis_engine():
    """ 创建redis连接 """
    return from_url(REDIS_URL)


def create_mysql_engine():
    """ 创建mysql连接 """
    protocol, host, port, user, password, database, charset, timezone = ParseMySQL(MYSQL_URL, callback="tuple")
    return Connection(host="{}:{}".format(host, port), database=database, user=user, password=password, time_zone=timezone, charset=charset)


class DO(dict):
    """A dict that allows for object-like property access syntax."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


def getIpArea(ip):
    """查询IP地址信息，返回格式：国家 省级 市级 运营商"""
    if ip == "127.0.0.1":
        return u"本地IP"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36"}
    url = "http://ip.taobao.com/service/getIpInfo.php?ip={0}".format(ip)
    try:
        data = DO(requests.get(url, timeout=10, headers=headers).json())
    except requests.exceptions.Timeout:
        try:
            data = DO(requests.get(url, headers=headers).json())
        except Exception:
            return "Unknown"
        else:
            data = DO(data.data)
    else:
        data = DO(data.data)
    if u'内网IP' in data.city:
        city = data.city
    else:
        if data.city:
            city = data.city if u"市" in data.city else data.city + u"市"
        else:
            city = data.city
    return u"{0} {1} {2} {3}".format(data.country, data.region.replace(u'市', ''), city, data.isp)


def get_current_timestamp():
    """ 获取本地当前时间戳(10位): Unix timestamp：是从1970年1月1日（UTC/GMT的午夜）开始所经过的秒数，不考虑闰秒 """
    return int(time.time())


def timestamp_after_timestamp(timestamp=None, seconds=0, minutes=0, hours=0, days=0):
    """ 给定时间戳(10位),计算该时间戳之后多少秒、分钟、小时、天的时间戳(本地时间) """
    # 1. 默认时间戳为当前时间
    timestamp = get_current_timestamp() if timestamp is None else timestamp
    # 2. 先转换为datetime
    d1 = datetime.datetime.fromtimestamp(timestamp)
    # 3. 根据相关时间得到datetime对象并相加给定时间戳的时间
    d2 = d1 + datetime.timedelta(seconds=int(seconds), minutes=int(minutes), hours=int(hours), days=int(days))
    # 4. 返回某时间后的时间戳
    return int(time.mktime(d2.timetuple()))


def timestamp_to_timestring(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """ 将时间戳(10位)转换为可读性的时间 """
    # timestamp为传入的值为时间戳(10位整数)，如：1332888820
    timestamp = time.localtime(timestamp)
    # 经过localtime转换后变成
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    return time.strftime(format, timestamp)


def timestring_to_timestamp(timestring, format="%Y-%m-%d %H:%M:%S"):
    """ 将普通时间格式转换为时间戳(10位), 形如 '2016-05-05 20:28:54'，由format指定 """
    try:
        # 转换成时间数组
        timeArray = time.strptime(timestring, format)
    except Exception:
        raise
    else:
        # 转换成10位时间戳
        return int(time.mktime(timeArray))


def generate_verification_code():
    ''' 随机生成6位的验证码 '''
    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    for i in range(65, 91):  # A-Z
        code_list.append(chr(i))
    for i in range(97, 123):  # a-z
        code_list.append(chr(i))

    myslice = random.sample(code_list, 6)  # 从list中随机获取6个元素，作为一个片断返回
    verification_code = ''.join(myslice)  # list to string
    return verification_code


def parse_userAgent(user_agent):
    """ 解析User-Agent """
    uap = user_agents_parse(user_agent)
    browserDevice, browserOs, browserFamily = str(uap).split(' / ')
    if uap.is_mobile:
        browserType = "mobile"
    elif uap.is_pc:
        browserType = "pc"
    elif uap.is_tablet:
        browserType = "tablet"
    elif uap.is_bot:
        browserType = "bot"
    else:
        browserType = "unknown"
    return browserType, browserDevice, browserOs, browserFamily


def parseAcceptLanguage(acceptLanguage, defaultLanguage="zh-CN"):
    if not acceptLanguage:
        return defaultLanguage
    languages = acceptLanguage.split(",")
    locale_q_pairs = []
    for language in languages:
        if language.split(";")[0] == language:
            # no q => q = 1
            locale_q_pairs.append((language.strip(), "1"))
        else:
            locale = language.split(";")[0].strip()
            q = language.split(";")[1].split("=")[1]
            locale_q_pairs.append((locale, q))
    return sorted(locale_q_pairs, key=lambda x: x[-1], reverse=True)[0][0] or defaultLanguage


def sso_request(kwargs):
    """post重试请求的封装
    kwargs dict: 包含以下具体参数
        @params dict: 请求查询参数
        @data dict: 提交表单数据
        @timeout int: 超时时间，单位秒
        @num_retries int: 超时重试次数
    """
    if kwargs and isinstance(kwargs, dict):
        url = kwargs["url"]
        params = kwargs.get("params", None)
        data = kwargs.get("data", None)
        timeout = kwargs.get("timeout", 5)
        num_retries = kwargs.get("num_retries", 0)
        headers = {"User-Agent": "Mozilla/5.0 (X11; CentOS; Linux i686; rv:7.0.1406) Gecko/20100101 PassportClient/{}".format(__version__)}
        try:
            resp = requests.post(url, params=params, headers=headers, timeout=timeout, data=dict(data=json.dumps(data))).json()
        except requests.exceptions.Timeout,e:
            if num_retries > 0:
                return sso_request(url, params=params, data=data, timeout=timeout, num_retries=num_retries-1)
        else:
            return resp