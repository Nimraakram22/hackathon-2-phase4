# Manual Testing Guide - Todo Chatbot

## Quick Start

### Server Status
- **Backend API:** http://localhost:8001
- **Frontend App:** http://localhost:5173
- **API Docs:** http://localhost:8001/docs

## Testing the Backend API

### 1. Health Check
```bash
curl http://localhost:8001/health | jq .
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "0.1.0"
}
```

### 2. Register a New User
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePassword123!"
  }' | jq .
```

Expected response:
```json
{
  "user_id": "uuid-here",
  "email": "testuser@example.com",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Login with Existing User
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePassword123!"
  }' | jq .
```

Save the `access_token` from the response for authenticated requests.

### 4. Get Current User Profile
```bash
# Replace YOUR_TOKEN with the access_token from login/register
curl -X GET http://localhost:8001/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN" | jq .
```

Expected response:
```json
{
  "user_id": "uuid-here",
  "email": "testuser@example.com",
  "created_at": "2026-01-30T00:00:00",
  "is_active": true
}
```

## Testing the Frontend

### 1. Open in Browser
Navigate to: http://localhost:5173

### 2. Test Authentication Flow
1. You should see a login/register form
2. Try registering a new account:
   - Email: `demo@example.com`
   - Password: `DemoPassword123!`
3. After registration, you should be automatically logged in
4. The chat interface should appear

### 3. Test Chat Interface
1. Type a message in the chat input
2. Send a todo-related command like:
   - "Create a task to buy groceries"
   - "Show me my tasks"
   - "Mark task 1 as complete"

## Interactive API Testing with Swagger UI

### Access Swagger UI
Open in browser: http://localhost:8001/docs

### Using Swagger UI
1. **Try the health endpoint:**
   - Click on `GET /health`
   - Click "Try it out"
   - Click "Execute"
   - View the response

2. **Register a user:**
   - Click on `POST /auth/register`
   - Click "Try it out"
   - Modify the request body:
     ```json
     {
       "email": "swagger@example.com",
       "password": "SwaggerTest123!"
     }
     ```
   - Click "Execute"
   - Copy the `access_token` from the response

3. **Authorize for protected endpoints:**
   - Click the "Authorize" button at the top
   - Enter: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"
   - Now you can access protected endpoints like `/auth/me`

## Testing with Postman

### Import Collection
Create a new Postman collection with these requests:

#### 1. Health Check
- Method: GET
- URL: `http://localhost:8001/health`

#### 2. Register User
- Method: POST
- URL: `http://localhost:8001/auth/register`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
  ```json
  {
    "email": "postman@example.com",
    "password": "PostmanTest123!"
  }
  ```

#### 3. Login User
- Method: POST
- URL: `http://localhost:8001/auth/login`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
  ```json
  {
    "email": "postman@example.com",
    "password": "PostmanTest123!"
  }
  ```
- Save the `access_token` to a variable

#### 4. Get User Profile
- Method: GET
- URL: `http://localhost:8001/auth/me`
- Headers: `Authorization: Bearer {{access_token}}`

## Common Issues and Solutions

### Backend Issues

#### Port Already in Use
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>

# Restart backend
cd backend
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Database Connection Error
- Check DATABASE_URL in `backend/.env`
- Verify Neon PostgreSQL is accessible
- Check network connectivity

#### Import Errors
```bash
cd backend
source .venv/bin/activate
poetry install
```

### Frontend Issues

#### Port Already in Use
```bash
# Find process using port 5173
lsof -i :5173

# Kill the process
kill -9 <PID>

# Restart frontend
cd frontend
npm run dev
```

#### API Connection Error
- Verify backend is running on port 8001
- Check `frontend/.env` has correct `VITE_API_URL`
- Check browser console for CORS errors

#### Dependencies Missing
```bash
cd frontend
npm install
```

## Automated Testing

### Run E2E Tests
```bash
# Make sure both servers are running first
python3 e2e_test.py
```

### Run Backend Tests
```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

## Monitoring Server Logs

### Backend Logs
```bash
# View live backend logs
tail -f /tmp/claude-1000/-home-habib-hackathon-2-agentic-todo/tasks/b5c06c5.output
```

### Frontend Logs
```bash
# View live frontend logs
tail -f /tmp/claude-1000/-home-habib-hackathon-2-agentic-todo/tasks/b0e56b5.output
```

## Database Inspection

### Connect to PostgreSQL
```bash
# Using psql (if installed)
psql "postgresql://neondb_owner:npg_vRUnq7sBdI6X@ep-bold-star-ad2blzyw-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

### Common Queries
```sql
-- List all users
SELECT id, email, created_at, is_active FROM users;

-- Count users
SELECT COUNT(*) FROM users;

-- Find user by email
SELECT * FROM users WHERE email = 'testuser@example.com';
```

## Performance Testing

### Simple Load Test
```bash
# Install apache bench if needed
# sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8001/health

# Test with authentication (save token first)
ab -n 100 -c 5 -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/auth/me
```

## Security Testing

### Test CORS
```bash
# Should succeed (allowed origin)
curl -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS http://localhost:8001/auth/login -v

# Should fail (disallowed origin)
curl -H "Origin: http://evil.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS http://localhost:8001/auth/login -v
```

### Test Security Headers
```bash
curl -I http://localhost:8001/health | grep -E "(X-Content-Type-Options|X-Frame-Options|X-XSS-Protection)"
```

### Test Password Requirements
```bash
# Should fail - password too short
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "short"}' | jq .
```

## Stopping the Servers

### Stop Backend
```bash
# Find the process
ps aux | grep uvicorn | grep 8001

# Kill it
kill <PID>

# Or use the task ID if running in background
# (check with /tasks command in Claude Code)
```

### Stop Frontend
```bash
# Find the process
ps aux | grep vite

# Kill it
kill <PID>
```

## Next Steps

1. **Explore the API Documentation**
   - Visit http://localhost:8001/docs
   - Try all available endpoints
   - Understand request/response formats

2. **Test the Frontend**
   - Open http://localhost:5173 in your browser
   - Create an account
   - Test the chat interface
   - Try creating and managing todos

3. **Review the Code**
   - Backend: `backend/src/`
   - Frontend: `frontend/src/`
   - Tests: `backend/tests/` and `e2e_test.py`

4. **Extend the Application**
   - Add new API endpoints
   - Enhance the chat interface
   - Add more todo features
   - Implement real-time updates

## Support

For issues or questions:
- Check the logs in `/tmp/claude-1000/...`
- Review `E2E_TEST_RESULTS.md` for test status
- Check `backend/README.md` and `frontend/README.md`
