from aiogram import Dispatcher
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def crate_keyboard(width: int, *args: str, **kwargs: str):
    """ Инициализация клавиатуры """

    menu: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    buttons: list[KeyboardButton] = []

    if args:
        for button in args:
            buttons.append(KeyboardButton(text=button))

    if kwargs:
        for key, value in kwargs.items():
            buttons.append(KeyboardButton(text=value))

    menu.row(*buttons, width=width)
    return menu.as_markup(resize_keyboard=True)
