# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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

import os
import sys

sys.path.append(os.getcwd())
from app import create_app

import uuid
import unittest

from . import testing_headers


class AuthTests(unittest.TestCase):

    test_user_email_address: str = None

    def setUp(self) -> None:
        app = create_app()
        app.testing = True
        self.app = app.test_client()

    def test_auth_home(self) -> None:
        response = self.app.get(
            "api/auth", headers=testing_headers, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])

    def test_auth_view_user(self) -> None:
        response = self.app.get(
            "api/auth/user/1", headers=testing_headers, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])
        self.assertEqual(
            response.json["content"]["email"], "kryten@jupiterminingcorp.co.uk"
        )

    def test_auth_edit_user(self) -> None:
        response = self.app.put(
            "api/auth/user/1/edit",
            headers=testing_headers,
            follow_redirects=True,
            json={"first_name": "Kry-ton"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["content"]["first_name"], "Kry-ton")

    def test_auth_new_user(self) -> None:

        self.__class__.test_user_email_address = "%s@gmail.com" % (
            uuid.uuid4().hex.upper()[0:6]
        )

        response = self.app.post(
            "api/auth/user/new",
            headers=testing_headers,
            follow_redirects=True,
            json={
                "email": self.__class__.test_user_email_address,
                "title": "MR",
                "first_name": "Test",
                "middle_name": "Ing",
                "last_name": "User",
                "account_type": "BOT",
                "access_control": "BOT",
                "site_id": 1,
                "password": "nonce",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])
        self.assertEqual(
            response.json["content"]["email"], self.__class__.test_user_email_address
        )


if __name__ == "__main__":
    unittest.main()
