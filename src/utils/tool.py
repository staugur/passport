# -*- coding: utf8 -*-

import re, time, hashlib, binascii, os, uuid, datetime, json
from log import Syslog
from config import MODULES
from torndb import Connection as torndbConnection
from redis import Redis
from rediscluster import StrictRedisCluster
from functools import wraps
from flask import g, redirect, url_for

MYSQL = MODULES.get("Authentication")
REDIS = MODULES.get("Session")

#公共正则表达式
mail_check    = re.compile(r'([0-9a-zA-Z\_*\.*\-*]+)@([a-zA-Z0-9\-*\_*\.*]+)\.([a-zA-Z]+$)')
chinese_check = re.compile(u"[\u4e00-\u9fa5]+")
ip_pat        = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")

#公共函数
md5           = lambda pwd:hashlib.md5(pwd).hexdigest()
logger        = Syslog.getLogger()
gen_token     = lambda :binascii.b2a_base64(os.urandom(24))[:32]
gen_requestId = lambda :str(uuid.uuid4())

dms   = Redis(host=REDIS.get("host"), port=REDIS.get("port"), db=REDIS.get("db"), password=REDIS.get("pass"), socket_timeout=3, socket_connect_timeout=3, retry_on_timeout=3) if REDIS.get("type") == "redis" else StrictRedisCluster(startup_nodes=[{"host": REDIS.get("host"), "port": REDIS.get("port")}], decode_responses=True, socket_timeout=5)
mysql = torndbConnection(
                    host     = "%s:%s" %(MYSQL.get('Host'), MYSQL.get('Port', 3306)),
                    database = MYSQL.get('Database'),
                    user     = MYSQL.get('User', None),
                    password = MYSQL.get('Passwd', None),
                    time_zone= MYSQL.get('Timezone','+8:00'),
                    charset  = MYSQL.get('Charset', 'utf8'),
                    connect_timeout=3,
                    max_idle_time=3)

def ip_check(ip):
    logger.info("the function ip_check param is %s" %ip)
    if isinstance(ip, (str, unicode)):
        return ip_pat.match(ip)

def Parse_Access_Token(x):
    '''
        parse string, such as access_token=E8BF2BCAF63B7CE749796519F5C5D5EB&expires_in=7776000&refresh_token=30AF0BD336324575029492BD2D1E134B.
        return data, such as {'access_token': 'E8BF2BCAF63B7CE749796519F5C5D5EB', 'expires_in': '7776000', 'refresh_token': '30AF0BD336324575029492BD2D1E134B'}
    '''
    return dict( _.split('=') for _ in x.split('&') )

def How_Much_Time(seconds=0, minutes=0, hours=0):
    dt = datetime.datetime.now() + datetime.timedelta(seconds=int(seconds), minutes=int(minutes), hours=int(hours))
    return dt.strftime("%Y-%m-%d")

def ISOString2Time(s):
    ''' 
    convert a ISO format time to second
    from:2006-04-12 to:23123123
    '''
    import time
    d = datetime.datetime.strptime(s,"%Y-%m-%d")
    return time.mktime(d.timetuple())

def Callback_Returned_To_Dict(x):
    '''
        OAuthResponse class can't parse the JSON data with content-type text/html and because of a rubbish api,
        we can't just tell flask-oauthlib to treat it as json.
    '''
    return json.loads(x[10:-3])

def get_ip(getLanIp=False):
    _WanIpCmd = "/sbin/ifconfig | grep -o '\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}' | grep -vE '192.168.|172.1[0-9]|172.2[0-9]|172.3[0-1]|10.[0-254]|255|127.0.0.1|0.0.0.0'"
    _WanIp    = commands.getoutput(_WanIpCmd).replace("\n", ",")
    if _WanIp:
        logger.info("First get ip success, WanIp is %s with cmd(%s), enter LanIp." %(_WanIp, _WanIpCmd))
    else:
        _WanIp = requests.get("http://members.3322.org/dyndns/getip", timeout=3).text.strip()
        if ip_check(_WanIp):
            logger.info("Second get ip success, WanIp is %s with requests, enter LanIp." %_WanIp)
        else:
            logger.error("get_ip fail")
            return ('', '')
    if getLanIp == True:
        _LanIpCmd = "/sbin/ifconfig | grep -o '\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}' | grep -vE '255|0.0.0.0|127.0.0.1' | sort -n -k 3 -t . | grep -E '192.168.|172.1[0-9]|172.2[0-9]|172.3[0-1]|10.[0-9]'"
        _LanIp    = commands.getoutput(_LanIpCmd).replace("\n", ",") or 'Unknown'
        logger.info("Get ip success, LanIp is %s with cmd(%s), over IP." %(_LanIp, _LanIpCmd))
        Ips = (_WanIp, _LanIp)
    else:
        Ips = (_WanIp,)
    return Ips

def put2Redis(RedisConnection, name="Team.Front", port=10050, misc={}):
    def Ips():
        _WanIps, _LanIps = get_ip(getLanIp=True)
        logger.debug("wanip(%s), lanip(%s)" %(_WanIps, _LanIps))
        WanIp = _WanIps if len(_WanIps.split(",")) == 1 else _WanIps.split(",")[0]
        LanIp = _LanIps if len(_LanIps.split(",")) == 1 else _LanIps.split(",")[0]
        return WanIp, LanIp, _WanIps, _LanIps
    WanIp, LanIp, _WanIps, _LanIps = Ips()
    while True:
        if ip_check(WanIp):
            logger.info("You will write something information into redis.")
            try:
                value = "port:%d, proc:%s, wanIp:%s, lanIp:%s, misc:%s" %(port, name, _WanIps, _LanIps, misc)
                logger.debug(RedisConnection.ttl(name))
                RedisConnection.set(name, value)
                RedisConnection.expire(name, 60)
                logger.info(RedisConnection.get(name))
            except Exception,e:
                logger.error(e)
        else:
            logger.warn("ip invaild, continue.")
            WanIp, LanIp, _WanIps, _LanIps = Ips()
            continue
        time.sleep(15)

def put2RedisSimple(RedisConnection, key, value):
    if key and value:
        try:
            logger.debug(RedisConnection.ttl(key))
            RedisConnection.set(key, value)
            RedisConnection.expire(key, 30)
            logger.info(RedisConnection.get(key))
        except Exception,e:
            logger.error(e)
            return False
        else:
            return True
    else:
        return False

# 计算加密cookie:
def make_signed_cookie(username, flag, seconds=0, minutes=0, hours=0):
    '''
      ::param: username, global in g.
      ::param: flag, it's password(local auth) or openid(qq auth) or userid(weibo auth).
      ::param: seconds, minutes, hours, it's a day time, such as 2016-10-16.
    '''
    expires = How_Much_Time(seconds=seconds, minutes=minutes, hours=hours)
    return '.'.join([ username, expires, md5('%s-%s-%s-%s' %(username, flag, expires, md5("COOKIE_KEY"))).upper() ])

# 解密cookie:
def parse_signed_cookie(cookie_str, flag):
    try:
        L = cookie_str.split('.')

        if len(L) != 3:
            return None

        username, expires, md5str = L

        if expires < How_Much_Time():
            return None

        if not username:
            return None

        if md5str != md5('%s-%s-%s-%s' % (username, flag, expires, md5("COOKIE_KEY"))).upper():
            return None

        return username
    except Exception,e:
        print e
        return None

'''
#Login required in need
def login_required(func):
    logger.info("exec check login")
    @wraps(func)
    def deco(*args, **kwargs):
        logger.debug(dir(g))
        if hasattr(g, "signin"):
            return func(*args, **kwargs)
        else:
            return redirect(url_for("login"))
    return deco
'''
