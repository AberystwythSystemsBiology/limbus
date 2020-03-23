from app import create_app, db
from app.auth.models import User

create_app()



import pandas as pd


def add_users():
    if len(db.session.query(User).all()) == 0:
        u_data = df["User"]
        p_data = df["Profile"]
        a_data = df["Address"]
        pta_da = df["ProfileToAddress"]

        print(u_data)

add_users()


