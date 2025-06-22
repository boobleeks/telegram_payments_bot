from database.models import User
from database.models import Transaction


async def get_or_create_user(tg_id: int, phone: str = None) -> User:
    user, created = await User.get_or_create(
        tg_id=tg_id,
        defaults={"phone_number": phone} if phone else {}
    )
    if phone and not user.phone_number:
        user.phone_number = phone
        await user.save()
    return user

async def create_transaction(user: User, amount: float, tx_type: str, verification_code: str, card_number: str, x_id: int):
    return await Transaction.create(
        user=user,
        amount=amount,
        type=tx_type,
        status='Не выполнен',
        verification_code=verification_code,
        card_number=card_number,
        x_id=x_id
    )


async def update_transaction_status(tx_id: int, new_status: str) -> bool:
    updated_count = await Transaction.filter(id=tx_id).update(status=new_status)
    return updated_count > 0