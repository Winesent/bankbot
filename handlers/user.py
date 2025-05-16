from decimal import Decimal, InvalidOperation
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import Config
from services.balance import BalanceService
from keyboards.main import main_keyboard, cancel_keyboard

router = Router()

class TransferStates(StatesGroup):
    enter_username = State()
    enter_amount = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = BalanceService.get_or_create_user(message.from_user.id, message.from_user.username)
    is_admin = message.from_user.id in Config.ADMIN_IDS
    await message.answer(
        f"👋 Добро пожаловать в финансовый бот!\n"
        f"💰 Ваш баланс: {user.balance}",
        reply_markup=main_keyboard(is_admin)
    )

@router.message(F.text == "💰 Баланс")
async def check_balance(message: Message):
    user = BalanceService.get_or_create_user(message.from_user.id, message.from_user.username)
    await message.answer(f"💰 Ваш баланс: {user.balance}")

@router.message(F.text == "💸 Перевести")
async def start_transfer(message: Message, state: FSMContext):
    await state.set_state(TransferStates.enter_username)
    await message.answer(
        "Введите @username получателя:",
        reply_markup=cancel_keyboard()
    )

@router.message(TransferStates.enter_username)
async def process_username(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Перевод отменен", reply_markup=main_keyboard())
        return

    username = message.text.lstrip('@')
    if not username:
        await message.answer("Пожалуйста, введите @username получателя:")
        return

    await state.update_data(username=username)
    await state.set_state(TransferStates.enter_amount)
    await message.answer("Введите сумму для перевода:")

@router.message(TransferStates.enter_amount)
async def process_amount(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Перевод отменен", reply_markup=main_keyboard())
        return

    try:
        amount = Decimal(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError("Сумма должна быть положительна")
    except (InvalidOperation, ValueError):
        await message.answer("Пожалуйста, введите корректную сумму (например: 100 или 50.5):")
        return

    data = await state.get_data()
    username = data['username']

    try:
        sender, recipient = BalanceService.transfer(
            from_user_id=message.from_user.id,
            to_username=username,
            amount=amount
        )
        await message.answer(
            f"✅ Перевод выполнен!\n"
            f"💸 Сумма: {amount}\n"
            f"👤 Получатель: @{recipient.username}\n"
            f"💰 Ваш новый баланс: {sender.balance}",
            reply_markup=main_keyboard()
        )
    except ValueError as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        await state.clear()