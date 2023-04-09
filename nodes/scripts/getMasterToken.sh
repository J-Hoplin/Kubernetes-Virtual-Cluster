#!/bin/bash

master_node=$1

multipass exec $master_node -- /bin/bash -c "sudo cat /var/lib/rancher/k3s/server/node-token"