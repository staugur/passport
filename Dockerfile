FROM registry.saintic.com/alpine-python:gcc
MAINTAINER Mr.tao <staugur@saintic.com>
ADD ./src /Passport
WORKDIR /Passport
RUN pip install Flask==0.10.1 Flask-RESTful==0.3.5 tornado==4.3 gevent==1.1.1 setproctitle==1.1.10 redis-py-cluster==1.2.0 redis==2.10.5 MySQL-python==1.2.3 torndb==0.3 && chmod +x Product.py
EXPOSE 10030
ENTRYPOINT ["/Passport/Product.py"]