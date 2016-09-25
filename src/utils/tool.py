# -*- coding: utf8 -*-

import re
import time
import torndb
import commands
import hashlib, binascii, os, uuid
from _log import Syslog
from config import MODULES

MYSQL = MODULES.get("Authentication")

#公共正则表达式
mail_check    = re.compile(r'([0-9a-zA-Z\_*\.*\-*]+)@([a-zA-Z0-9\-*\_*\.*]+)\.([a-zA-Z]+$)')
chinese_check = re.compile(u"[\u4e00-\u9fa5]+")
ip_pat        = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")

#公共函数
md5           = lambda pwd:hashlib.md5(pwd).hexdigest()
logger        = Syslog.getLogger()
gen_token     = lambda :binascii.b2a_base64(os.urandom(24))[:32]
gen_requestId = lambda :str(uuid.uuid4())
mysql         = torndb.Connection(
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
def make_signed_cookie(uid, password, max_age):
    expires = str(int(time.time() + max_age))
    L = [uid, expires, md5('%s-%s-%s-%s' % (uid, password, expires, _COOKIE_KEY))]
    return '-'.join(L)

# 解密cookie:
def parse_signed_cookie(cookie_str):
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        id, expires, md5 = L
        if int(expires) < time.time():
            return None
        user = User.get(id)
        if user is None:
            return None
        if md5 != hashlib.md5('%s-%s-%s-%s' % (id, user.password, expires, _COOKIE_KEY)).hexdigest():
            return None
        return user
    except Exception,e:
        print e
        return None
