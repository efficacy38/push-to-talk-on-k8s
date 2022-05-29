# HOW TO CONFIG IT

## Pre-request
- install mysql operator
    `kubectl apply -f https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-crds.yaml`
    `kubectl apply -f https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-operator.yaml`
- add mysql db secret
    ```
    kubectl create secret generic mypwds \
        --from-literal=rootUser=root \
        --from-literal=rootHost=% \
        --from-literal=rootPassword="sakila"
    ```

## import configMap
- import kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg"`
- update kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg" --dry-run=client -o yaml | kubectl apply -f -`
- crate watcher's configMap
    `k create configmap --from-literal=db-host=mysqldb --from-literal=kamailio-rw-user=kamailio --from-literal=kamailio-rw-pw=kamailiorw --from-literal=kamailio-db=kamailio watcher-config`

