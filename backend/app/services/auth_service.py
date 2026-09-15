# app/services/auth_service.py

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

from app.db.models.user import Users

from app.repositories.user_repository import (
    UserRepository
)


user_repository = UserRepository()



class AuthService:


    async def register(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        full_name: str | None
    ):


        existing_user = await user_repository.get_by_email(
            db,
            email
        )


        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )


        user = Users(

            email=email,

            full_name=full_name,

            hashed_password=hash_password(
                password
            )
        )


        return await user_repository.create(
            db,
            user
        )



    async def login(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ):


        user = await user_repository.get_by_email(
            db,
            email
        )


        if not user:

            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )


        if not verify_password(
            password,
            user.hashed_password
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )



        return {

            "access_token":
                create_access_token(
                    user.id
                ),

            "refresh_token":
                create_refresh_token(
                    user.id
                ),

            "token_type":
                "bearer"
        }



auth_service = AuthService()