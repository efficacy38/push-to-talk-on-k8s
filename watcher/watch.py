#!/bin/env python3.9
# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Uses watch to print the stream of events from list namespaces and list pods.
The script will wait for 10 events related to namespaces to occur within
the `timeout_seconds` threshold and then move on to wait for another 10 events
related to pods to occur within the `timeout_seconds` threshold.
Refer to the document below to understand the server-side & client-side
timeout settings for the watch request handler: ~
https://github.com/github.com/kubernetes-client/python/blob/master/examples/watch/timeout-settings.md
"""

from argparse import Namespace
from sys import api_version
from kubernetes import client, config, watch


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    v1 = client.CoreV1Api()
    w = watch.Watch()
    resource_version = ""
    while True:
        for event in w.stream(v1.list_namespaced_pod, namespace="default", label_selector = "app=rtpengine", timeout_seconds=1800):
            if (event['type'] == 'DELETED'):
                # delete record from database
                print("Event: %s %s %s" % (
                    event['type'],
                    event['object'].kind,
                    event['object'].metadata.name)
                )

            elif (event['type'] == 'MODIFIED' and event['object'].status.phase == 'Running'):
                # push the record into database
                print("Event: %s %s %s %s %s" % (
                    event['type'],
                    event['object'].kind,
                    event['object'].metadata.name,
                    event['object'].metadata.resource_version,
                    event['object'].status.phase)
                )


        # w.stop()
    print("Finished pod stream.")


if __name__ == '__main__':
    main()