#!/bin/bash

master_node_name=$1
node_name=$2

multipass exec $master_node_name -- /bin/bash -c "kubectl drain $node_name --ignore-daemonsets --delete-local-data"
multipass exec $master_node_name -- /bin/bash -c "kubectl delete node $node_name"