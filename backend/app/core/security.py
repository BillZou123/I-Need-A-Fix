from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


# A jwt token works like this:
# 1. When a user logs in, we create a JWT token that contains the user's ID (or other identifying information) and an expiration time. We sign this token with a secret key so that it cannot be tampered with.
# 2. The client (e.g., frontend) receives this token and stores it (e.g., in local storage or a cookie).
# 3. For subsequent requests to protected endpoints, the client includes this token in the Authorization header (e.g., "Authorization: Bearer <token>").
# 4. The backend receives the request and extracts the token from the Authorization header. Itn verifies the token using the same secret key that was used to sign it. If the token is valid and not expired, the server can trust the information contained in the token (e.g., the user's ID) and use it to authenticate the user and authorize access to the requested resource. If the token is invalid or expired, the server will reject the request and return an appropriate error response (e



from passlib.context import CryptContext #this package helps with hasing and verifying passwords securely.  

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #BCRYPT is the hasing algo, and deprecated="auto" means that if we ever change the hashing algo in the future, it will automatically mark the old algo as deprecated, which can help with migrating existing passwords to the new algo over time. This way, when a user logs in with an old password hash, we can verify it with the old algo, and if it's valid, we can re-hash the password with the new algo and update it in the database. This allows for a smooth transition to a new hashing algorithm without forcing all users to reset their passwords at once.


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str: #subject is usually the userId
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)} #this defines what the token contains. "sub" is a standard claim in JWT that stands for "subject", and it typically contains the unique identifier of the user (e.g., user ID). "exp" is another standard claim that stands for "expiration time", and it indicates when the token will expire. By including these claims in the token, we can later verify the token and extract the user's identity and check if the token is still valid based on the expiration time.
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt #the final jwt token may look like this: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODg4ODg4ODgsInN1YiI6IjEyMzQ1Njc4OTAifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
