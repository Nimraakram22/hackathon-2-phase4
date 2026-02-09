#!/bin/bash
# Cleanup Todo Chatbot deployment from Minikube
# Usage: ./cleanup.sh [--delete-cluster]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RELEASE_NAME="todo-chatbot"
NAMESPACE="default"
DELETE_CLUSTER=false

# Parse arguments
if [[ "$1" == "--delete-cluster" ]]; then
    DELETE_CLUSTER=true
fi

echo -e "${YELLOW}Cleaning up Todo Chatbot deployment...${NC}"
echo ""

# Uninstall Helm release
if helm list --namespace=${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    echo -e "${YELLOW}Uninstalling Helm release...${NC}"
    helm uninstall ${RELEASE_NAME} --namespace=${NAMESPACE}
    echo -e "${GREEN}✓ Helm release uninstalled${NC}"
else
    echo -e "${YELLOW}No Helm release found${NC}"
fi
echo ""

# Delete Secret (if not managed by Helm)
if kubectl get secret ${RELEASE_NAME}-secret --namespace=${NAMESPACE} &> /dev/null; then
    echo -e "${YELLOW}Deleting Secret...${NC}"
    kubectl delete secret ${RELEASE_NAME}-secret --namespace=${NAMESPACE}
    echo -e "${GREEN}✓ Secret deleted${NC}"
fi
echo ""

# Verify cleanup
echo -e "${YELLOW}Verifying cleanup...${NC}"
kubectl get all -l app.kubernetes.io/instance=${RELEASE_NAME} --namespace=${NAMESPACE}
echo ""

# Delete Minikube cluster (optional)
if [ "$DELETE_CLUSTER" = true ]; then
    echo -e "${YELLOW}Deleting Minikube cluster...${NC}"
    minikube delete
    echo -e "${GREEN}✓ Minikube cluster deleted${NC}"
else
    echo -e "${GREEN}Minikube cluster preserved${NC}"
    echo "To delete the cluster, run: ./deployment/cleanup.sh --delete-cluster"
fi
echo ""

echo -e "${GREEN}Cleanup complete!${NC}"
