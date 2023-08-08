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

from ..database import db, UserAccount, UserAccountToken, Address, SiteInformation

from uuid import uuid4

import random
import string


@cmd_setup.cli.command("create-kryten")
def create_kryten():
    kryten_ascii = """             _--~~--_
"Smeee-     |\      /|
 Heeee!"    | \    / |
           i.--`..'--.i
           \\~* || *~//  
            |\^([])^/|
            '.(-__-).'
             |`.__.'|
     .-~\____`------'____/~-.
    / _-~MMMM`------'MMMM~-_ \
   'T~MMMM/##--_.._--##\MMMM~T'
   |\MMMM/%%%%%%||%%%%%%\MMMM/|
   |=|MM|`:%%%%%||%%%%%;'|MM|=|
   |=|MM|\ `.===!!===.' /|MM|=|
   |=|MM||W\   _--_   /W||MM|=|   
   |/MMM||WW|,'_--_`.|WW||MMM\|
    |MMM||WW/.'    `.\WW||MMM|
   |\MMM||WW||      ||WW||MMM/|
   |=|MM||WW\`.    ,'/WW||MM|=|
   |/MMM||WWW`.~--~,'WWW||MMM\| 
    `:;;'\WWWWW~--~WWWWW/`:;;'
    | U '.`------------',' U |
    i111\J L ]|   | L ] L/|||i
    U111 | ~--_L____--~ | |||U
     UJJ |MMMMMM/\MMMMMM| UJJ
        |\MM"""

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

        print("NOTICE: Kryten created!\n %s" % (kryten_ascii))
    else:
        print("NOTICE: Kryten already exists. Not going to add.")


@cmd_setup.cli.command("create-testuser")
def create_testuser():
    address = Address(
        street_address_one="32 Charles Street",
        street_address_two="Abertysswg",
        city="Tredegar",
        county="Rhondda Cynon Taff",
        post_code="NP225AZ",
        country="GB",
    )

    db.session.add(address)
    db.session.commit()
    db.session.flush()

    site = SiteInformation(
        name="Testing Biobank",
        address_id=address.id,
        author_id=UserAccount.query.filter_by(email="kryten@jupiterminingcorp.co.uk")
        .first()
        .id,
    )

    db.session.add(site)
    db.session.commit()
    db.session.flush()

    generated_password = "".join(random.choice(string.printable) for i in range(15))

    me = UserAccount(
        email="me@domain.com",
        password=generated_password,
        title="MR",
        first_name="Joe",
        last_name="Bloggs",
        account_type="ADM",
        access_control="ADM",
        site_id=site.id,
    )

    db.session.add(me)
    db.session.commit()

    uat = UserAccountToken(user_id=me.id, token="testing-token-please-change")
    db.session.add(uat)
    db.session.commit()

    print("Created the testing/development user.")
    print(
        "You can log in using the following credentials:\nEmail: me@domain.com\nPassword: %s"
        % (generated_password)
    )
