from domain.services.user_service import UserService
from domain.services.expense_service import ExpenseService
from domain.services.category_service import CategoryService


async def get_user_service(repo) -> UserService:
    return UserService(repo)


async def get_expense_service(repo) -> ExpenseService:
    return ExpenseService(repo)


async def get_category_service(repo) -> CategoryService:
    return CategoryService(repo)
