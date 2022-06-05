# HOW TO CONFIG IT

## Pre-request
- install mysql operator
    ```
    kubectl apply -f https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-crds.yaml
    kubectl apply -f https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-operator.yaml
    ```
- add mysql db secret(you may change as u wish)
    ```
    kubectl create secret generic mypwds \
        --from-literal=rootUser=root \
        --from-literal=rootHost=% \
        --from-literal=rootPassword="sakila"
    ```

## import configuration
- import kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg"`
    `kubectl create configmap kamailio-db-config --from-env-file="./configs/kamailio_db_env.txt"`
- import kamailio secret
    `kubectl create secret generic kamailio-db-secret --from-env-file="./configs/kamailio_db_secret_env.txt"`
- crate watcher's configMap
    `k create configmap --from-literal=db-host=mysqldb --from-literal=kamailio-rw-user=kamailio --from-literal=kamailio-rw-pw=kamailiorw --from-literal=kamailio-db=kamailio watcher-config`

---
- update kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg" --dry-run=client -o yaml | kubectl apply -f -`

## Deploy it!!!
- `k apply -f ./k8s/00-database.yaml`
- `k apply -f ./k8s/01-service-watcher.yaml`
- `k apply -f ./k8s/02-rtpengine.yaml`
- `k apply -f ./k8s/03-kamailio.yaml`
