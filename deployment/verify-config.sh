#!/bin/bash
# Verify deployment configuration for Gemini API
# Usage: ./deployment/verify-config.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Configuration Verification for Gemini API + Hot Reload   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}Checking configuration files...${NC}"
echo ""

# Check 1: .env file exists
echo -n "1. Checking .env file... "
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${YELLOW}⚠ Not found (will be created from .env.example)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 2: GEMINI_API_KEY in .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -n "2. Checking GEMINI_API_KEY in .env... "
    if grep -q "GEMINI_API_KEY=" "$PROJECT_ROOT/.env" && ! grep -q "GEMINI_API_KEY=your-gemini-api-key-here" "$PROJECT_ROOT/.env"; then
        echo -e "${GREEN}✓ Configured${NC}"
    else
        echo -e "${RED}✗ Not configured or using placeholder${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 3: DATABASE_URL in .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -n "3. Checking DATABASE_URL in .env... "
    if grep -q "DATABASE_URL=" "$PROJECT_ROOT/.env" && ! grep -q "DATABASE_URL=postgresql://username:password" "$PROJECT_ROOT/.env"; then
        echo -e "${GREEN}✓ Configured${NC}"
    else
        echo -e "${RED}✗ Not configured or using placeholder${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 4: JWT_SECRET_KEY in .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -n "4. Checking JWT_SECRET_KEY in .env... "
    if grep -q "JWT_SECRET_KEY=" "$PROJECT_ROOT/.env" && ! grep -q "JWT_SECRET_KEY=generate-with-openssl" "$PROJECT_ROOT/.env"; then
        echo -e "${GREEN}✓ Configured${NC}"
    else
        echo -e "${RED}✗ Not configured or using placeholder${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 5: No OPENAI_API_KEY references in Helm templates
echo -n "5. Checking for OPENAI_API_KEY in Helm templates... "
if grep -r "OPENAI_API_KEY" "$PROJECT_ROOT/helm/todo-chatbot/templates/" 2>/dev/null; then
    echo -e "${RED}✗ Found OPENAI_API_KEY references (should be GEMINI_API_KEY)${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ No references found${NC}"
fi

# Check 6: GEMINI_API_KEY in secret template
echo -n "6. Checking GEMINI_API_KEY in secret template... "
if grep -q "GEMINI_API_KEY" "$PROJECT_ROOT/helm/todo-chatbot/templates/secret.yaml"; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 7: GEMINI_API_KEY in backend deployment
echo -n "7. Checking GEMINI_API_KEY in backend deployment... "
if grep -q "GEMINI_API_KEY" "$PROJECT_ROOT/helm/todo-chatbot/templates/backend-deployment.yaml"; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 8: Development Dockerfiles exist
echo -n "8. Checking development Dockerfiles... "
if [ -f "$PROJECT_ROOT/backend/Dockerfile.dev" ] && [ -f "$PROJECT_ROOT/frontend/Dockerfile.dev" ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 9: Skaffold configuration exists
echo -n "9. Checking skaffold.yaml... "
if [ -f "$PROJECT_ROOT/skaffold.yaml" ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 10: dev-start.sh script exists and is executable
echo -n "10. Checking dev-start.sh script... "
if [ -f "$PROJECT_ROOT/deployment/dev-start.sh" ] && [ -x "$PROJECT_ROOT/deployment/dev-start.sh" ]; then
    echo -e "${GREEN}✓ Found and executable${NC}"
else
    echo -e "${RED}✗ Not found or not executable${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 11: Skaffold installed
echo -n "11. Checking Skaffold installation... "
if command -v skaffold &> /dev/null; then
    SKAFFOLD_VERSION=$(skaffold version)
    echo -e "${GREEN}✓ Installed ($SKAFFOLD_VERSION)${NC}"
else
    echo -e "${YELLOW}⚠ Not installed${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 12: Minikube installed
echo -n "12. Checking Minikube installation... "
if command -v minikube &> /dev/null; then
    MINIKUBE_VERSION=$(minikube version --short)
    echo -e "${GREEN}✓ Installed ($MINIKUBE_VERSION)${NC}"
else
    echo -e "${YELLOW}⚠ Not installed${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 13: kubectl installed
echo -n "13. Checking kubectl installation... "
if command -v kubectl &> /dev/null; then
    KUBECTL_VERSION=$(kubectl version --client --short 2>/dev/null || kubectl version --client)
    echo -e "${GREEN}✓ Installed${NC}"
else
    echo -e "${YELLOW}⚠ Not installed${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Verification Summary                                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo -e "${GREEN}Your configuration is ready for development.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start development: ./deployment/dev-start.sh"
    echo "  2. Access frontend: http://localhost:8080"
    echo "  3. Access backend: http://localhost:8000"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo ""
    echo "Warnings are non-critical but should be addressed:"
    if ! command -v skaffold &> /dev/null; then
        echo "  - Install Skaffold: brew install skaffold"
    fi
    if ! command -v minikube &> /dev/null; then
        echo "  - Install Minikube: brew install minikube"
    fi
    if ! command -v kubectl &> /dev/null; then
        echo "  - Install kubectl: brew install kubectl"
    fi
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        echo "  - Create .env file: cp .env.example .env"
    fi
    echo ""
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    fi
    echo ""
    echo "Please fix the errors above before proceeding."
    echo ""
    echo "Common fixes:"
    echo "  - Create .env file: cp .env.example .env"
    echo "  - Add GEMINI_API_KEY to .env"
    echo "  - Add DATABASE_URL to .env"
    echo "  - Generate JWT secret: ./deployment/generate-jwt-secret.sh"
    echo ""
    exit 1
fi
