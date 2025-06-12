from domain.entities.user_settings import UserSettingsCreate, UserSettingsInDB
from infrastructure.db.sqlalchemy.models import UserSettingsORM


def create_to_orm(settings: UserSettingsCreate) -> UserSettingsORM:
    return UserSettingsORM(
        user_id=settings.user_id, default_category=settings.default_category
    )


def orm_to_entity(orm: UserSettingsORM) -> UserSettingsInDB:
    return UserSettingsInDB(
        id=orm.id,
        user_id=orm.user_id,
        default_category=orm.default_category,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def indb_to_orm(entity: UserSettingsInDB) -> UserSettingsORM:
    return UserSettingsORM(
        id=entity.id,
        user_id=entity.user_id,
        default_category=entity.default_category,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
