from abc import ABC, abstractmethod
from domain.entities.category import CategoryCreate, CategoryInDb


class AbstractCategoryRepository(ABC):
    @abstractmethod
    async def add(self, category: CategoryCreate) -> CategoryInDb: ...

    @abstractmethod
    async def get_user_categories(self, user_id: int) -> list[CategoryInDb]: ...

    # @abstractmethod
    # async def delete(self, category_id: int) -> bool: ...

    # @abstractmethod
    # async def get_by_id(self, category_id: int) -> CategoryInDb | None: ...

    # @abstractmethod
    # async def update(self, category: CategoryInDb) -> CategoryInDb: ...
