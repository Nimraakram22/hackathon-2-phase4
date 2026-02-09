#!/bin/bash
# Start development environment with Skaffold watch mode
# Usage: ./deployment/dev-start.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Todo Chatbot - Development Environment with Hot Reload   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if Skaffold is installed
if ! command -v skaffold &> /dev/null; then
    echo -e "${RED}✗ Skaffold is not installed${NC}"
    echo ""
    echo "Install Skaffold:"
    echo "  macOS:   brew install skaffold"
    echo "  Linux:   curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 && chmod +x skaffold && sudo mv skaffold /usr/local/bin"
    echo "  Windows: choco install skaffold"
    echo ""
    echo "Or visit: https://skaffold.dev/docs/install/"
    exit 1
fi
echo -e "${GREEN}✓ Skaffold is installed${NC}"

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${YELLOW}⚠ Minikube is not running${NC}"
    echo ""
    read -p "Start Minikube now? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo -e "${BLUE}Starting Minikube...${NC}"
        "$SCRIPT_DIR/minikube-setup.sh"
    else
        echo -e "${RED}✗ Minikube is required for development${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Minikube is running${NC}"

# Configure Docker to use Minikube's Docker daemon
echo -e "${BLUE}Configuring Docker for Minikube...${NC}"
eval $(minikube docker-env)
echo -e "${GREEN}✓ Docker configured for Minikube${NC}"

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo ""
    echo "Creating .env from .env.example..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo ""
    echo -e "${YELLOW}⚠ IMPORTANT: Edit .env and add your credentials:${NC}"
    echo "  - GEMINI_API_KEY (required for AI agent)"
    echo "  - DATABASE_URL (required for PostgreSQL)"
    echo "  - JWT_SECRET_KEY (generate with: openssl rand -hex 32)"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Create Kubernetes secret from .env
echo -e "${BLUE}Creating Kubernetes secret from .env...${NC}"
if kubectl get secret todo-chatbot-secret &> /dev/null; then
    kubectl delete secret todo-chatbot-secret
fi

# Read .env and create secret
kubectl create secret generic todo-chatbot-secret \
    --from-env-file="$PROJECT_ROOT/.env" \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Kubernetes secret created${NC}"
echo ""

# Start Skaffold in dev mode
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Starting Skaffold in development mode...                  ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║  Features:                                                 ║${NC}"
echo -e "${BLUE}║  • Hot reload for backend (uvicorn --reload)               ║${NC}"
echo -e "${BLUE}║  • Hot Module Replacement for frontend (Vite HMR)         ║${NC}"
echo -e "${BLUE}║  • Automatic rebuild on file changes                      ║${NC}"
echo -e "${BLUE}║  • File sync for faster iteration                         ║${NC}"
echo -e "${BLUE}║  • Port forwarding to localhost                           ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║  Access URLs:                                              ║${NC}"
echo -e "${BLUE}║  • Frontend: http://localhost:8080                         ║${NC}"
echo -e "${BLUE}║  • Backend:  http://localhost:8000                         ║${NC}"
echo -e "${BLUE}║  • API Docs: http://localhost:8000/docs                    ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║  Press Ctrl+C to stop                                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd "$PROJECT_ROOT"

# Run Skaffold in dev mode
skaffold dev \
    --port-forward \
    --cleanup=true \
    --tail=true \
    --profile=dev

echo ""
echo -e "${GREEN}Development environment stopped${NC}"
