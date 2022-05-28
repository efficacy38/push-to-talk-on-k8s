#!/bin/python3
import threading
import uuid
from kubernetes import client, config, watch
from kubernetes.leaderelection import leaderelection
from kubernetes.leaderelection.resourcelock.configmaplock import ConfigMapLock
from kubernetes.leaderelection import electionconfig
from database_controller import Controller
import logging
import os

# self-build informer this is not stable
# FIXME: rewrite it at go lang or js which has informer
# FIXME: change it to class


# init logging moudle
logging.basicConfig(level=logging.INFO)

# Authenticate using config file
# config.load_kube_config(config_file=r"~/.kube/config")
config.load_incluster_config()

# database setting
db_setting = {
    "host": os.environ["DB_HOST"],
    "user": os.environ["KAMAILIO_RW_USER"],
    "password": os.environ["KAMAILIO_RW_PW"],
    "database": os.environ["KAMAILIO_DB"]
}

# leader election setting
leaderElectionConfig = {
    "candidate_id": uuid.uuid4(),                       # A unique identifier for this candidate
    "lock_name": "rtpengine-controller",                # Name of the lock object to be created
    "lock_namespace": os.environ["namespace"]           # Kubernetes namespace
}

# public variables
isMaster = False
flush_cache_timer = None
db_operation = []                                       # cache of db_operation
lock = threading.Lock()                                 # mutex lock for db_operation
db_controller = Controller(**db_setting)


def onstarted_leading():
    global isMaster
    isMaster = True
    threading.Thread(target=WatcherJob).start()


def onstopped_leading():
    global isMaster
    isMaster = False


def leaderElectionJob(leaderElectionConfig):
    # Create config
    # lease_duration: lease's vaild time
    # renew_deadline: if renew take more than this specify time, then release this lease
    # retry_period: renew lock period
    # print(leaderElectionConfig)
    config = electionconfig.Config(ConfigMapLock(leaderElectionConfig["lock_name"], leaderElectionConfig["lock_namespace"], leaderElectionConfig["candidate_id"]), lease_duration=10,
                                   renew_deadline=7, retry_period=5, onstarted_leading=onstarted_leading,
                                   onstopped_leading=onstopped_leading)
    # Enter leader election
    leaderelection.LeaderElection(config).run()


def dbJob():
    """
    handle watched data change
    """
    global db_operation, isMaster, db_controller
    logging.info("db: flush the events " + str(db_operation))

    lock.acquire()

    for event in db_operation:
        if event["event"] == "DELETED":
            db_controller.delete_old_rtpengine(event["ip"])
        else:
            db_controller.add_new_rtpengine(event["ip"])

    db_operation = []
    lock.release()


def WatcherJob():
    v1 = client.CoreV1Api()
    w = watch.Watch()
    global flush_cache_timer, db_operation, isMaster
    flush_cache_timer = threading.Timer(5.0, dbJob)

    def addToCache(event):
        global flush_cache_timer, lock, isMaster, db_operation
        flush_cache_timer.cancel()
        flush_cache_timer = threading.Timer(5.0, dbJob)
        # logging.info("Event:", event)
        if isMaster:
            lock.acquire()

            if event["event"] == 'DELETED':
                db_operation = list(
                    filter(lambda ev: ev["name"] != event["name"], db_operation))
            db_operation.append(event)
            lock.release()
            flush_cache_timer.start()

    while not isMaster:
        continue

    while isMaster:
        for event in w.stream(v1.list_namespaced_pod, namespace="default", label_selector="app=rtpengine", timeout_seconds=1800):
            if not isMaster:
                w.stop()
                flush_cache_timer.cancel()

            if (event['type'] == 'DELETED'):
                # delete record from database
                addToCache({
                    "event": event['type'],
                    "kind": event['object'].kind,
                    "name": event['object'].metadata.name,
                    "ip": event['object'].status.host_ip
                })
            elif ((event['type'] == 'MODIFIED' and event['object'].status.phase == 'Running') or
                  (event['type'] == 'ADDED' and event['object'].status.host_ip != None)):
                # push the record into database
                addToCache(
                    {
                        "event": event['type'],
                        "kind": event['object'].kind,
                        "name": event['object'].metadata.name,
                        "ip": event['object'].status.host_ip,
                        "phase": event['object'].status.phase
                    })


def main():
    threading.Thread(target=leaderElectionJob,
                     args=(leaderElectionConfig,)).start()


if __name__ == '__main__':
    main()
