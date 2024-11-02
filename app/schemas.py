from ast import List
from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    email: EmailStr = Field(..., example="johndoe@example.com")
    password: str = Field(..., example="password")


class ResponseSchema(BaseModel):
    status: str = "success"
    message: str


class TokenResponseDataSchema(BaseModel):
    token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    )


class TokenResponseSchema(ResponseSchema):
    data: TokenResponseDataSchema


class ArticleSchema(BaseModel):
    name: str
    slug: str
    desc: str
    likes_count: int


class ArticlesResponseSchema(ResponseSchema):
    data: List[ArticleSchema]


class ArticleResponseSchema(ResponseSchema):
    data: ArticleSchema
