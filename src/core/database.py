import sqlalchemy
import sanic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Database connection
DATABASE_URL = "sqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def attach_db(app: sanic.Sanic):
    app.ctx.db = engine
    app.ctx.db_session = async_session
    app.ctx.db_base = Base

async def close_db(app: sanic.Sanic, loop):
    await app.ctx.db.close()
    await app.ctx.db_session.close()

# Models

class Config(Base):
    __tablename__ = "config"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    key = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    value = sqlalchemy.Column(sqlalchemy.String)

class AuthKeys(Base):
    __tablename__ = "auth_keys"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True, autoincrement=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.func.now())
    key = sqlalchemy.Column(sqlalchemy.String, unique=True, default=sqlalchemy.func.uuid_generate_v4())

# Create the database
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# Fill config table
async def populate_database():
    async with async_session() as session:
        async with session.begin():
            for key in ['external_server_config_endpoint', 'external_check_endpoint', 'max_servers']:
                await session.add(Config(key=key, value=True))
            await session.add(AuthKeys())

# Initiate the database
async def init_db(app: sanic.Sanic, loop):
    await create_db()
    await populate_database()
    await attach_db(app)

async def key_valid(key: str):
    key = key.removeprefix("Bearer ")

    async with async_session() as session:
        async with session.begin():
            key = await session.query(AuthKeys).filter(AuthKeys.key == key).first()
            if key:
                return True
            return False