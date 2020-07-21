from . import cmd_setup

from ..auth.models import UserAccount
from .. import db

from uuid import uuid4

@cmd_setup.cli.command("create-kryton")
def create_kryton():
    if UserAccount.query.filter_by(email="kryton@jupiterminingcorp.co.uk").first() is None:
        kyrton = UserAccount(
            username="kryton@jupiterminingcorp.co.uk",
            password=uuid4().hex,
            is_admin=True
        )

        db.session.add(kyrton)
        db.session.commit()

        print("NOTICE: Kryton created!")
    else:
        print("NOTICE: Kryton already exists...")