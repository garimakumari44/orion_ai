from pydantic import BaseModel, EmailStr, Field
from fastapi import Form



# =====================================
# User Registration
# =====================================

class UserCreate(BaseModel):

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=72
    )

    full_name: str | None = None



# =====================================
# User Login (Frontend JSON)
# =====================================

class UserLogin(BaseModel):

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=72
    )



# =====================================
# Swagger OAuth2 Login Form
# =====================================

class OAuthLoginForm:

    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
    ):

        self.username = username
        self.password = password



# =====================================
# JWT Token Response
# =====================================

class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str = "bearer"



# =====================================
# Public User Response
# =====================================

class UserResponse(BaseModel):

    id: int

    email: EmailStr

    full_name: str | None = None


    class Config:
        from_attributes = True