from Database.models import async_session
from Database.models import User, UserShoppingList, ShoppingList, Product

from sqlalchemy import select, update, delete, and_


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_shopping_list_ig_by_product_id(product_id: int):
    async with async_session() as session:
        return (await session.scalar(select(Product).where(Product.id == product_id))).id_shoppinglist


async def get_shopping_list_title(id_shopping_list: int):
    async with async_session() as session:
        return await session.scalar(select(ShoppingList.title).where(ShoppingList.id == id_shopping_list))


async def get_shopping_list_items(id_shopping_list: int, key_product_start_with: str = ''):
    async with async_session() as session:
        shopping_list_items_obj = await session.scalars(
            select(Product).where(Product.id_shoppinglist == id_shopping_list).order_by(Product.id.asc())
        )
        shopping_list_items: dict[str, str] = dict()
        for item in shopping_list_items_obj:
            shopping_list_items[f'{key_product_start_with}product_{item.id}'] = item.title
        return shopping_list_items


async def get_shopping_list_items_with_check(id_shopping_list: int):
    async with async_session() as session:
        shopping_list_items_obj = await session.scalars(
            select(Product).where(Product.id_shoppinglist == id_shopping_list).order_by(Product.id.asc())
        )
        shopping_list_items: dict[str, str] = dict()
        for item in shopping_list_items_obj:
            if item.check:
                shopping_list_items[f'product_{item.id}'] = f'✅ {item.title}'
            else:
                shopping_list_items[f'product_{item.id}'] = item.title
        return shopping_list_items


async def get_shopping_list_items_with_delete_state(id_shopping_list: int):
    async with async_session() as session:
        shopping_list_items_obj = await session.scalars(
            select(Product).where(Product.id_shoppinglist == id_shopping_list).order_by(Product.id.asc())
        )
        shopping_list_items: dict[str, str] = dict()
        for item in shopping_list_items_obj:
            if item.selected_for_delete:
                shopping_list_items[f'select_item_for_del_product_product_{item.id}'] = f'❌ {item.title}'
            else:
                shopping_list_items[f'select_item_for_del_product_product_{item.id}'] = item.title
        return shopping_list_items


async def get_shopping_lists(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        shopping_lists_ids = await session.scalars(select(UserShoppingList).where(UserShoppingList.id_user == user.id))
        user_shopping_lists: dict[str, str] = {}
        for shopping_list_id in shopping_lists_ids:
            shopping_list = await session.scalar(select(ShoppingList).where(ShoppingList.id == shopping_list_id.id_shopping_list))
            user_shopping_lists[f'shopping_list_{shopping_list.id}'] = shopping_list.title
        return user_shopping_lists


async def create_shopping_list(tg_id, title):
    async with async_session() as session:
        user_id = (await session.scalar(select(User).where(User.tg_id == tg_id))).id
        created_shopping_list = ShoppingList(title=title)
        session.add(created_shopping_list)
        await session.flush()
        await session.refresh(created_shopping_list)
        new_shopping_list = created_shopping_list.id
        session.add(UserShoppingList(id_user=user_id, id_shopping_list=created_shopping_list.id))
        await session.commit()
    return new_shopping_list


async def add_product(shopping_list_id: int, product):
    async with async_session() as session:
        session.add(Product(id_shoppinglist=shopping_list_id, title=product))
        await session.commit()


async def edit_product_check(product_id: int):
    async with async_session() as session:
        product_check = not (await session.scalar(select(Product).where(Product.id == product_id))).check
        await session.execute(update(Product).values(check=product_check).where(Product.id == product_id))
        await session.commit()


async def edit_product_delete_status(product_id: int):
    async with async_session() as session:
        product_delete_status = not (
            await session.scalar(select(Product).where(Product.id == product_id))
        ).selected_for_delete
        await session.execute(
            update(Product).values(selected_for_delete=product_delete_status).where(Product.id == product_id)
        )
        await session.commit()


async def delete_selected_product(shopping_list_id: int):
    async with async_session() as session:
        await session.execute(delete(Product).where(and_(Product.id_shoppinglist == shopping_list_id, Product.selected_for_delete == True)))
        await session.commit()


async def connect_shopping_list(tg_id, shopping_list_id: int):
    async with async_session() as session:
        user_id = (await session.scalar(select(User).where(User.tg_id == tg_id))).id
        user_shopping_list = await session.scalar(select(UserShoppingList).filter(and_(
            UserShoppingList.id_user == user_id,
            UserShoppingList.id_shopping_list == shopping_list_id))
        )
        if not user_shopping_list:
            session.add(UserShoppingList(id_user=user_id, id_shopping_list=shopping_list_id))
            await session.commit()


async def delete_shopping_list(shopping_list_id: int, tg_id: int):
    async with async_session() as session:
        user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
        await session.execute(delete(UserShoppingList).where(and_(
            UserShoppingList.id_shopping_list == shopping_list_id,
            UserShoppingList.id_user == user_id
        )))
        await session.commit()


async def get_product_title_by_id(product_id: int):
    async with async_session() as session:
        return (await session.scalar(select(Product).where(Product.id == product_id))).title


async def set_new_product_title(product_id: int, title: str):
    async with async_session() as session:
        await session.execute(update(Product).where(Product.id == product_id).values(title=title))
        await session.commit()
