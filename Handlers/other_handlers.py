from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State,StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from asyncio import sleep

from Keyboards.keyboards import crate_keyboard

from Resources.strings_ru import MENU_BUTTONS


router: Router = Router()
keyboard = crate_keyboard(2, **MENU_BUTTONS)


class FSMFillDice(StatesGroup):
    bot_threw_dice = State()


@router.message(CommandStart())
async def start(message: Message):
    await message.delete()
    await message.answer(f'Привет {message.from_user.full_name}!', reply_markup=keyboard)


@router.message(F.text == MENU_BUTTONS['say_hi'])
async def keyboard_say_hi(message: Message):
    await message.answer(f'{message.from_user.full_name} да уже здоровались)')


@router.message(F.text == MENU_BUTTONS['take_cube'])
async def keyboard_take_cube(message: Message, bot: Bot, state: FSMContext):
    bot_dice = (await bot.send_dice(chat_id=message.from_user.id)).dice
    print(bot_dice)
    await state.update_data(bot_dice_value=bot_dice.value)
    await state.set_state(FSMFillDice.bot_threw_dice)


@router.message(StateFilter(FSMFillDice.bot_threw_dice))
async def user_dice(message: Message, state: FSMContext):
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
    print(message)
