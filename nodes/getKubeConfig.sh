#!/bin/bash


master_node=$1

multipass transfer $master_node:/etc/rancher/k3s/k3s.yaml "$HOME/.kube/config"