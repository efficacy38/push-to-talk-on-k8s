#!/bin/env python3.9
import threading
import uuid
from kubernetes import client, config, watch
from kubernetes.leaderelection import leaderelection
from kubernetes.leaderelection.resourcelock.configmaplock import ConfigMapLock
from kubernetes.leaderelection import electionconfig
import logging

# init logging moudle
logging.basicConfig(level=logging.INFO)

# Authenticate using config file
config.load_kube_config(config_file=r"~/.kube/config")
isMaster = False
leaderElectionConfig = {
    "candidate_id": uuid.uuid4(),          # A unique identifier for this candidate
    "lock_name": "rtpengine-controller",   # Name of the lock object to be created
    "lock_namespace": "default"            # Kubernetes namespace
}
flush_cache_timer = None
db_operation = []


def onstarted_leading():
    global isMaster
    isMaster = True


def onstopped_leading():
    global isMaster
    isMaster = False


def leaderElectionJob(leaderElectionConfig):
    # Create config
    # lease_duration: lease's vaild time
    # renew_deadline: if renew take more than this specify time, then release this lease
    # retry_period: renew lock period
    print(leaderElectionConfig)
    config = electionconfig.Config(ConfigMapLock(leaderElectionConfig["lock_name"], leaderElectionConfig["lock_namespace"], leaderElectionConfig["candidate_id"]), lease_duration=17,
                                   renew_deadline=15, retry_period=5, onstarted_leading=onstarted_leading,
                                   onstopped_leading=onstopped_leading)
    # Enter leader election
    leaderelection.LeaderElection(config).run()


def dbJob():
    """
    handle watched data change
    """
    global db_operation, isMaster
    logging.info("db: flush the events " + str(db_operation))
    db_operation = []
    if isMaster:
        print("fake sql cmd dispatch")
    else:
        print("sql not dispatch")


def WatcherJob():
    v1 = client.CoreV1Api()
    w = watch.Watch()
    global flush_cache_timer
    global db_operation
    flush_cache_timer = threading.Timer(5.0, dbJob)

    def addToCache(event):
        global flush_cache_timer
        flush_cache_timer.cancel()
        flush_cache_timer = threading.Timer(5.0, dbJob)
        # logging.info("Event:", event)
        db_operation.append(event)
        flush_cache_timer.start()

    while True:
        for event in w.stream(v1.list_namespaced_pod, namespace="default", label_selector="app=rtpengine", timeout_seconds=1800):
            if (event['type'] == 'DELETED'):
                # delete record from database
                addToCache((
                    event['type'],
                    event['object'].kind,
                    event['object'].metadata.name))

            elif (event['type'] == 'MODIFIED' and event['object'].status.phase == 'Running'):
                # push the record into database
                addToCache((
                    event['type'],
                    event['object'].kind,
                    event['object'].metadata.name,
                    event['object'].metadata.resource_version,
                    event['object'].status.phase))


def main():
    threads = [
        threading.Thread(target=WatcherJob),
        threading.Thread(target=leaderElectionJob,
                         args=(leaderElectionConfig, )),
    ]
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    main()
