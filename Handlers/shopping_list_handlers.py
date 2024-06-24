from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from Database.requests import (get_shopping_lists,
                               create_shopping_list,
                               add_product,
                               get_shopping_list_title,
                               get_shopping_list_items,
                               get_shopping_list_ig_by_product_id,
                               edit_product_check,
                               delete_shopping_list,
                               connect_shopping_list)
from Keyboards.keyboards import (create_inline_keyboard,
                                 create_reply_keyboard,
                                 create_inline_keyboard_shopping_list_settings)
from Resources.strings_ru import MENU_BUTTONS, MENU_BUTTONS_NEW_LIST, VIEW_SHOPPING_LIST_BUTTONS, SHOPPING_LIST_BUTTONS

router: Router = Router()
keyboard = create_reply_keyboard(2, 'Выберите пункт меню...', **MENU_BUTTONS)


class ShoppingList(StatesGroup):
    select_list = State()
    title = State()
    items = State()


@router.message(F.text == MENU_BUTTONS['shopping_list'])
async def shopping_list(message: Message):
    shopping_lists: dict[str, str] = await get_shopping_lists(message.from_user.id)
    await message.answer(text='Ваши списки покупок',
                         reply_markup=create_inline_keyboard(2, VIEW_SHOPPING_LIST_BUTTONS, **shopping_lists))


@router.callback_query(F.data == 'create_list')
async def new_shopping_list(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ShoppingList.title)
    await callback.answer('Новый список покупок')
    await callback.message.answer('Введите название списка покупок')


@router.message(StateFilter(ShoppingList.title))
async def shopping_list(message: Message, state: FSMContext):
    shopping_list_id = await create_shopping_list(tg_id=message.from_user.id,
                                                  title=message.text)
    await state.update_data(shopping_list_id=shopping_list_id)
    await state.set_state(ShoppingList.items)
    await message.answer(f'Создан список {message.text}',
                         reply_markup=create_reply_keyboard(width=2,
                                                            placeholder='Название продукта',
                                                            **MENU_BUTTONS_NEW_LIST))


@router.message(StateFilter(ShoppingList.items))
async def add_items_to_shopping_list(message: Message, state: FSMContext):
    if message.text == MENU_BUTTONS_NEW_LIST['get_list']:
        shopping_list_id = (await state.get_data())['shopping_list_id']
        products = await get_shopping_list_items(shopping_list_id)
        last_button = {'delet_massage': '❌ закрыть'}
        await message.answer(await get_shopping_list_title(shopping_list_id),
                             reply_markup=create_inline_keyboard(1, last_button,
                                                                 **products))

    elif message.text != MENU_BUTTONS_NEW_LIST['exit']:
        shopping_list_id = (await state.get_data())['shopping_list_id']
        items = message.text.split('\n')
        for item in items:
            await add_product(shopping_list_id, item)
    else:
        await state.clear()
        await message.answer('Хорошо, сохранил ваши продукты', reply_markup=keyboard)


@router.callback_query(F.data.startswith('product_'))
async def edit_check_product(callback: CallbackQuery):
    product_id = callback.data.split('_')[-1]
    shopping_list_id = await get_shopping_list_ig_by_product_id(product_id)
    await edit_product_check(product_id)
    products = await get_shopping_list_items(shopping_list_id)
    await callback.answer('отмечен')
    last_button = {'delet_massage': '❌ закрыть'}
    await callback.message.edit_reply_markup(reply_markup=create_inline_keyboard(1,
                                                                                 last_button,
                                                                                 **products))


@router.callback_query(F.data.startswith('shopping_list_'))
async def shopping_list_callback(callback: CallbackQuery, state: FSMContext):
    shopping_list_id = callback.data.split('_')[-1]
    await callback.answer(callback.data)
    last_button = {'delet_massage': '❌ закрыть'}
    await callback.message.edit_text(await get_shopping_list_title(shopping_list_id),
                                     reply_markup=create_inline_keyboard_shopping_list_settings(
                                         2,
                                         shopping_list_id,
                                         last_button,
                                         **SHOPPING_LIST_BUTTONS))


@router.callback_query(F.data.startswith('get_view_'))
async def get_view_shopping_list(callback: CallbackQuery):
    shopping_list_id = callback.data.split('_')[-1]
    products = await get_shopping_list_items(shopping_list_id)
    last_button = {f'shopping_list_{shopping_list_id}': '⬅️ назад'}
    await callback.message.edit_text(await get_shopping_list_title(shopping_list_id),
                                     reply_markup=create_inline_keyboard(1, last_button, **products))


@router.callback_query(F.data.startswith('add_items_'))
async def add_items_to_shopping_list(callback: CallbackQuery, state: FSMContext):
    shopping_list_id = callback.data.split('_')[-1]
    await state.update_data(shopping_list_id=shopping_list_id)
    await state.set_state(ShoppingList.items)
    await callback.message.delete()
    await callback.message.answer(f'Дополняем список {await get_shopping_list_title(shopping_list_id)}',
                                  reply_markup=create_reply_keyboard(width=2,
                                                                     placeholder='Название продукта',
                                                                     **MENU_BUTTONS_NEW_LIST))


@router.callback_query(F.data.startswith('share_shopping_list_'))
async def share_shopping_list(callback: CallbackQuery):
    shopping_list_id = callback.data.split('_')[-1]
    await callback.answer('Делимся списком')
    await callback.message.edit_text('Перешлите следующее сообщение тому с кем хотите поделиться')
    await callback.message.answer(
        f'Перейдите в бота @RoldexProBot и отправьте ему это сообщение для подключения списка покупок\nПодключить список {shopping_list_id}'
    )


@router.message(F.text.startswith(
    'Перейдите в бота @RoldexProBot и отправьте ему это сообщение для подключения списка покупок')
)
async def get_shared_shopping_list(message: Message):
    if message.forward_origin.sender_user.username == 'RoldexProBot':
        shopping_list_id = int(message.text.split(' ')[-1])
        await connect_shopping_list(message.from_user.id, shopping_list_id)
        await message.answer(f'Подключаем список {shopping_list_id}')


@router.callback_query(F.data.startswith('delete_'))
async def delete_shopping_list_by_id(callback: CallbackQuery):
    shopping_list_id = callback.data.split('_')[-1]
    await callback.answer('Подтвердите удаление')
    shopping_list_name = await get_shopping_list_title(shopping_list_id)
    last_buttons = {
        f'confirmed_delete_{shopping_list_id}': '❌ Подтвердить удаление',
        f'shopping_list_{shopping_list_id}': '⬅️ назад'
    }
    await callback.message.edit_text(f'Вы дейсвительно хотите удалить список {shopping_list_name}',
                                     reply_markup=create_inline_keyboard(1, last_buttons))


@router.callback_query(F.data.startswith('confirmed_delete_'))
async def delete_shopping_list_by_id(callback: CallbackQuery):
    shopping_list_id = callback.data.split('_')[-1]
    await delete_shopping_list(shopping_list_id)
    await callback.answer('Список удалён')
    await callback.message.delete()


@router.callback_query(F.data == 'delet_massage')
async def delet_message(callback: CallbackQuery):
    await callback.answer('Сообщение удалено')
    await callback.message.delete()
