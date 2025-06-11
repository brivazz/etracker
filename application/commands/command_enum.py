from enum import Enum

class Command(Enum):
    REGISTER_OR_GET_USER = "register_or_get_user"
    ADD_EXPENSE = "add_expense"
    EDIT_EXPENSE = "edit_expense"
    DELETE_EXPENSE = "delete_expense"
    GET_EXPENSE_HISTORY = "get_expense_history"
    GET_USER_CATEGORIES = "get_user_categories"
    ADD_CATEGORY = "add_category"
    GET_STATS_EXPENSE = "get_stats_expense"
    GET_LAST_EXPENSE = "get_last_expense"
