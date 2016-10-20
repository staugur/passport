FROM alpine:gcc
MAINTAINER Mr.tao <staugur@saintic.com>
ENV PROJECT Passport
ADD ./src /$PROJECT
ADD requirements.txt /tmp
WORKDIR /$PROJECT
RUN apk add --no-cache mysql-dev
RUN pip install -r /tmp/requirements.txt && chmod +x Product.py
EXPOSE 10030
ENTRYPOINT ["/$PROJECT/Product.py"]