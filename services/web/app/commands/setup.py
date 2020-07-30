# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
