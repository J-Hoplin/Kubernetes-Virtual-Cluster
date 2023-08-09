#!/bin/bash

node_name=$1
node_cpu=$2
node_memory=$3
node_disk=$4
node_type=$5
master_token=$6
master_ip=$7
k3s_version=$8

common_path=$(dirname $(realpath $0))/common

if [ $node_type = "master" ]; then
  multipass launch --name $node_name --cpus $node_cpu --memory $node_memory --disk $node_disk
  multipass exec $node_name -- /bin/bash -c "curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL='$k3s_version' K3S_KUBECONFIG_MODE='644' INSTALL_K3S_EXEC='--disable traefik'  sh -"
  multipass transfer $common_path/master-node-util.sh $node_name:master-node-util.sh
  multipass exec $node_name -- /bin/bash -c "chmod u+rwx ~/master-node-util.sh"
  multipass exec $node_name -- /bin/bash -c "~/master-node-util.sh"
else
  multipass launch --name $node_name --cpus $node_cpu --memory $node_memory --disk $node_disk
  multipass exec $node_name -- /bin/bash -c "curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL='$k3s_version' K3S_TOKEN='$master_token'  K3S_URL=https://$master_ip:6443 sh -"
fi


multipass transfer $common_path/util.sh $node_name:util.sh
multipass exec $node_name -- /bin/bash -c "chmod u+rwx ~/util.sh"
multipass exec $node_name -- /bin/bash -c "~/util.sh"