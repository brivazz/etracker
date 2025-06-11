from domain.repositories.message_repo import AbstractMessageRepository
from domain.entities.message import MessageCreate

class MessageService:
    def __init__(self, repo: AbstractMessageRepository):
        self.repo = repo

    def add_message(self, user_id: int, text: str):
        msg = MessageCreate(id=0, user_id=user_id, text=text)
        self.repo.save(msg)
