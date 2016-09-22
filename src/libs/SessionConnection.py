#-*- coding:utf8 -*-
#Conection Redis Module.

from utils import logger
try:
    import redis
    import rediscluster
except ImportError,e:
    logger.error(e)
    raise ImportError('%s, maybe you need to install `redis-py-cluster`.' %e)


def RedisBaseApi(sessionType, **kw):
    logger.info(sessionType, kw)
    host = kw.get("host")
    port = kw.get("port")
    auth = kw.get("pass", kw.get("auth", None))
    rc1  = redis.Redis(host=host, port=port, password=auth, socket_timeout=5, socket_connect_timeout=3, retry_on_timeout=3)
    rc2  = rediscluster.StrictRedisCluster(startup_nodes=[{"host": host, "port": port}], decode_responses=True, socket_timeout=5)
    if sessionType == "redis":
        rc = rc1
    elif sessionType == "redis_cluster":
        rc = rc2
    else:
        logger.error("sessionType is error, nonsupport.")
        return None
    return rc

