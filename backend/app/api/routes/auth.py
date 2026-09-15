# app/api/routes/auth.py

from fastapi import (
    APIRouter,
    Depends,
    status,
    Form,
)

from sqlalchemy.ext.asyncio import AsyncSession


from app.db.session import get_db


from app.schemas.auth import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
)


from app.services.auth_service import auth_service


from app.core.dependencies import get_current_user


from app.db.models.user import Users



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)



# =====================================================
# Swagger Login Form
# Removes client_id/client_secret
# =====================================================

class SwaggerLoginForm:

    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
    ):
        self.username = username
        self.password = password



# =====================================================
# REGISTER USER
# =====================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    return await auth_service.register(
        db,
        data.email,
        data.password,
        data.full_name
    )



# =====================================================
# LOGIN
# Frontend JSON Authentication
# =====================================================

@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
):

    return await auth_service.login(
        db,
        data.email,
        data.password
    )



# =====================================================
# TOKEN
# Swagger Authentication
# =====================================================

@router.post(
    "/token",
    response_model=TokenResponse
)
async def login_token(
    form_data: SwaggerLoginForm = Depends(),
    db: AsyncSession = Depends(get_db)
):

    return await auth_service.login(
        db,
        form_data.username,
        form_data.password
    )



# =====================================================
# CURRENT USER
# Protected Route Example
# =====================================================

@router.get(
    "/me",
    response_model=UserResponse
)
async def get_current_user_profile(
    user: Users = Depends(get_current_user)
):

    return user