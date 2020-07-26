import os

from gino_admin import create_admin_app

os.environ["GINO_ADMIN"] = "1"

# gino admin uses Sanic as a framework, so you can define most params as environment variables with 'SANIC_' prefix
# in example used this way to define DB credentials & login-password to admin panel

os.environ["SANIC_DB_HOST"] = os.getenv("DB_HOST", "localhost")
os.environ["SANIC_DB_DATABASE"] = "bot"
os.environ["SANIC_DB_USER"] = "bot"
os.environ["SANIC_DB_PASSWORD"] = "bot"


os.environ["SANIC_ADMIN_USER"] = "admin"
os.environ["SANIC_ADMIN_PASSWORD"] = "1234"

current_path = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    import models  # noqa E402

    create_admin_app(
        host="0.0.0.0",
        port=os.getenv("PORT", 5555),
        db=models.db,
        db_models=[models.User, models.Chat]
    )
