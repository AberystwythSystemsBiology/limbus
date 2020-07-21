from . import cmd_setup

from ..auth.models import UserAccount
from .. import db

from uuid import uuid4

@cmd_setup.cli.command("create-kryten")
def create_kryton():
    if UserAccount.query.filter_by(email="kryten@jupiterminingcorp.co.uk").first() is None:
        kyrton = UserAccount(
            email="kryten@jupiterminingcorp.co.uk",
            password=uuid4().hex,
            title="MR",
            first_name = "Kryten",
            last_name = "Series 3000",
            is_bot = True,
            is_admin=True
        )

        db.session.add(kyrton)
        db.session.commit()

        print("NOTICE: Kryton created!")
    else:
        print("NOTICE: Kryton already exists...")