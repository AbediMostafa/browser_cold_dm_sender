import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account


class Color(BaseModel):
    title = CharField()
    is_used = SmallIntegerField(default=0)

    class Meta:
        table_name = 'colors'
