#!/bin/bash
# Generate JWT secret key for authentication
# Usage: ./deployment/generate-jwt-secret.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Generating JWT Secret Key...${NC}"
echo ""

# Generate 32-byte random hex string
JWT_SECRET=$(openssl rand -hex 32)

echo -e "${GREEN}✓ JWT Secret Key generated:${NC}"
echo ""
echo "$JWT_SECRET"
echo ""
echo -e "${BLUE}Add this to your .env file:${NC}"
echo "JWT_SECRET_KEY=$JWT_SECRET"
echo ""
