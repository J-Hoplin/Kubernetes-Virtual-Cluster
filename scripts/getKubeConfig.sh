#!/bin/bash


master_node=$1
master_node_ip=$2
kube_config=$3


multipass transfer $master_node:/etc/rancher/k3s/k3s.yaml config
sed -i '' -e "s/127.0.0.1/$master_node_ip/g" config
mv config $kube_config