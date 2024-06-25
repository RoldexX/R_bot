from aiogram import Dispatcher
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def create_reply_keyboard(width: int, placeholder: str = '', one_time=False, *args: list[str],
                          **kwargs: dict[str, str]) -> ReplyKeyboardMarkup:
    """ Инициализация пользовательской клавиатуры """

    menu: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    buttons: list[KeyboardButton] = []

    if args:
        for button in args:
            buttons.append(KeyboardButton(text=button))

    if kwargs:
        for key, value in kwargs.items():
            buttons.append(KeyboardButton(text=value))

    menu.row(*buttons, width=width)
    return menu.as_markup(resize_keyboard=True, input_field_placeholder=f'{placeholder}', one_time_keyboard=one_time)


def create_inline_keyboard(width: int, last_button: dict[str, str] = None, *args: list[str],
                           **kwargs: dict[str, str]) -> InlineKeyboardMarkup:
    """ Инициализация клавиатуры сообщения """

    menu: InlineKeyboardBuilder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(text=button, callback_data='0'))

    if kwargs:
        for key, value in kwargs.items():
            buttons.append(InlineKeyboardButton(text=value, callback_data=key))

    if last_button:
        for key, value in last_button.items():
            buttons.append(InlineKeyboardButton(text=value, callback_data=key))

    menu.row(*buttons, width=width)
    return menu.as_markup(resize_keyboard=True)


def create_inline_keyboard_shopping_list_settings(width: int,
                                                  shopping_list_id: str,
                                                  last_button: dict[str, str] = None,
                                                  **kwargs: dict[str, str]) -> InlineKeyboardMarkup:
    """ Инициализация клавиатуры сообщения """

    menu: InlineKeyboardBuilder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    for key, value in kwargs.items():
        buttons.append(InlineKeyboardButton(text=value, callback_data=f'{key}_{shopping_list_id}'))

    if last_button:
        for key, value in last_button.items():
            buttons.append(InlineKeyboardButton(text=value, callback_data=key))

    menu.row(*buttons, width=width)
    return menu.as_markup(resize_keyboard=True)
