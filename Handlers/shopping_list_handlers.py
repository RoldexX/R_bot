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
                               get_shopping_list_items_with_check,
                               get_shopping_list_items_with_delete_state,
                               get_shopping_list_ig_by_product_id,
                               edit_product_check,
                               edit_product_delete_status,
                               delete_shopping_list,
                               connect_shopping_list,
                               get_product_title_by_id,
                               set_new_product_title,
                               delete_selected_product)
from Keyboards.keyboards import (create_inline_keyboard,
                                 create_reply_keyboard,
                                 create_inline_keyboard_shopping_list_settings)
from Resources.strings_ru import (MENU_BUTTONS,
                                  MENU_BUTTONS_NEW_LIST,
                                  VIEW_SHOPPING_LIST_BUTTONS,
                                  SHOPPING_LIST_BUTTONS,
                                  SHOPPING_LIST_EDIT_BUTTONS)

router: Router = Router()
keyboard = create_reply_keyboard(2, 'Выберите пункт меню...', **MENU_BUTTONS)


class ShoppingList(StatesGroup):
    select_list = State()
    title = State()
    items = State()
    edit_item = State()


@router.message(F.text == MENU_BUTTONS['shopping_list'])
async def shopping_list(message: Message):
    """ Обработка запроса на вывод всех списков прикреплённых в текущему пользователю """
    shopping_lists: dict[str, str] = await get_shopping_lists(message.from_user.id)
    await message.answer(text='Ваши списки покупок',
                         reply_markup=create_inline_keyboard(2, VIEW_SHOPPING_LIST_BUTTONS, **shopping_lists))


@router.callback_query(F.data == 'create_list')
async def new_shopping_list(callback: CallbackQuery, state: FSMContext):
    """ Обработка запроса на создание нового списка покупок и запрос названия будущего списка """
    await state.set_state(ShoppingList.title)
    await callback.answer('Новый список покупок')
    await callback.message.answer('Введите название списка покупок')


@router.message(StateFilter(ShoppingList.title))
async def shopping_list(message: Message, state: FSMContext):
    """ Создание списка с полученным именем и переход к добавлению позиций """
    shopping_list_id = await create_shopping_list(tg_id=message.from_user.id,
                                                  title=message.text)
    await state.update_data(shopping_list_id=shopping_list_id)
    await state.set_state(ShoppingList.items)
    await message.answer(f'Создан список {message.text}\n'
                         f'Теперь вводите названия продуктов по одному, либо отделяя их переносом на новую строку',
                         reply_markup=create_reply_keyboard(width=2,
                                                            placeholder='Название продукта',
                                                            **MENU_BUTTONS_NEW_LIST))


@router.message(StateFilter(ShoppingList.items))
async def add_items_to_shopping_list(message: Message, state: FSMContext):
    """ Добавление позиций в список покупок """
    if message.text == MENU_BUTTONS_NEW_LIST['get_list']:
        shopping_list_id = (await state.get_data())['shopping_list_id']
        products = await get_shopping_list_items_with_check(int(shopping_list_id))
        last_button = {'delet_massage': '❌ закрыть'}
        await message.answer(await get_shopping_list_title(int(shopping_list_id)),
                             reply_markup=create_inline_keyboard(1, last_button,
                                                                 **products))

    elif message.text != MENU_BUTTONS_NEW_LIST['exit']:
        if message.text != None:
            shopping_list_id = (await state.get_data())['shopping_list_id']
            items = message.text.split('\n')
            for item in items:
                await add_product(int(shopping_list_id), item)
        else:
            await message.answer('Названия продуктов принимаются только текстом!')
    else:
        await state.clear()
        await message.answer('Хорошо, сохранил ваши продукты', reply_markup=keyboard)


@router.callback_query(F.data.startswith('product_'))
async def edit_check_product(callback: CallbackQuery):
    """ Изменение состояния продукта """
    product_id = callback.data.split('_')[-1]
    shopping_list_id = await get_shopping_list_ig_by_product_id(int(product_id))
    await edit_product_check(int(product_id))
    products = await get_shopping_list_items_with_check(int(shopping_list_id))
    await callback.answer('отмечен')
    last_button = {'delet_massage': '❌ закрыть'}
    await callback.message.edit_reply_markup(reply_markup=create_inline_keyboard(1,
                                                                                 last_button,
                                                                                 **products))


@router.callback_query(F.data.startswith('shopping_list_'))
async def shopping_list_callback(callback: CallbackQuery, state: FSMContext):
    """ Вызов меню работы со списком продуктов """
    shopping_list_id = callback.data.split('_')[-1]
    await callback.answer(callback.data)
    last_button = {'delet_massage': '❌ закрыть'}
    await callback.message.edit_text(await get_shopping_list_title(int(shopping_list_id)),
                                     reply_markup=create_inline_keyboard_shopping_list_settings(
                                         2,
                                         shopping_list_id,
                                         last_button,
                                         **SHOPPING_LIST_BUTTONS))


@router.callback_query(F.data.startswith('get_view_'))
async def get_view_shopping_list(callback: CallbackQuery):
    """ Вывод продуктов текущего спика покупок """
    shopping_list_id = callback.data.split('_')[-1]
    products = await get_shopping_list_items_with_check(int(shopping_list_id))
    last_button = {f'shopping_list_{shopping_list_id}': '⬅️ назад'}
    await callback.message.edit_text(await get_shopping_list_title(int(shopping_list_id)),
                                     reply_markup=create_inline_keyboard(1, last_button, **products))


@router.callback_query(F.data.startswith('add_items_'))
async def add_items_to_shopping_list(callback: CallbackQuery, state: FSMContext):
    """ Переход к добавлению продуктов в текущий список покупок """
    shopping_list_id = callback.data.split('_')[-1]
    await state.update_data(shopping_list_id=shopping_list_id)
    await state.set_state(ShoppingList.items)
    await callback.answer('Дополняем список')
    await callback.message.delete()
    await callback.message.answer(f'Дополняем список {await get_shopping_list_title(int(shopping_list_id))}\n'
                                  f'Теперь вводите названия продуктов по одному, '
                                  f'либо отделяя их переносом на новую строку',
                                  reply_markup=create_reply_keyboard(width=2,
                                                                     placeholder='Название продукта',
                                                                     **MENU_BUTTONS_NEW_LIST))


@router.callback_query(F.data.startswith('share_shopping_list_'))
async def share_shopping_list(callback: CallbackQuery):
    """ Формированние сообщения для подключения списка другому пользователю """
    shopping_list_id = callback.data.split('_')[-1]
    await callback.answer('Делимся списком')
    await callback.message.edit_text('Перешлите следующее сообщение тому с кем хотите поделиться')
    await callback.message.answer(
        f'Перейдите в бота @RoldexProBot и отправьте ему это сообщение для подключения списка покупок\n'
        f'Подключить список {shopping_list_id}'
    )


@router.message(F.text.startswith(
    'Перейдите в бота @RoldexProBot и отправьте ему это сообщение для подключения списка покупок')
)
async def get_shared_shopping_list(message: Message):
    """ Подключение списка покупок любого пользователя, текущему пользователю """
    if message.forward_origin.sender_user.username == 'RoldexProBot':
        shopping_list_id = int(message.text.split(' ')[-1])
        await connect_shopping_list(message.from_user.id, shopping_list_id)

        shopping_list_name = await get_shopping_list_title(int(shopping_list_id))
        await message.answer(f'Вам подлючён список\n{shopping_list_name}')


@router.callback_query(F.data.startswith('delete_'))
async def delete_shopping_list_by_id(callback: CallbackQuery):
    """ Запрос подтверждения открепления списка у текущего пользователя """
    shopping_list_id = callback.data.split('_')[-1]
    await callback.answer('Подтвердите удаление')
    shopping_list_name = await get_shopping_list_title(int(shopping_list_id))
    last_buttons = {
        f'confirmed_delete_{shopping_list_id}': '✅ Подтвердить удаление',
        f'shopping_list_{shopping_list_id}': '⬅️ назад'
    }
    await callback.message.edit_text(f'Вы дейсвительно хотите удалить список\n{shopping_list_name}',
                                     reply_markup=create_inline_keyboard(1, last_buttons))


@router.callback_query(F.data.startswith('confirmed_delete_'))
async def delete_shopping_list_by_id(callback: CallbackQuery):
    """ Открепление текущего списка покупок от текущего пользователя """
    shopping_list_id = int(callback.data.split('_')[-1])
    user_tg_id = int(callback.from_user.id)
    print(user_tg_id)
    await delete_shopping_list(shopping_list_id, user_tg_id)
    await callback.answer('Список удалён')
    await callback.message.delete()


@router.callback_query(F.data == 'delet_massage')
async def delet_message(callback: CallbackQuery):
    """ Удаление текущего сообщения """
    await callback.answer('Сообщение удалено')
    await callback.message.delete()


@router.callback_query(F.data.startswith('edit_items_'))
async def get_keyboard_edit_shopping_list_items(callback: CallbackQuery):
    """ Вывод клавиатуры для выбора вида редактирования списка """
    shopping_list_id = callback.data.split('_')[-1]
    last_button = {f'shopping_list_{shopping_list_id}': '⬅️ назад'}
    shopping_list_name = await get_shopping_list_title(int(shopping_list_id))
    await callback.answer('Выбор вида изменения позиций спика')
    await callback.message.edit_text(f'Как вы хотите изменить список\n{shopping_list_name}',
                                     reply_markup=create_inline_keyboard_shopping_list_settings(
                                         1,
                                         shopping_list_id,
                                         last_button,
                                         **SHOPPING_LIST_EDIT_BUTTONS))


@router.callback_query(F.data.startswith('rename_items_'))
async def select_shopping_list_items_for_edit(callback: CallbackQuery):
    """ Вывод всех продуктов списка для выбора редактируемого """
    shopping_list_id = callback.data.split('_')[-1]
    products_for_edit = await get_shopping_list_items(int(shopping_list_id), 'edit_')
    last_button = {f'edit_items_{shopping_list_id}': '⬅️ назад'}
    await callback.answer('Выбор продукта')
    await callback.message.edit_text('Выберите продукт, наименование которого хотите изменить',
                                     reply_markup=create_inline_keyboard(1, last_button, **products_for_edit))


@router.callback_query(F.data.startswith('edit_product_'))
async def edit_shopping_list_item(callback: CallbackQuery, state: FSMContext):
    """ Переход к состоянию ожидания нового названия продукта """
    product_id = callback.data.split('_')[-1]
    product_title = await get_product_title_by_id(int(product_id))
    await state.update_data(edit_product_id=product_id)
    await state.set_state(ShoppingList.edit_item)
    await callback.answer(f'Редактируем продукт {product_title}')
    await callback.message.edit_text(f'Сейчас продукт называется: {product_title}\n'
                                     f'Введите новое название для этого продукта')


@router.message(StateFilter(ShoppingList.edit_item))
async def get_new_product_title(message: Message, state: FSMContext):
    """ Получение нового названия и обновление названия текущего продукта """
    product_id = (await state.get_data())['edit_product_id']
    product_title_new = message.text
    await set_new_product_title(int(product_id), product_title_new)
    await state.clear()
    shopping_list_id = await get_shopping_list_ig_by_product_id(int(product_id))
    last_buttons = {
        f'rename_items_{shopping_list_id}': 'Продолжить редактировать продукты',
        f'shopping_list_{shopping_list_id}': 'Вернуться к настройкам списка',
        'delet_massage': '❌ закрыть'
    }
    await message.answer(f'Название продукта изменено на: {product_title_new}',
                         reply_markup=create_inline_keyboard(1, last_buttons))


@router.callback_query(F.data.startswith('del_items_'))
async def get_shopping_list_items_for_delete(callback: CallbackQuery):
    """ Вывод всех продуктов списка для выбора удаляемых позоций """
    shopping_list_id = callback.data.split('_')[-1]
    products_for_delete = await get_shopping_list_items(int(shopping_list_id), 'select_item_for_del_')
    await callback.answer('Выберите продукты которые необходимо удалить')
    last_button = {f'edit_items_{shopping_list_id}': '⬅️ назад'}
    await callback.message.edit_text('Выберите продукты которые необходимо удалить',
                                     reply_markup=create_inline_keyboard(1, last_button, **products_for_delete))


@router.callback_query(F.data.startswith('select_item_for_del_product_'))
async def select_shopping_list_items_for_delete(callback: CallbackQuery):
    """ Вывод продуктов выбранных к удалению до тех под пока удаление не будет подтверждено  """
    selected_product_id = callback.data.split('_')[-1]
    shopping_list_id = await get_shopping_list_ig_by_product_id(int(selected_product_id))
    await edit_product_delete_status(int(selected_product_id))
    products_for_delete = await get_shopping_list_items_with_delete_state(int(shopping_list_id))
    await callback.answer(callback.data)
    last_button = {f'confirmed_select_items_{shopping_list_id}': '✅ подтвердить удаление'}
    await callback.message.edit_reply_markup(reply_markup=create_inline_keyboard(1,
                                                                                 last_button,
                                                                                 **products_for_delete))


@router.callback_query(F.data.startswith('confirmed_select_items_'))
async def confirmed_selected_shopping_list_items_for_delete(callback: CallbackQuery):
    """ Удаление отмеченных элементов """
    shopping_list_id = callback.data.split('_')[-1]
    await callback.answer('Удаляем выбранные элементы')
    await delete_selected_product(int(shopping_list_id))
    last_buttons = {
        f'del_items_{shopping_list_id}': 'Удалить ещё что-нибудь',
        f'shopping_list_{shopping_list_id}': 'Вернуться к настройкам списка',
        'delet_massage': '❌ закрыть'
    }
    await callback.message.edit_text('Выбранные элементы удалены',
                                     reply_markup=create_inline_keyboard(1, last_buttons))
