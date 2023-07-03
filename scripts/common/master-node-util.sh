#!/bin/bash

function master-node-install(){
  # Master node global installation script
  
  sudo snap install helm --classic
  sudo snap install jq

  # Prometheus metrics for lens metrics collector
  export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm repo add stable https://charts.helm.sh/stable
  helm repo update
  helm install prometheus prometheus-community/kube-prometheus-stack
}


# Ignore stdin, stdout, stderr outputs to prevent frontend warning logs
master-node-install > /dev/null 2>&1
