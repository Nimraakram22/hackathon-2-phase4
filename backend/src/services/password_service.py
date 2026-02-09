"""
Password validation service using Have I Been Pwned k-anonymity API
Checks if passwords have been exposed in data breaches
"""

import hashlib
import httpx
from typing import Tuple


async def check_password_pwned(password: str) -> Tuple[bool, int]:
    """
    Check if password appears in Have I Been Pwned database using k-anonymity.

    Args:
        password: The password to check

    Returns:
        Tuple of (is_pwned, occurrence_count)
        - is_pwned: True if password found in breach database
        - occurrence_count: Number of times password appeared in breaches

    Raises:
        httpx.HTTPError: If API request fails
    """
    # Hash password with SHA-1
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

    # Split into prefix (first 5 chars) and suffix
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]

    # Query API with prefix only (k-anonymity model)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.pwnedpasswords.com/range/{prefix}",
            headers={"User-Agent": "Agentic-Todo-App"},
            timeout=10.0
        )
        response.raise_for_status()

    # Check if suffix appears in response
    for line in response.text.splitlines():
        hash_suffix, count = line.split(':')
        if hash_suffix == suffix:
            return True, int(count)

    return False, 0


def validate_password_strength(password: str) -> Tuple[bool, list[str]]:
    """
    Validate password meets strength requirements.

    Requirements:
    - Minimum 8 characters
    - At least 3 of 4 character types:
      - Uppercase letters (A-Z)
      - Lowercase letters (a-z)
      - Numbers (0-9)
      - Special characters (!@#$%^&*()_+-=[]{}|;:,.<>?)

    Args:
        password: The password to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")

    # Check character type requirements
    has_uppercase = any(c.isupper() for c in password)
    has_lowercase = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    char_types_count = sum([has_uppercase, has_lowercase, has_digit, has_special])

    if char_types_count < 3:
        errors.append(
            "Password must contain at least 3 of 4 character types: "
            "uppercase, lowercase, numbers, special characters"
        )

    return len(errors) == 0, errors


async def validate_password(password: str) -> Tuple[bool, list[str]]:
    """
    Complete password validation including strength and breach check.

    Args:
        password: The password to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    # Check password strength
    is_strong, strength_errors = validate_password_strength(password)

    if not is_strong:
        return False, strength_errors

    # Check if password has been pwned
    try:
        is_pwned, count = await check_password_pwned(password)

        if is_pwned:
            return False, [
                f"This password has been exposed in {count:,} data breaches. "
                "Please choose a different password."
            ]
    except Exception as e:
        # Log error but don't block signup if API is down
        print(f"Warning: Could not check password against breach database: {e}")

    return True, []
