from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


@router.message(Command(commands=["start", "help"]))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await message.answer(f"Привет, {message.from_user.full_name}!")
