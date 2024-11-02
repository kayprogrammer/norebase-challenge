from datetime import datetime
import random
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    event,
    select,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship
from .database import Base, SessionLocal
import uuid
from slugify import slugify


class BaseModel(Base):
    __abstract__ = True
    id: Mapped[uuid.UUID] = Column(
        UUID(), default=uuid.uuid4, unique=True, primary_key=True
    )
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = Column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )


class User(BaseModel):
    __tablename__ = "users"
    name: Mapped[str] = Column(String(500))
    email: Mapped[str] = Column(String(), unique=True)
    password: Mapped[str] = Column(String())

    def __repr__(self):
        return self.name


class Article(BaseModel):
    __tablename__ = "articles"
    title: Mapped[str] = Column(String(500))
    slug: Mapped[str] = Column(String, unique=True, index=True)
    desc: Mapped[str] = Column(Text())
    likes = relationship("Like", back_populates="article")

    def __repr__(self):
        return self.title


@event.listens_for(Article, "before_insert")
async def before_insert_listener(mapper, connection, target):
    base_slug = slugify(target.title)
    slug = base_slug
    # Generate unique slug before insert
    async with SessionLocal() as session:
        while True:
            existing = (
                await session.execute(select(Article).where(Article.slug == slug))
            ).scalar_one_or_none()
            if not existing:  # No collision found
                break
            slug = f"{base_slug}-{random.randint(100000, 999999)}"
        target.slug = slug


class Like(BaseModel):
    __tablename__ = "likes"
    user_id: Mapped[uuid.UUID] = Column(
        UUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    article_id: Mapped[uuid.UUID] = Column(
        UUID(),
        ForeignKey("articles.id", ondelete="CASCADE"),
    )

    # Ensures a user can like an article only once
    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="unique_user_article_like"),
    )

    article = relationship("Article", back_populates="likes")
