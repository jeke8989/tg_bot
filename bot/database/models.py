from sqlalchemy import BigInteger, String, ForeignKey, JSON, Table, Column, Integer, Boolean, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(25))
    

class Channel(Base):
    __tablename__ = 'channels'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    id_channel: Mapped[str] = mapped_column(String(30))
    default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user: Mapped[str] = mapped_column(String(25))
    
class Post(Base):
    __tablename__ = 'posts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    message_ob: Mapped[dict] = mapped_column(JSON)
    approve_id_channels: Mapped[str] = mapped_column(String)
    user: Mapped[str] = mapped_column(String(25), nullable=False)
    
    
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)