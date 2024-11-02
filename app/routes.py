from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.database import get_db
from app.deps import get_user
from app.handlers import RequestError
from app.models import Article, Like, User
from app.schemas import (
    ArticleResponseSchema,
    ArticlesResponseSchema,
    LoginSchema,
    ResponseSchema,
    TokenResponseSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import create_auth_token, verify_password

router = APIRouter()


@router.post(
    "/auth/login",
    tags=["Auth"],
    summary="Login a user",
    description="""
        ****
        This endpoint generates new token for a user

        Use any of the following credentials to login:
        1. Email: johndoe@example.com | Password: johndoe
        2. Email: janedoe@example.com | Password: janedoe
    """,
    status_code=201,
)
async def login(
    data: LoginSchema,
    db: AsyncSession = Depends(get_db),
) -> TokenResponseSchema:
    email = data.email
    plain_password = data.password
    user = (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if not user or verify_password(plain_password, user.password) == False:
        raise RequestError(err_msg="Invalid credentials", status_code=401)

    # Create auth token
    token = create_auth_token(user.id)
    return {
        "message": "Login successful",
        "data": {"token": token},
    }


article_tags = (["Articles"],)


@router.get(
    "/articles",
    tags=article_tags,
    summary="View all articles",
    description="""
        ****
        This endpoint allows people to view all existing articles
    """,
    status_code=200,
)
async def articles_view(
    db: AsyncSession = Depends(get_db),
) -> ArticlesResponseSchema:
    articles = (await db.execute(select(Article))).unique().scalars().all()
    return {
        "message": "Articles fetched successfully",
        "data": articles,
    }


@router.get(
    "/articles/{slug:str}",
    tags=article_tags,
    summary="View a single article",
    description="""
        ****
        This endpoint allows people to view a single article details
    """,
    status_code=200,
)
async def single_article_view(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> ArticleResponseSchema:
    article = (
        (await db.execute(select(Article).where(Article.slug == slug)))
        .unique()
        .scalar_one_or_none()
    )
    if not article:
        raise RequestError(err_msg="Article does not exist!", status_code=404)

    return {
        "message": "Article details fetched successfully",
        "data": article,
    }


@router.get(
    "/articles/{slug:str}/like",
    tags=article_tags,
    summary="Like an article",
    description="""
        ****
        This endpoint allows authenticated users to like an article
        Set token generated from the login endpoint in the authorize dialog field. 
    """,
    status_code=200,
)
async def like_article(
    slug: str,
    user: User = Depends(get_user),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema:
    article = (
        (await db.execute(select(Article).where(Article.slug == slug)))
        .unique()
        .scalar_one_or_none()
    )
    if not article:
        raise RequestError(err_msg="Article does not exist!", status_code=404)

    message_substring = "added"
    # If an item with the same user and article id exists, we'll delete, otherwise we'll create
    like_obj = (
        await db.execute(
            select(Like).where(Like.article_id == article.id, Like.user_id == user.id)
        )
    ).scalar_one_or_none()
    if like_obj:
        message_substring = "removed"
        await db.delete(like_obj)
        await db.commit()
    else:
        obj_to_create = Like(user_id=user.id, article_id=article.id)
        db.add(obj_to_create)
        await db.commit()
    return {"message": f"Like {message_substring} successfully"}
