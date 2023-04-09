#!/bin/bash


master_node=$1
master_node_ip=$2
kube_config="$HOME/.kube/config"


multipass transfer $master_node:/etc/rancher/k3s/k3s.yaml $kube_config
sed -i '' -e "s/127.0.0.1/$master_node_ip/g" $kube_config