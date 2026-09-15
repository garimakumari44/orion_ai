# app/repositories/user_repository.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import Users



class UserRepository:


    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Users | None:


        result = await db.execute(
            select(Users)
            .where(
                Users.email == email
            )
        )

        return result.scalar_one_or_none()



    async def get_by_id(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Users | None:


        return await db.get(
            Users,
            user_id
        )



    async def create(
        self,
        db: AsyncSession,
        user: Users
    ) -> Users:


        db.add(user)

        await db.commit()

        await db.refresh(user)

        return user