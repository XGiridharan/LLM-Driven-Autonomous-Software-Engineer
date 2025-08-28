```python
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Index


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(50), unique=True, nullable=False)
    notes = relationship("Note", back_populates="user")

    @declared_attr
    def __table_args__(cls):
        return (Index('ix_username', cls.username),)


class Note(Base):
    __tablename__ = "notes"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String(100), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="notes")

    @declared_attr
    def __table_args__(cls):
        return (Index('ix_title', cls.title),)


# Database configuration (replace with your actual database URL)
DATABASE_URL = "postgresql+asyncpg://user:password@host:port/database"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with async_session() as session:
        yield session

#Example of CRUD operations (needs error handling and async context)

async def create_note(db: AsyncSession, title: str, content: str, user_id: int):
    note = Note(title=title, content=content, user_id=user_id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

async def get_note(db: AsyncSession, note_id: int):
    return await db.get(Note, note_id)

async def update_note(db: AsyncSession, note_id: int, title: str, content: str):
    note = await db.get(Note, note_id)
    if note:
        note.title = title
        note.content = content
        await db.commit()
        await db.refresh(note)
        return note
    return None

async def delete_note(db: AsyncSession, note_id: int):
    note = await db.get(Note, note_id)
    if note:
        await db.delete(note)
        await db.commit()
        return True
    return False

async def create_user(db: AsyncSession, username: str):
    user = User(username=username)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# Migration setup (requires Alembic) -  Not implemented here.
# Add Alembic configuration and commands to manage migrations.

```
