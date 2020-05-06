import os

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{user}:{passwd}@db:5432/{db}".format(
    user=os.environ["POSTGRES_USER"],
    passwd=os.environ["POSTGRES_PASSWORD"],
    db=os.environ["POSTGRES_DB"],
)

SECRET_KEY = os.environ["SECRET_KEY"]
WTF_CSRF_SECRET_KEY = os.environ["WTF_CSRF_SECRET_KEY"]
DOCUMENT_DIRECTORY = os.environ["DOCUMENT_DIRECTORY"]
