from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import ResponseSchema
from .conf import settings
from .initial_data import create_initial_data
from .routes import router
from .handlers import exc_handlers
from .database import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create initial data
    async with SessionLocal() as db:
        await create_initial_data(db)
    yield


app = FastAPI(
    title="Norebase Challenge API",
    version="1.0.0",
    description="""
        An API with articles and likes feature.

        Note:
        - Provision for test users are available (login endpoint)
        - I have a more sophisticated API similar to this: 
            Realtime socialnet API - https://socialnet-express.fly.dev 
            Github - https://github.com/kayprogrammer/socialnet-v7
            
    """,
    openapi_url=f"/openapi.json",
    docs_url="/",
    security=[{"BearerToken": []}],
    exception_handlers=exc_handlers,
    lifespan=lifespan,
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "x-requested-with",
        "content-type",
        "accept",
        "origin",
        "authorization",
        "accept-encoding",
        "access-control-allow-origin",
        "content-disposition",
    ],
)

app.include_router(router, prefix="/api/v1")


@app.get(
    "/api/v1/healthcheck",
    name="Healthcheck",
    tags=["Healthcheck"],
    description="""
        ****
        Checks API Health
    """,
)
async def healthcheck() -> ResponseSchema:
    return {"message": "pong!"}
