from aiogram.dispatcher.filters.state import State, StatesGroup


### ---___--- ЮЗЕР КЛАССЫ ---___--- ###


class withdrawal_of_balance(StatesGroup):
    withdrawal_amount_state = State()


### ---___--- АДМИН КЛАССЫ ---___--- ###


class receiving_a_message(StatesGroup):
    receiving_message_state = State()


class private_message(StatesGroup):
    id_or_username_state = State()
    private_message_state = State()


class changing_the_balance(StatesGroup):
    id_or_username_state = State()
    change_amount_state = State()
