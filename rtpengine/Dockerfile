FROM debian:buster

MAINTAINER Jerry Drung "efficacy38@gmail.com"

RUN apt-get update \
  && apt-get install -y wget \
  && TMP_DIR=$(mktemp -d) \
  && wget http://ms15.voip.edu.tw/~jerry/build.tar.gz -O "$TMP_DIR/build.tar.gz" \
  && tar -zxvf "$TMP_DIR/build.tar.gz" -C $TMP_DIR \
  && dpkg -i $TMP_DIR/build/bcg729/libbcg729-*.deb \
  && dpkg -i --force-depends $TMP_DIR/build/rtpengine/ngcp-rtpengine-daemon_*.deb \
  && apt --fix-broken install -y \
  && rm -rf $TMP_DIR \
  && rm -rf /var/lib/apt/* \
  && rm -rf /var/lib/dpkg/* \
  && rm -rf /var/lib/cache/* \
  && rm -Rf /var/log/* \
  && rm -Rf /usr/local/src/* \
  && rm -Rf /var/lib/apt/lists/* 

VOLUME ["/tmp"]

EXPOSE 23000-32768/udp 22222/udp

COPY ./entrypoint.sh /entrypoint.sh

COPY ./rtpengine.conf /etc/rtpengine

ENTRYPOINT ["/entrypoint.sh"]

CMD ["rtpengine"]
