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
    #track_packages = db.Column(db.Array(db.String))


class Chat(db.Model):
    __tablename__ = "chats"
    id = db.Column(db.Integer(), unique=True, primary_key=True)
    number_of_everyday_packages = db.Column(db.Integer())
    type = db.Column(db.String())


async def init_db():
    print(f'postgresql://{os.environ.get("POSTGRES_USER", "bot")}:{os.environ.get("POSTGRES_PASSWORD", "localhost")}@{os.environ.get("DB_HOST", "bot")}/{os.environ.get("POSTGRES_DB", "bot")}')
    await db.set_bind(f'postgresql://{os.environ.get("POSTGRES_USER", "bot")}:{os.environ.get("POSTGRES_PASSWORD", "localhost")}@{os.environ.get("DB_HOST", "bot")}/{os.environ.get("POSTGRES_DB", "bot")}')
    await db.gino.create_all()
    return db
