FROM alpine
LABEL maintainer="keeb"

VOLUME [ "/data" ]

RUN apk add python3 py3-pip
RUN pip install libtorrent
RUN mkdir -p /data/save && mkdir -p /data/incomplete

COPY . /app
WORKDIR /app

