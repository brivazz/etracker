from domain.repositories.category_repo import AbstractCategoryRepository
from domain.entities.category import CategoryCreate, CategoryInDb


class CategoryService:
    def __init__(self, repo: AbstractCategoryRepository):
        self.repo = repo

    async def add_category(self, category: CategoryCreate) -> CategoryInDb:
        return await self.repo.add(category)

    async def get_user_categories(self, user_id: int) -> list[CategoryInDb]:
        return await self.repo.get_user_categories(user_id)
