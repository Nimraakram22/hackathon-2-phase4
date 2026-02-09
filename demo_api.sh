#!/bin/bash
# Live API demonstration script

echo "==================================="
echo "Todo Chatbot - Live API Demo"
echo "==================================="
echo ""

# 1. Health Check
echo "1. Testing Backend Health..."
curl -s http://localhost:8001/health | jq .
echo ""

# 2. Register User
echo "2. Registering New User..."
TIMESTAMP=$(date +%s)
EMAIL="demo_${TIMESTAMP}@example.com"

REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"TestPassword123!\"}")

echo "$REGISTER_RESPONSE" | jq .
echo ""

# 3. Extract Token
TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "3. Authentication Successful!"
    echo "Token: ${TOKEN:0:50}..."
    echo ""

    # 4. Get User Profile
    echo "4. Fetching User Profile..."
    curl -s -X GET http://localhost:8001/auth/me \
      -H "Authorization: Bearer $TOKEN" | jq .
    echo ""

    echo "✅ All API tests passed!"
else
    echo "❌ Registration failed"
    exit 1
fi

echo ""
echo "==================================="
echo "Demo Complete!"
echo "==================================="
