import datetime

from peewee import *
from .Base import BaseModel
from .Color import Color



def delete(_type, text):
    return Template.delete().where(
        (Template.type == _type) & (Template.text == text)
    ).execute()


def get_a(_type):
    return Template.select().where(Template.type == _type).first()


class Template(BaseModel):
    text = CharField()
    caption = CharField()
    type = CharField()
    carousel_id = CharField(null=True)
    uid = CharField(null=True)
    color = ForeignKeyField(Color, backref='templates', null=True)

    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    class Meta:
        table_name = 'templates'
