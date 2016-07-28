FROM alpine:3.4
MAINTAINER Gareth Rushgrove "gareth@puppet.com"

ENV TZ="Etc/UTC"

RUN apk add --update py-pip && \
    rm -rf /var/cache/apk/*

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY src /src

VOLUME packages

EXPOSE 8888

CMD ["python", "/src/package-indexer.py", "--logging=debug", "--interval=10"]
