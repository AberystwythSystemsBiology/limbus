_env = {}

with open("/limbus/.env", "r") as infile:
    for line in infile.readlines():
        key, value = line.split("=")
        _env[key] = value.replace("\n", "")

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{user}:{passwd}@db:5432/{db}".format(
    user = _env["POSTGRES_USER"],
    passwd = _env["POSTGRES_PASSWORD"],
    db = _env["POSTGRES_DB"]
)