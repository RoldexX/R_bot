from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from asyncio import sleep

from Database import requests
from Keyboards.keyboards import create_reply_keyboard

from Resources.strings_ru import MENU_BUTTONS


router: Router = Router()
keyboard = create_reply_keyboard(2, 'Выберите пункт меню...', **MENU_BUTTONS)


class FSMFillDice(StatesGroup):
    bot_threw_dice = State()


@router.message(CommandStart())
async def start(message: Message):
    """ Обработка команды /start """
    await requests.set_user(message.from_user.id)
    await message.delete()
    await message.answer(f'Привет {message.from_user.full_name}!', reply_markup=keyboard)


@router.message(F.text == MENU_BUTTONS['say_hi'])
async def keyboard_say_hi(message: Message):
    """ Joke """
    await message.answer(f'{message.from_user.full_name} да уже здоровались)')


@router.message(F.text == MENU_BUTTONS['take_cube'])
async def keyboard_take_cube(message: Message, bot: Bot, state: FSMContext):
    """ Бот бросает кубик, сохраняет значение и ожидает броска пользователя """
    bot_dice = (await bot.send_dice(chat_id=message.from_user.id)).dice
    print(bot_dice)
    await state.update_data(bot_dice_value=bot_dice.value)
    await state.set_state(FSMFillDice.bot_threw_dice)


@router.message(StateFilter(FSMFillDice.bot_threw_dice))
async def user_dice(message: Message, state: FSMContext):
    """ Получаем значение кубика пользователя и выводим результат """
    user_dice_value = message.dice.value
    print(user_dice_value)
    bot_dice_value = (await state.get_data())["bot_dice_value"]
    await state.clear()
    await sleep(3)
    if user_dice_value > bot_dice_value:
        await message.answer('Вы выйграли)')
        await message.answer('🎉')
    elif user_dice_value < bot_dice_value:
        await message.answer('Вы проиграли(')
    else:
        await message.answer('Ничья!')


@router.message()
async def user_dice(message: Message):
    """ Обрабатываем отсутствующие комманды """
    await message.answer('У меня нет таких комманд\nМожет список покупок?')
    print(message)
