import logging
from typing import List, Union

from app.models import Article, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import exists
from sqlalchemy.dialects.postgresql import insert
from app.utils import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_initial_data(db: AsyncSession) -> None:
    logger.info("Creating initial data")

    # Create users
    users_to_create = [
        {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "password": get_password_hash("johndoe"),
        },
        {
            "name": "Jane Doe",
            "email": "janedoe@example.com",
            "password": get_password_hash("janedoe"),
        },
    ]
    await check_and_bulk_create_data(db, User, users_to_create)

    # Create articles
    articles_to_create = [
        {
            "title": "My article",
            "slug": "my-article",
            "desc": "This is my first article that I love",
        },
        {
            "title": "Cool article",
            "slug": "cool-article",
            "desc": "Have you seen this article on whatever",
        },
    ]
    await check_and_bulk_create_data(db, Article, articles_to_create)
    logger.info("Initial data created")


async def check_and_bulk_create_data(
    db: AsyncSession, model: Union[Article, User], data: List
) -> None:
    # create articles if none in database
    if not (
        await db.execute(select(exists().where(model.__table__.c.id != None)))
    ).scalar():
        await db.execute(insert(model).values(data).on_conflict_do_nothing())
        await db.commit()
