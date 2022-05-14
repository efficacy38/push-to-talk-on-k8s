# HOW TO CONFIG IT

## import configMap
- import kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg"`
- update kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg" --dry-run=client -o yaml | kubectl apply -f`
