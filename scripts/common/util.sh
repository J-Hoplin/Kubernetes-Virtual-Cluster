#!/bin/bash

function install(){
  # Make installation script under this function statements
  
  sudo apt-get install -y nfs-common

  
}


# Ignore stdin, stdout, stderr outputs to prevent frontend warning logs
install > /dev/null 2>&1
