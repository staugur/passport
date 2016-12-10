FROM registry.saintic.com/python

MAINTAINER Mr.tao <staugur@saintic.com>

ENV PROJECT Passport

ADD ./src /$PROJECT

ADD requirements.txt /tmp

ADD misc/supervisord.conf /etc/

RUN pip install --timeout 30 --index https://pypi.douban.com/simple/ -r /tmp/requirements.txt

WORKDIR /$PROJECT

ENTRYPOINT ["supervisord"]