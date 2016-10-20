FROM alpine:gcc
MAINTAINER Mr.tao <staugur@saintic.com>
ENV PROJECR Passport
ADD ./src /$PROJECR
ADD requirements.txt /tmp
WORKDIR /$PROJECR
RUN pip install -r /tmp/requirements.txt && chmod +x Product.py
EXPOSE 10030
ENTRYPOINT ["/$PROJECR/Product.py"]