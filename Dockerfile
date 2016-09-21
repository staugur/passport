FROM registry.saintic.com/alpine-python:gcc
MAINTAINER Mr.tao <staugur@saintic.com>
ADD ./src /Auth
WORKDIR /Auth
RUN pip install Flask Flask-RESTful tornado gevent setproctitle redis-py-cluster redis && chmod +x Product.py
EXPOSE 10030
ENTRYPOINT ["/Auth/Product.py"]
