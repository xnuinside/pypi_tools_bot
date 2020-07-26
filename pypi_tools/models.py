import os
if os.environ.get("GINO_ADMIN"):
    from gino.ext.sanic import Gino
else:
    from gino import Gino

db = Gino()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(), unique=True, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())


class Chat(db.Model):
    __tablename__ = "chats"
    id = db.Column(db.Integer(), unique=True, primary_key=True)
    number_of_everyday_packages = db.Column(db.Integer())
    type = db.Column(db.String())


class MessageHistory(db.Model):
    __tablename__ = "message_history"


class Packages(db.Model):
    __tablename__ = "packages"
    id = db.Column(db.String(), unique=True, primary_key=True)
    downloads = db.Column(db.Integer())
    date = db.Column(db.Date())


async def init_db():
    await db.set_bind(f'postgresql://bot:bot@{os.environ["DB_HOST"]}/bot')
    await db.gino.create_all()
    return db
