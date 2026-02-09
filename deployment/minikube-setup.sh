#!/bin/bash
# Minikube setup script for Todo Chatbot
# Usage: ./minikube-setup.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Minikube for Todo Chatbot...${NC}"
echo ""

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo -e "${RED}✗ Minikube is not installed${NC}"
    echo "Install Minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi
echo -e "${GREEN}✓ Minikube is installed${NC}"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl is not installed${NC}"
    echo "Install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo -e "${GREEN}✓ kubectl is installed${NC}"

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}✗ Helm is not installed${NC}"
    echo "Install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi
echo -e "${GREEN}✓ Helm is installed${NC}"
echo ""

# Check if Minikube is already running
if minikube status &> /dev/null; then
    echo -e "${YELLOW}Minikube is already running${NC}"
    echo "Current status:"
    minikube status
    echo ""
    read -p "Do you want to delete and recreate the cluster? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deleting existing Minikube cluster...${NC}"
        minikube delete
    else
        echo -e "${GREEN}Using existing Minikube cluster${NC}"
        exit 0
    fi
fi

# Start Minikube with appropriate resources
# Note: 4GB RAM required for application resource limits (1.5Gi request + system overhead)
echo -e "${YELLOW}Starting Minikube cluster...${NC}"
minikube start --cpus=2 --memory=4096 --driver=docker

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Minikube cluster started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start Minikube cluster${NC}"
    exit 1
fi
echo ""

# Enable useful addons
echo -e "${YELLOW}Enabling Minikube addons...${NC}"
minikube addons enable metrics-server
minikube addons enable storage-provisioner
echo -e "${GREEN}✓ Addons enabled${NC}"
echo ""

# Verify cluster is ready
echo -e "${YELLOW}Verifying cluster status...${NC}"
kubectl cluster-info
echo ""
kubectl get nodes
echo ""

# Configure Docker to use Minikube's Docker daemon
echo -e "${YELLOW}Configuring Docker environment...${NC}"
echo "Run the following command to configure your shell:"
echo ""
echo -e "${GREEN}eval \$(minikube docker-env)${NC}"
echo ""

echo -e "${GREEN}Minikube setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure Docker: eval \$(minikube docker-env)"
echo "  2. Build images: ./deployment/build-images.sh"
echo "  3. Deploy application: ./deployment/deploy.sh"
