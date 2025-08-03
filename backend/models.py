from tortoise import fields
from tortoise.models import Model


class Link(Model):
    id = fields.IntField(pk=True)
    original_url = fields.CharField(max_length=255)
    shortened_url = fields.CharField(max_length=100, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

