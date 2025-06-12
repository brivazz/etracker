from domain.entities.message import MessageCreate, MessageInDB
from domain.repositories.message_repo import AbstractMessageRepository
from infrastructure.db.sqlalchemy.models import MessageORM
from sqlalchemy.orm import Session


class SQLAlchemyMessageRepository(AbstractMessageRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_messages_by_user(self, user_id: int) -> list[MessageInDB]:
        return [
            MessageInDB(id=m.id, user_id=m.user_id, text=m.text)
            for m in self.session.query(MessageORM).filter_by(user_id=user_id)
        ]

    def save(self, message: MessageCreate):
        orm = MessageORM(user_id=message.user_id, text=message.text)
        self.session.add(orm)
