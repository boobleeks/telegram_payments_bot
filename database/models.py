from tortoise import fields
from tortoise.models import Model

class User(Model):
    payment_id = fields.IntField(pk=True)
    tg_id = fields.BigIntField(unique=True)
    phone_number = fields.CharField(max_length=20) 
    created_at = fields.DatetimeField(auto_now_add=True)

class Transaction(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="transactions")
    card_number = fields.CharField(max_length=20)
    amount = fields.IntField(default=0)
    x_id = fields.BigIntField()
    verification_code = fields.TextField()
    type = fields.CharField(max_length=10)
    status = fields.CharField(max_length=20, default="pending")
    created_at = fields.DatetimeField(auto_now_add=True)
                



