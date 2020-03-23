from app import create_app, db
from app.auth.models import User

create_app()



import pandas as pd

df = {n: d for n,d in pd.read_excel("/limbus/testdata.ods", engine="odf", sheet_name=None).items()}

def add_users():
    if len(db.session.query(User).all()) == 0:
        u_data = df["User"]
        p_data = df["Profile"]
        a_data = df["Address"]
        pta_da = df["ProfileToAddress"]

        print(u_data)

add_users()


