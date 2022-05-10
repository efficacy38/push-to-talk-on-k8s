FROM mysql:8.0.29
MAINTAINER Jerry Drung "efficacy38@gmail.com"

# Install config and templates
ADD kamailio/utils /tmp/kam-utils
ADD kamctlrc /usr/local/etc/kamailio/kamctlrc
# ADD dispatcher.list /data/kamailio/dispatcher.list

ENTRYPOINT ["/entrypoint.sh"]
EXPOSE 3306 33060
CMD ["mysqld"]
