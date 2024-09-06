import datetime

from peewee import *
from .Base import BaseModel
from .Color import Color
from script.extra.helper import *


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

    def download_image(self, tmp=None):
        # If no tmp folder is provided, generate a random one
        if tmp is None:
            tmp = generate_random_folder()

        image_url = get_post_url(self.text)
        image_path = os.path.join(tmp, 'downloaded_image.png')

        download_image(image_url, image_path)

        return image_path

    class Meta:
        table_name = 'templates'
