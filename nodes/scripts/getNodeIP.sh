#!/bin/bash

node_name=$1

multipass info $node_name | grep IPv4 | awk '{ print $2 }'