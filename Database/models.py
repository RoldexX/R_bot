from sqlalchemy import Integer, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from Config_data.config import Config, load_config

config: Config = load_config()

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[BigInteger] = mapped_column(BigInteger)


class ShoppingList(Base):
    __tablename__ = 'shopping_lists'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(25))


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_shoppinglist: Mapped[int] = mapped_column(ForeignKey('shopping_lists.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(50))
    check: Mapped[bool] = mapped_column(Boolean, default=False)
    selected_for_delete: Mapped[bool] = mapped_column(Boolean, default=False)


class UserShoppingList(Base):
    __tablename__ = 'users_shopping_lists'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    id_shopping_list: Mapped[int] = mapped_column(ForeignKey('shopping_lists.id', ondelete='CASCADE'))


async def async_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
