from peewee import *
from script.extra.config import *

database = MySQLDatabase(
    database_name,
    user='root',
    # password='mysql',
    password='TMFQ40GalqrQfB4fdkNU',
    host='194.26.183.188',
    port=3306,
    charset='utf8mb4',
    collation='utf8mb4_unicode_ci'
)
# database = MySQLDatabase(database_name, user='root', password='TMFQ40GalqrQfB4fdkNU', host='localhost', port=3306)
database.connect()


class BaseModel(Model):
    class Meta:
        database = database
