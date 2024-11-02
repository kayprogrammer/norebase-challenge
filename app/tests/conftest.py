from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import app
from app.database import get_db, Base
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from httpx import AsyncClient
import pytest, asyncio

from app.models import Article, User
from app.utils import get_password_hash

test_db = factories.postgresql_proc(port=None, dbname="test_db")


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine(test_db):
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_db = test_db.dbname
    pg_password = test_db.password

    with DatabaseJanitor(
        user=pg_user,
        host=pg_host,
        port=pg_port,
        dbname=pg_db,
        version=test_db.version,
        password=pg_password,
    ):
        connection_str = f"postgresql+psycopg://{pg_user}:@{pg_host}:{pg_port}/{pg_db}"
        engine = create_async_engine(connection_str)
        yield engine
        engine.dispose()


@pytest.fixture
async def database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    TestSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
    async with TestSessionLocal() as db:
        yield db


@pytest.fixture
async def client(database):
    async def overide_get_db():
        try:
            yield database
        finally:
            await database.close()

    app.dependency_overrides[get_db] = overide_get_db
    async with AsyncClient(app=app, base_url="http://test/api/v1") as client:
        yield client


@pytest.fixture
async def test_user(database):
    user = User(
        name="Test User",
        email="testuser@example.com",
        password=get_password_hash("testpassword"),
    )
    database.add(user)
    await database.commit()
    return user


@pytest.fixture
async def test_article(database):
    article = Article(
        title="Test Article", slug="test-article", desc="This is my test article"
    )
    database.add(article)
    await database.commit()
    return article
