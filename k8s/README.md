# HOW TO CONFIG IT

## import configMap
- import kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg"`
- update kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg" --dry-run=client -o yaml | kubectl apply -f -`
- crate watcher's configMap
    `k create configmap --from-literal=db-host=mysqldb --from-literal=kamailio-rw-user=kamailio --from-literal=kamailio-rw-pw=kamailiorw --from-literal=kamailio-db=kamailio watcher-config`

