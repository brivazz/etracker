# domain/services/user_service.py

from domain.repositories.user_repo import AbstractUserRepository
from domain.entities.user import UserCreate, UserInDB

class UserService:
    def __init__(self, repo: AbstractUserRepository):
        self.repo = repo

    async def create_user(self, user: UserCreate) -> UserInDB:
        return await self.repo.add(user)

    async def get_by_telegram_id(self, user: UserCreate) -> UserInDB | None:
        return await self.repo.get_by_telegram_id(telegram_id=user.telegram_id)

    # async def get_user_categories(self, user_id: int) -> list[CategoryInDb]:
    #     return await self.repo.get_user_categories(user_id)

    async def top_up_balance(self, user_id: int, amount: float) -> UserInDB | None:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            return None

        updated_user = UserInDB(
            id=user.id,
            username=user.username,
            balance=user.balance + amount,
            created_at=user.created_at,
        )
        return await self.repo.update(updated_user)
