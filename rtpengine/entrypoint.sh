#!/bin/bash
set -e

PATH=/usr/local/bin:$PATH

case $CLOUD in
  gcp)
    LOCAL_IP=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/ip)
    PUBLIC_IP=$(curl -s -H "Metadata-Flavor: Google" http://metadata/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip)
    ;;
  aws)
    LOCAL_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    ;;
  digitalocean)
    LOCAL_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/private/0/ipv4/address)
    PUBLIC_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
    ;;
  azure)
    LOCAL_IP=$(curl -H Metadata:true "http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/privateIpAddress?api-version=2017-08-01&format=text")
    PUBLIC_IP=$(curl -H Metadata:true "http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/publicIpAddress?api-version=2017-08-01&format=text")
    ;;
  *)
    ;;
esac

if [ -z "$LOCAL_IP" ]; then
  LOCAL_IP=`ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/'`
fi

if [ -n "$PUBLIC_IP" ]; then
  MY_IP="$LOCAL_IP"!"$PUBLIC_IP"
else
  PUBLIC_IP=$LOCAL_IP
  MY_IP=$PUBLIC_IP
fi

sed -i -e "s/MY_IP/$MY_IP/g" /etc/rtpengine/rtpengine.conf
sed -i -e "s/PRIVATE_IP/$LOCAL_IP/g" /etc/rtpengine/rtpengine.conf

cat /etc/rtpengine/rtpengine.conf

if [ "$1" = 'rtpengine' ]; then
  shift
  exec rtpengine --config-file /etc/rtpengine/rtpengine.conf  "$@"
fi

exec "$@"
