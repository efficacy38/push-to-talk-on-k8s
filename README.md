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
    - `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg"`
    - `kubectl create configmap kamailio-db-config --from-env-file="./configs/kamailio_db_env.txt"`
- import kamailio secret
    - `kubectl create secret generic kamailio-db-secret --from-env-file="./configs/kamailio_db_secret_env.txt"`
- create watcher's configMap
    - `k create configmap --from-literal=db-host=mysqldb --from-literal=kamailio-rw-user=kamailio --from-literal=kamailio-rw-pw=kamailiorw --from-literal=kamailio-db=kamailio watcher-config`

<!-- ---
- update kamailio configMap
    `kubectl create configmap kamailio-config --from-file="./configs/kamailio.cfg" --dry-run=client -o yaml | kubectl apply -f -`
-->

### create database table
- create database
    - `k apply -f ./00-database.yaml`
    - this may take long time, using `k get pods | grep mysql` to list pods, it will show 2/2 and Running if it install sucessfully
      ```
      mysqldb-router-56c7d689c-kbqqz         1/1     Running   0             23h
      mysqldb-0                              2/2     Running   0             23h
      mysqldb-1                              2/2     Running   0             23h
      mysqldb-2                              2/2     Running   0             23h
      ```
- (optional) edit the database account info(this is db root password, you can change it as you wish)
    - `vim ./configs/sql/.env`
- open a new terminal, this is a blocked program, which would port forward db to the local environment:
    - `kubectl port-forward service/mysqldb mysql`
- create the tables
    - `cd ./configs/sql`
    - `./create_tbl.sh`

### Deploy the following resource
- `k apply -f ./01-service-watcher.yaml`
- `k apply -f ./02-rtpengine.yaml`
- `k apply -f ./03-kamailio.yaml`

## application configuration
### change rtpengine's port range
- change the `rtpengine.conf`'s `port-min` and `port-max`
- change `docker-compose.yml`'s `.service.rtpengine.ports` to disired mapping
#### example
- if i want to use port 20020 to port 20030
    - at `rtpengine.conf`
        - `port-min=20020`
        - `port-max=20030`
    - at `docker-compose.yml`'s `.service.rtpengine.ports`
        - change it to `20020-20030:20020-20030/udp`

### Create SIP phone accounts and internal carrier links
- create carrier link(for k8s interconnection)
    - `apt install mysql-client`
    - `mysql -u root -psakila -h 127.0.0.1 kamailio`
    - `INSERT INTO address (ip_addr, mask, port, tag) VALUES('10.0.0.0', 8, 5060, 'inter-cluster connection');`
- create user
    - get into one kamailio pod
        - `k exec -it kamailio-deployment-8ddb48ff-82rjf /bin/bash`
        - `curl -o ~/.kamctlrc https://raw.githubusercontent.com/kamailio/kamailio/master/utils/kamctl/kamctlrc`
        - `vim ~/.kamctlrc`
            - uncomment and change `SIP_DOMAIN` to k8s kamailio load balancer service IP
            - uncomment `DBENGINE`
            - uncomment `DBHOST` and change it to `mysqldb`(which is the service that is defined at `00-database.yaml`)
            - uncomment `DBPORT`, `DBNAME`
            - uncomment `DBRWUSER`, `DBRWPW` to your db credentials(which is defined at secret `mypwds`), or keep it as default(unsecure)
        - add user
            - `kamctl add 1010 1234`
                - 1020 is user
                - 1234 is password
    - after config, delete the credentials
        - `rm .kamctlrc`
    - restart the kamailio
        - `k delete -f 03-kamailio.yaml`
        - `k create -f 03-kamailio.yaml`
