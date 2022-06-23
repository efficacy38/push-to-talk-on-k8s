# push to talk on k8s

## installation
### install CRD
- install mysql operator
    ```
    kubectl apply -f https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-crds.yaml
    kubectl apply -f https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-operator.yaml
    ```
- add mysql db secret(you may change the value as you wish)
    ```
    kubectl create secret generic mypwds \
        --from-literal=rootUser=root \
        --from-literal=rootHost=% \
        --from-literal=rootPassword="sakila"
    ```

### import configuration
- change to the directory
    - `cd k8s` 
- import kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg"`
    `kubectl create configmap kamailio-db-config --from-env-file="./configs/kamailio_db_env.txt"`
- import kamailio secret
    `kubectl create secret generic kamailio-db-secret --from-env-file="./configs/kamailio_db_secret_env.txt"`
- crate watcher's configMap
    `k create configmap --from-literal=db-host=mysqldb --from-literal=kamailio-rw-user=kamailio --from-literal=kamailio-rw-pw=kamailiorw --from-literal=kamailio-db=kamailio watcher-config`

<!-- ---
- update kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg" --dry-run=client -o yaml | kubectl apply -f -`
-->

### create database table
- create database
    - `k apply -f ./k8s/00-database.yaml`
- edit the database account info(associate with `mypwds` secret resource)
    - `vim k8s/configs/sql/.env`
- port forward db to local environment:
    - `kubectl port-forward service/mysqldb mysql`
- create the tables
    - `cd k8s/configs/sql`
    - `./create_tbl.sh`

### Deploy following resource
- `k apply -f ./k8s/01-service-watcher.yaml`
- `k apply -f ./k8s/02-rtpengine.yaml`
- `k apply -f ./k8s/03-kamailio.yaml`

### Create SIP phone account and internal carrier link
- crate carrier link(for k8s inter connection)
    - `mysql -u root -psakila -h 127.0.0.1 kamailio`
    - `INSERT INTO address (ip_addr, mask, port, tag) VALUES('10.0.0.0', 8, 5060, 'inter-cluster connection');`
- create user
    - get into one kamailio pod
        - `k exec -it kamailio-deployment-8ddb48ff-82rjf /bin/bash`
        - `curl -o ~/.kamctlrc https://raw.githubusercontent.com/kamailio/kamailio/master/utils/kamctl/kamctlrc`
        - `vim ~/.kamctlrc`
            - uncomment and change `SIP_DOMAIN` to k8s kamailio loadbalancer service IP
            - uncomment `DBENGINE`
            - uncomment `DBHOST` and change it to `mysqldb`(which is the service that defined at `00-database.yaml`)
            - uncomment `DBPORT`, `DBNAME`
            - uncomment `DBRWUSER`, `DBRWPW` to the your db credentials(which defined at secret `mypwds`), or keep it as default(unsecure)
        - add user
            - `kamctl add 1010 1234`
                - 1020 is user
                - 1234 is password
    - after config, delete the credentials
        - `rm .kamctlrc`
    - restart the kamailio
        - `k delete -f 03-kamailio.yaml`
        - `k create -f 03-kamailio.yaml`
