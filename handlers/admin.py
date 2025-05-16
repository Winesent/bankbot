from decimal import Decimal, InvalidOperation
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.balance import BalanceService
from keyboards.main import admin_keyboard, main_keyboard, cancel_keyboard
from config import Config

router = Router()


class AdminStates(StatesGroup):
    admin_action = State()
    admin_username = State()
    admin_amount = State()


async def is_admin(user_id: int) -> bool:
    return user_id in Config.ADMIN_IDS


@router.message(F.text == "👑 Админ-панель")
async def admin_panel(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к админ-панели")
        return

    await message.answer("Админ-панель", reply_markup=admin_keyboard())


@router.message(F.text == "◀️ Назад")
async def back_to_main(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("Главное меню", reply_markup=main_keyboard())
        return

    await message.answer("Главное меню", reply_markup=main_keyboard())


@router.message(F.text.in_(["Начислить", "Списать", "Проверить баланс"]))
async def admin_action(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой функции")
        return

    await state.update_data(action=message.text)
    await state.set_state(AdminStates.admin_username)
    await message.answer("Введите @username пользователя:", reply_markup=cancel_keyboard())


@router.message(AdminStates.admin_username)
async def admin_process_username(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await state.clear()
        await message.answer("Доступ запрещен", reply_markup=main_keyboard())
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Действие отменено", reply_markup=admin_keyboard())
        return

    username = message.text.lstrip('@')
    if not username:
        await message.answer("Пожалуйста, введите @username пользователя:")
        return

    data = await state.get_data()
    action = data['action']

    if action == "Проверить баланс":
        user = BalanceService.get_user_by_username(username)
        if not user:
            await message.answer(f"Пользователь @{username} не найден")
        else:
            await message.answer(f"💰 Баланс @{username}: {user.balance}")
        await state.clear()
        return

    await state.update_data(username=username)
    await state.set_state(AdminStates.admin_amount)
    await message.answer("Введите сумму:")


@router.message(AdminStates.admin_amount)
async def admin_process_amount(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await state.clear()
        await message.answer("Доступ запрещен", reply_markup=main_keyboard())
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Действие отменено", reply_markup=admin_keyboard())
        return

    try:
        amount = Decimal(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except (InvalidOperation, ValueError):
        await message.answer("Пожалуйста, введите корректную сумму (например: 100 или 50.5):")
        return

    data = await state.get_data()
    action = data['action']
    username = data['username']

    try:
        if action == "Начислить":
            user = BalanceService.admin_update_balance(username, amount)
            await message.answer(
                f"✅ Баланс @{username} пополнен на {amount}\n"
                f"💰 Новый баланс: {user.balance}",
                reply_markup=admin_keyboard()
            )
        elif action == "Списать":
            user = BalanceService.admin_update_balance(username, -amount)
            await message.answer(
                f"✅ С @{username} списано {amount}\n"
                f"💰 Новый баланс: {user.balance}",
                reply_markup=admin_keyboard()
            )
    except ValueError as e:
        await message.answer(f"❌ Ошибка: {e}")

    await state.clear()