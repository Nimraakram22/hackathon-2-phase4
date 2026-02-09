#!/bin/bash
# Build script for Todo Chatbot container images
# Usage: ./build-images.sh [--push]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_IMAGE="todo-chatbot-frontend"
BACKEND_IMAGE="todo-chatbot-backend"
VERSION="1.0.0"
PUSH_IMAGES=false

# Parse arguments
if [[ "$1" == "--push" ]]; then
    PUSH_IMAGES=true
fi

echo -e "${GREEN}Building Todo Chatbot container images...${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Build frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
cd "$PROJECT_ROOT/frontend"
docker build -t "${FRONTEND_IMAGE}:${VERSION}" -t "${FRONTEND_IMAGE}:latest" .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image built successfully${NC}"
    FRONTEND_SIZE=$(docker images "${FRONTEND_IMAGE}:${VERSION}" --format "{{.Size}}")
    echo -e "  Image size: ${FRONTEND_SIZE}"
else
    echo -e "${RED}✗ Frontend image build failed${NC}"
    exit 1
fi
echo ""

# Build backend image
echo -e "${YELLOW}Building backend image...${NC}"
cd "$PROJECT_ROOT/backend"
docker build -t "${BACKEND_IMAGE}:${VERSION}" -t "${BACKEND_IMAGE}:latest" .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image built successfully${NC}"
    BACKEND_SIZE=$(docker images "${BACKEND_IMAGE}:${VERSION}" --format "{{.Size}}")
    echo -e "  Image size: ${BACKEND_SIZE}"
else
    echo -e "${RED}✗ Backend image build failed${NC}"
    exit 1
fi
echo ""

# Verify images
echo -e "${YELLOW}Verifying images...${NC}"
FRONTEND_USER=$(docker inspect "${FRONTEND_IMAGE}:${VERSION}" --format='{{.Config.User}}')
BACKEND_USER=$(docker inspect "${BACKEND_IMAGE}:${VERSION}" --format='{{.Config.User}}')

echo -e "  Frontend user: ${FRONTEND_USER}"
echo -e "  Backend user: ${BACKEND_USER}"

if [[ "$FRONTEND_USER" != "nginx" ]] || [[ "$BACKEND_USER" != "app" ]]; then
    echo -e "${RED}✗ Images not running as expected non-root users${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Images verified successfully${NC}"
echo ""

# Push images (optional)
if [ "$PUSH_IMAGES" = true ]; then
    echo -e "${YELLOW}Pushing images to registry...${NC}"
    docker push "${FRONTEND_IMAGE}:${VERSION}"
    docker push "${FRONTEND_IMAGE}:latest"
    docker push "${BACKEND_IMAGE}:${VERSION}"
    docker push "${BACKEND_IMAGE}:latest"
    echo -e "${GREEN}✓ Images pushed successfully${NC}"
    echo ""
fi

# Summary
echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "Images built:"
echo "  - ${FRONTEND_IMAGE}:${VERSION} (${FRONTEND_SIZE})"
echo "  - ${BACKEND_IMAGE}:${VERSION} (${BACKEND_SIZE})"
echo ""
echo "Next steps:"
echo "  1. Deploy to Minikube: ./deployment/deploy.sh"
echo "  2. Or test locally:"
echo "     docker run -p 8080:8080 ${FRONTEND_IMAGE}:${VERSION}"
echo "     docker run -p 8000:8000 ${BACKEND_IMAGE}:${VERSION}"
