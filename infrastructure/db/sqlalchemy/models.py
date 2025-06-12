from datetime import datetime

from sqlalchemy import Float, ForeignKey, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.sqlalchemy.sqlalchemy_async_session import Base


class IdTimestampsMixin:
    """
    Миксин с полями id, created_at и updated_at
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class UserORM(IdTimestampsMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String)
    balance: Mapped[float] = mapped_column(Float)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)

    # Связь: один пользователь -> много сообщений
    messages: Mapped[list["MessageORM"]] = relationship(back_populates="user")

    # Связь: один пользователь -> много расходов
    expenses: Mapped[list["ExpenseORM"]] = relationship(back_populates="user")

    # Связь: один пользователь -> много категорий
    categories: Mapped[list["CategoryORM"]] = relationship(back_populates="user")

    # Связь: один пользователь <-> одна настройка
    settings: Mapped["UserSettingsORM"] = relationship(back_populates="user")


class ExpenseORM(IdTimestampsMixin, Base):
    __tablename__ = "expenses"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    # category: Mapped[str] = mapped_column(String)
    note: Mapped[str] = mapped_column(String)

    # Обратная связь: расход может быть связан с множеством категорий
    category = relationship("CategoryORM", back_populates="expenses")

    # Обратная связь: расход принадлежит пользователю
    user: Mapped["UserORM"] = relationship(back_populates="expenses")


class CategoryORM(IdTimestampsMixin, Base):
    __tablename__ = "categories"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )

    # Связь: категория принадлежит одному пользователю
    user: Mapped["UserORM"] = relationship(back_populates="categories")

    # Связь: категория может быть связана с многими расходами
    expenses: Mapped[list["ExpenseORM"]] = relationship(back_populates="category")


class MessageORM(IdTimestampsMixin, Base):
    __tablename__ = "messages"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(String)

    # Обратная связь: сообщение принадлежит пользователю
    user: Mapped["UserORM"] = relationship(back_populates="messages")


class UserSettingsORM(IdTimestampsMixin, Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    default_category: Mapped[str] = mapped_column(String)

    # Обратная связь: настройки принадлежат пользователю
    user: Mapped["UserORM"] = relationship(back_populates="settings")
