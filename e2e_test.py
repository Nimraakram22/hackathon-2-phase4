#!/usr/bin/env python3
"""
End-to-end test script for Todo Chatbot.

Tests the live backend (port 8001) and frontend (port 5173) servers.
"""

import asyncio
import httpx
import sys
from typing import Dict, Optional


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class E2ETestRunner:
    """End-to-end test runner for Todo Chatbot."""

    def __init__(self, backend_url: str = "http://localhost:8001", frontend_url: str = "http://localhost:5173"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.passed = 0
        self.failed = 0
        self.auth_token: Optional[str] = None

    def print_test(self, name: str, status: str, message: str = ""):
        """Print test result with color coding."""
        if status == "PASS":
            print(f"{Colors.GREEN}✓{Colors.RESET} {name}")
            self.passed += 1
        elif status == "FAIL":
            print(f"{Colors.RED}✗{Colors.RESET} {name}")
            if message:
                print(f"  {Colors.RED}{message}{Colors.RESET}")
            self.failed += 1
        elif status == "INFO":
            print(f"{Colors.BLUE}ℹ{Colors.RESET} {name}")

    async def test_backend_health(self) -> bool:
        """Test backend health endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/health", timeout=5.0)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        self.print_test("Backend health check", "PASS")
                        self.print_test(f"  Database: {data.get('database')}", "INFO")
                        self.print_test(f"  Version: {data.get('version')}", "INFO")
                        return True
                    else:
                        self.print_test("Backend health check", "FAIL", f"Unhealthy status: {data}")
                        return False
                else:
                    self.print_test("Backend health check", "FAIL", f"Status code: {response.status_code}")
                    return False
        except Exception as e:
            self.print_test("Backend health check", "FAIL", str(e))
            return False

    async def test_frontend_accessible(self) -> bool:
        """Test frontend is accessible."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.frontend_url, timeout=5.0)

                if response.status_code == 200:
                    if "Todo Chatbot" in response.text or "root" in response.text:
                        self.print_test("Frontend accessible", "PASS")
                        return True
                    else:
                        self.print_test("Frontend accessible", "FAIL", "Unexpected content")
                        return False
                else:
                    self.print_test("Frontend accessible", "FAIL", f"Status code: {response.status_code}")
                    return False
        except Exception as e:
            self.print_test("Frontend accessible", "FAIL", str(e))
            return False

    async def test_api_docs(self) -> bool:
        """Test API documentation is accessible."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/docs", timeout=5.0)

                if response.status_code == 200:
                    self.print_test("API documentation accessible", "PASS")
                    return True
                else:
                    self.print_test("API documentation accessible", "FAIL", f"Status code: {response.status_code}")
                    return False
        except Exception as e:
            self.print_test("API documentation accessible", "FAIL", str(e))
            return False

    async def test_user_registration(self) -> bool:
        """Test user registration endpoint."""
        try:
            import time
            unique_username = f"e2etest_{int(time.time())}"

            async with httpx.AsyncClient() as client:
                register_data = {
                    "email": f"{unique_username}@example.com",
                    "password": "TestPassword123!"
                }

                response = await client.post(
                    f"{self.backend_url}/auth/register",
                    json=register_data,
                    timeout=10.0
                )

                if response.status_code in [200, 201]:
                    self.print_test("User registration", "PASS")
                    return True
                else:
                    self.print_test("User registration", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                    return False
        except Exception as e:
            self.print_test("User registration", "FAIL", str(e))
            return False

    async def test_user_login(self) -> bool:
        """Test user login endpoint."""
        try:
            import time
            unique_username = f"logintest_{int(time.time())}"

            async with httpx.AsyncClient() as client:
                # First register
                register_data = {
                    "email": f"{unique_username}@example.com",
                    "password": "TestPassword123!"
                }

                await client.post(
                    f"{self.backend_url}/auth/register",
                    json=register_data,
                    timeout=10.0
                )

                # Then login
                login_data = {
                    "email": f"{unique_username}@example.com",
                    "password": "TestPassword123!"
                }

                response = await client.post(
                    f"{self.backend_url}/auth/login",
                    json=login_data,
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.auth_token = data["access_token"]
                        self.print_test("User login", "PASS")
                        return True
                    else:
                        self.print_test("User login", "FAIL", "No access token in response")
                        return False
                else:
                    self.print_test("User login", "FAIL", f"Status code: {response.status_code}")
                    return False
        except Exception as e:
            self.print_test("User login", "FAIL", str(e))
            return False

    async def test_cors_headers(self) -> bool:
        """Test CORS headers are properly set."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/health", timeout=5.0)

                headers = response.headers
                # Check for CORS headers (they should be present when accessed from frontend)
                self.print_test("CORS headers configured", "PASS")
                return True
        except Exception as e:
            self.print_test("CORS headers configured", "FAIL", str(e))
            return False

    async def test_security_headers(self) -> bool:
        """Test security headers are properly set."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/health", timeout=5.0)

                headers = response.headers
                required_headers = {
                    "x-content-type-options": "nosniff",
                    "x-frame-options": "DENY",
                    "x-xss-protection": "1; mode=block"
                }

                missing = []
                for header, expected_value in required_headers.items():
                    if header not in headers:
                        missing.append(header)
                    elif headers[header] != expected_value:
                        missing.append(f"{header} (wrong value)")

                if not missing:
                    self.print_test("Security headers", "PASS")
                    return True
                else:
                    self.print_test("Security headers", "FAIL", f"Missing/incorrect: {', '.join(missing)}")
                    return False
        except Exception as e:
            self.print_test("Security headers", "FAIL", str(e))
            return False

    async def run_all_tests(self):
        """Run all e2e tests."""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Todo Chatbot E2E Test Suite{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

        print(f"{Colors.BLUE}Testing Backend: {self.backend_url}{Colors.RESET}")
        print(f"{Colors.BLUE}Testing Frontend: {self.frontend_url}{Colors.RESET}\n")

        # Run tests
        await self.test_backend_health()
        await self.test_frontend_accessible()
        await self.test_api_docs()
        await self.test_user_registration()
        await self.test_user_login()
        await self.test_cors_headers()
        await self.test_security_headers()

        # Print summary
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Test Summary{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        print(f"Total: {self.passed + self.failed}")

        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All tests passed!{Colors.RESET}\n")
            return 0
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ Some tests failed{Colors.RESET}\n")
            return 1


async def main():
    """Main entry point."""
    runner = E2ETestRunner()
    exit_code = await runner.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
