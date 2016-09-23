#!/usr/bin/python -O
#product environment start application with `tornado IOLoop` and `gevent server`

from main import app
from utils import logger
from config import GLOBAL, PRODUCT, MODULES

Host = GLOBAL.get('Host')
Port = GLOBAL.get('Port')
Environment = GLOBAL.get('Environment')
ProcessName = PRODUCT.get('ProcessName')
ProductType = PRODUCT.get('ProductType')

try:
    import setproctitle
except ImportError, e:
    logger.warn("%s, try to pip install setproctitle, otherwise, you can't use the process to customize the function" %e)
else:
    setproctitle.setproctitle(ProcessName)
    logger.info("The process is %s" % ProcessName)

if GLOBAL.get("put2Redis") == True:
    logger.info("Open process `Put2Redis` to writting.")
    from utils import put2Redis
    from threading import Thread
    from libs.SessionConnection import RedisBaseApi
    SessionType = MODULES.get('Session')['type']
    SessionHost = MODULES.get('Session')['host']
    SessionPort = MODULES.get('Session')['port']
    SessionPass = MODULES.get('Session')['pass']
    rc = RedisBaseApi(SessionType, host=SessionHost, port=SessionPort, auth=SessionPass)
    MISC = {"loglevel": GLOBAL.get("LogLevel"), "proctype": ProductType}
    t = Thread(target=put2Redis, name='Put2Redis', args=(rc, ProcessName, Port, MISC))
    t.start()

try:
    msg = '%s has been launched, %s:%d' %(ProcessName, Host, Port)
    print(msg)
    logger.info(msg)
    if ProductType == 'gevent':
        from gevent.wsgi import WSGIServer
        http_server = WSGIServer((Host, Port), app)
        http_server.serve_forever()

    elif ProductType == 'tornado':
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(Port)
        IOLoop.instance().start()

    elif ProductType == "uwsgi":
        try:
            import os
            from sh import uwsgi
            from multiprocessing import cpu_count
            BASE_DIR= os.path.dirname(os.path.abspath(__file__))
            logfile = os.path.join(BASE_DIR, 'logs', 'uwsgi.log')
            if os.path.exists('uwsgi.ini'):
                uwsgi("--http", "%s:%d"%(Host,Port), "--procname-master", ProcessName, "--procname", ProcessName + ".worker", "--chdir", BASE_DIR, "-w", "api:app", "-d", logfile, "-M", "-p", cpu_count(), "--ini", "uwsgi.ini")
            else:
                uwsgi("--http", "%s:%d"%(Host,Port), "--procname-master", ProcessName, "--procname", ProcessName + ".worker", "--chdir", BASE_DIR, "-w", "api:app", "-d", logfile, "-M", "-p", cpu_count())
        except ImportError:
            msg = r"Start Fail, maybe you did not install the `sh` module."
            logger.error(msg)
            raise ImportError(msg)

    else:
        msg = 'Start the program does not support with %s, abnormal exit!' %ProductType
        logger.error(msg)
        raise RuntimeError(msg)

except Exception,e:
    print(e)
    logger.error(e)
