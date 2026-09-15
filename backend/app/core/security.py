# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.core.config import settings


# =====================================================
# Password Hashing Configuration
# =====================================================

password_hash = PasswordHash.recommended()


# =====================================================
# Password Utilities
# =====================================================

def hash_password(password: str) -> str:
    """
    Hash plain password before storing in database.
    Uses Argon2.
    """

    return password_hash.hash(password)



def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify plain password against stored hash.
    """

    return password_hash.verify(
        plain_password,
        hashed_password,
    )


# =====================================================
# JWT Creation
# =====================================================

def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """
    Create JWT access token.
    """

    if expires_delta:

        expire = (
            datetime.now(timezone.utc)
            + expires_delta
        )

    else:

        expire = (
            datetime.now(timezone.utc)
            +
            timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )


    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
    }


    if extra_claims:
        payload.update(extra_claims)


    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )



def create_refresh_token(
    subject: str | int,
) -> str:
    """
    Create refresh token.
    """

    expire = (
        datetime.now(timezone.utc)
        +
        timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )


    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }


    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# =====================================================
# JWT Verification
# =====================================================

def decode_token(
    token: str,
) -> Optional[dict[str, Any]]:
    """
    Decode and validate JWT token.
    """

    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[
                settings.JWT_ALGORITHM
            ],
        )

        return payload


    except JWTError:

        return None



def verify_access_token(
    token: str,
) -> Optional[str]:
    """
    Validate access token
    and return user identity.
    """

    payload = decode_token(token)


    if not payload:
        return None


    if payload.get("type") != "access":
        return None


    return payload.get("sub")



def verify_refresh_token(
    token: str,
) -> Optional[str]:
    """
    Validate refresh token.
    """

    payload = decode_token(token)


    if not payload:
        return None


    if payload.get("type") != "refresh":
        return None


    return payload.get("sub")