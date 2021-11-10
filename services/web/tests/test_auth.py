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

import os
import sys

sys.path.append(os.getcwd())
from app import create_app

import json
import unittest

from . import headers


class AuthTests(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app()
        app.testing = True
        self.app = app.test_client()

    def test_auth_home_unauthorised(self):
        response = self.app.get("api/auth", follow_redirects=True)
        self.assertEqual(response.status_code, 417)

    def test_auth_home(self):
        response = self.app.get("api/auth", headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)

    def test_auth_view_user(self):
        response = self.app.get(
            "api/auth/user/1", headers=headers, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)
        self.assertEqual(
            response.json["content"]["email"], "kryten@jupiterminingcorp.co.uk"
        )

    def test_auth_edit_user(self):
        response = self.app.put(
            "api/auth/user/1/edit",
            headers=headers,
            follow_redirects=True,
            json={"first_name": "Kry-ton"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)
        self.assertEqual(response.json["content"]["first_name"], "Kry-ton")

    def test_auth_new_user(self):
        response = self.app.post(
            "api/auth/user/new",
            headers=headers,
            follow_redirects=True,
            json={
                "email": "testing-user@gmail.com",
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
        self.assertEqual(response.json["success"], True)
        self.assertEqual(response.json["content"]["email"], "testing-user@gmail.com")


if __name__ == "__main__":
    unittest.main()
