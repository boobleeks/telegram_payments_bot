from aiogram.fsm.state import StatesGroup, State

class UzUserReg(StatesGroup):
    type = State()
    tg_id = State()
    name = State()
    phone = State()
    x_id = State()
    card_number = State()
    amount = State()
    confirm_code = State()
    summary = State()

class RuUserReg(StatesGroup):
    type = State()
    tg_id = State()
    name = State()
    phone = State()
    x_id = State()
    card_number = State()
    amount = State()
    confirm_code = State()
    summary = State()