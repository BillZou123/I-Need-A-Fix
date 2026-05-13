from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User



#this file runs before your endpoints, and it is used to define dependencies that can be injected into your endpoints. 


# Frontend request

#     ↓

# FastAPI dependency system

#     ↓

# get_db() gives database session

#     ↓

# OAuth2PasswordBearer extracts token

#     ↓

# get_current_user() decodes token and loads user

#     ↓

# endpoint function runs
tokenUrl=f"{settings.API_V1_STR}/login/access-token"
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=tokenUrl)

# we use yield here instead of return, since his dependency prevents you from manually opening/closing sessions in every endpoint.
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session #gives the db session to the endpoint function and close it after the request is done. This is a common pattern in FastAPI to manage database sessions efficiently and safely.


SessionDep = Annotated[Session, Depends(get_db)]  #A SQLModel Session provided by get_db()
TokenDep = Annotated[str, Depends(reusable_oauth2)] #A string token provided by the reusable_oauth2 dependency, which extracts the token from the request's Authorization header.

# Given a database session and a JWT token, decode the token and return the current logged-in user.
def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload) #token_data.sub is the user_id
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)] #Annotated here means that CurrentUser is a User object that is provided by the get_current_user dependency, or function. This allows you to use CurrentUser as a parameter in your endpoint functions, and FastAPI will automatically call get_current_user to provide the current logged-in user based on the token in the request.


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
