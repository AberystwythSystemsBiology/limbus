from . import cmd_setup

from ..auth.models import UserAccount, UserAccountToken
from .. import db

from uuid import uuid4


@cmd_setup.cli.command("create-kryten")
def create_kryton():
    """

    :return:
    """
    if (
        UserAccount.query.filter_by(email="kryten@jupiterminingcorp.co.uk").first()
        is None
    ):
        kryten = UserAccount(
            email="kryten@jupiterminingcorp.co.uk",
            password=uuid4().hex,
            title="MR",
            first_name="Kryten",
            last_name="Series 3000",
            account_type="BOT",
            access_control="BOT",
        )

        db.session.add(kryten)
        db.session.flush()

        kryten_token = UserAccountToken(user_id=kryten.id, token=uuid4().hex)

        db.session.add(kryten_token)
        db.session.commit()

        print("NOTICE: Kryton created!")
    else:
        print("NOTICE: Kryton already exists...")
