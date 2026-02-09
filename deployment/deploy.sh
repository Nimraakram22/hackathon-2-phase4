#!/bin/bash
# Deploy Todo Chatbot to Minikube
# Usage: ./deploy.sh [--upgrade]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RELEASE_NAME="todo-chatbot"
NAMESPACE="default"
UPGRADE=false

# Parse arguments
if [[ "$1" == "--upgrade" ]]; then
    UPGRADE=true
fi

echo -e "${GREEN}Deploying Todo Chatbot to Minikube...${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${RED}✗ Minikube is not running${NC}"
    echo "Start Minikube: ./deployment/minikube-setup.sh"
    exit 1
fi
echo -e "${GREEN}✓ Minikube is running${NC}"

# Check if Docker is configured for Minikube
if ! docker info 2>/dev/null | grep -q "minikube"; then
    echo -e "${YELLOW}⚠ Docker is not configured for Minikube${NC}"
    echo "Run: eval \$(minikube docker-env)"
    echo ""
    read -p "Configure Docker for Minikube now? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        eval $(minikube docker-env)
        echo -e "${GREEN}✓ Docker configured for Minikube${NC}"
    fi
fi
echo ""

# Check if images exist in Minikube
echo -e "${YELLOW}Checking for container images...${NC}"
if ! docker images | grep -q "todo-chatbot-frontend.*1.0.0"; then
    echo -e "${YELLOW}⚠ Frontend image not found in Minikube${NC}"
    echo "Building images..."
    cd "$PROJECT_ROOT"
    ./deployment/build-images.sh
else
    echo -e "${GREEN}✓ Container images found${NC}"
fi
echo ""

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Create .env file with your credentials:"
    echo "  DATABASE_URL=postgresql://user:password@host:5432/database"
    echo "  GEMINI_API_KEY=your-gemini-api-key"
    echo "  JWT_SECRET_KEY=generate-with-openssl-rand-hex-32"
    echo "  NEON_API_KEY=your-neon-api-key"
    echo ""
    echo "Or copy from example: cp .env.example .env"
    exit 1
fi
echo -e "${GREEN}✓ .env file found${NC}"

# Create or update Kubernetes Secret
echo -e "${YELLOW}Creating Kubernetes Secret...${NC}"
kubectl create secret generic ${RELEASE_NAME}-secret \
    --from-env-file="$PROJECT_ROOT/.env" \
    --namespace=${NAMESPACE} \
    --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Secret created/updated${NC}"
echo ""

# Deploy or upgrade Helm chart
cd "$PROJECT_ROOT/helm/todo-chatbot"

if [ "$UPGRADE" = true ]; then
    echo -e "${YELLOW}Upgrading Helm release...${NC}"
    helm upgrade ${RELEASE_NAME} . --namespace=${NAMESPACE}
else
    echo -e "${YELLOW}Installing Helm chart...${NC}"
    helm install ${RELEASE_NAME} . --namespace=${NAMESPACE}
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment successful${NC}"
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi
echo ""

# Wait for pods to be ready
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=${RELEASE_NAME} --timeout=120s --namespace=${NAMESPACE}
echo ""

# Show deployment status
echo -e "${GREEN}Deployment Status:${NC}"
kubectl get pods -l app.kubernetes.io/instance=${RELEASE_NAME} --namespace=${NAMESPACE}
echo ""
kubectl get services -l app.kubernetes.io/instance=${RELEASE_NAME} --namespace=${NAMESPACE}
echo ""
kubectl get pvc -l app.kubernetes.io/instance=${RELEASE_NAME} --namespace=${NAMESPACE}
echo ""

# Get frontend URL
echo -e "${GREEN}Application Access:${NC}"
echo "Frontend URL: $(minikube service ${RELEASE_NAME}-frontend --url --namespace=${NAMESPACE})"
echo ""
echo "Or use port-forward:"
echo "  kubectl port-forward service/${RELEASE_NAME}-frontend 8080:80 --namespace=${NAMESPACE}"
echo "  kubectl port-forward service/${RELEASE_NAME}-backend 8000:8000 --namespace=${NAMESPACE}"
echo ""

echo -e "${GREEN}Deployment complete!${NC}"
