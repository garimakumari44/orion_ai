# app/models/user.py

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.database import Base



class Users(Base):
    """
    Application user model.

    Handles authentication,
    authorization,
    and user identity.
    """


    __tablename__ = "users"



    # ==========================
    # Primary Key
    # ==========================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )


    # ==========================
    # User Identity
    # ==========================

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )


    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    # ==========================
    # Authentication
    # ==========================

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    # ==========================
    # Authorization
    # ==========================

    role: Mapped[str] = mapped_column(
        String(50),
        default="user",
        nullable=False,
    )


    # ==========================
    # Account Status
    # ==========================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )


    # ==========================
    # Timestamps
    # ==========================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )



    def __repr__(self) -> str:
        return (
            f"<User id={self.id} "
            f"email={self.email}>"
        )