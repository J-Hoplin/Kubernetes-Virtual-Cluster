#!/bin/bash

# 하... 나중에 각잡고 리팩토링하자...
set -e

if [ $# -lt 1 ]; then
  echo "Usage: $0 node1:ip1 node2:ip2 ..."
  exit 1
fi

# K3s temporary directory
TEMP_DIR=$(mktemp -d)

KUBE_CONFIG="$HOME/.kube/config"
mkdir -p "$HOME/.kube"
MERGED_TEMP_CONFIG="$TEMP_DIR/merged_k3s.yaml"

for node_info in "$@"; do
    NODE_NAME=$(echo $node_info | cut -d: -f1)
    NODE_IP=$(echo $node_info | cut -d: -f2)
    TEMP_CONFIG="$TEMP_DIR/${NODE_NAME}.yaml"
    CONTEXT_NAME="k3s-$NODE_NAME"

    if ! multipass exec $NODE_NAME -- sudo cat /etc/rancher/k3s/k3s.yaml > "$TEMP_CONFIG"; then
        continue
    fi

    # Replace config values to sync with multipass instance values
    sed -i.bak "s/127.0.0.1/$NODE_IP/g" "$TEMP_CONFIG" && rm -f "${TEMP_CONFIG}.bak"
    sed -i.bak "s/name: default/name: $CONTEXT_NAME/g" "$TEMP_CONFIG" && rm -f "${TEMP_CONFIG}.bak"
    sed -i.bak "s/cluster: default/cluster: $CONTEXT_NAME/g" "$TEMP_CONFIG" && rm -f "${TEMP_CONFIG}.bak"
    sed -i.bak "s/user: default/user: $CONTEXT_NAME/g" "$TEMP_CONFIG" && rm -f "${TEMP_CONFIG}.bak"
    sed -i.bak "s/current-context: default/current-context: $CONTEXT_NAME/g" "$TEMP_CONFIG" && rm -f "${TEMP_CONFIG}.bak"

    if [ ! -f "$MERGED_TEMP_CONFIG" ]; then
        cp "$TEMP_CONFIG" "$MERGED_TEMP_CONFIG"
    else
        KUBECONFIG="$MERGED_TEMP_CONFIG:$TEMP_CONFIG" kubectl config view --flatten > "$TEMP_DIR/temp_merged"
        mv "$TEMP_DIR/temp_merged" "$MERGED_TEMP_CONFIG"
    fi
done


# Merge kubeconfig from k3s cluster and host machine kubeconfig
if [ -f "$KUBE_CONFIG" ]; then
    CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "")
    if [ -n "$CURRENT_CONTEXT" ]; then
        if ! kubectl config get-contexts "$CURRENT_CONTEXT" &>/dev/null; then
            kubectl config unset current-context &>/dev/null || true
        fi
    fi

    # Remove context from kubeconfig if same context name exist
    for node_info in "$@"; do
        NODE_NAME=$(echo $node_info | cut -d: -f1)
        CONTEXT_NAME="k3s-$NODE_NAME"
        if kubectl config get-contexts $CONTEXT_NAME &>/dev/null; then
            kubectl config delete-context "$CONTEXT_NAME" &>/dev/null || true
            kubectl config delete-cluster "$CONTEXT_NAME" &>/dev/null || true
            kubectl config delete-user "$CONTEXT_NAME" &>/dev/null || true
        fi
    done

    KUBECONFIG="$KUBE_CONFIG:$MERGED_TEMP_CONFIG" kubectl config view --flatten > "$TEMP_DIR/final_merged"
    mv "$TEMP_DIR/final_merged" "$KUBE_CONFIG"
else
    cp "$MERGED_TEMP_CONFIG" "$KUBE_CONFIG"
fi

chmod 600 "$KUBE_CONFIG"

rm -rf "$TEMP_DIR"

export KUBECONFIG="$KUBE_CONFIG"
