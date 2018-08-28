FROM registry.cn-beijing.aliyuncs.com/staugur/alpine:python
MAINTAINER staugur <staugur@saintic.com>
ADD src /passport
ADD misc/supervisord.conf /etc/supervisord.conf
ADD requirements.txt /tmp
RUN pip install --timeout 30 --index https://pypi.douban.com/simple/ -r /tmp/requirements.txt
WORKDIR /passport
ENTRYPOINT ["supervisord"]