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
import unittest

sys.path.append(os.getcwd())
from app import create_app

from . import testing_headers


class DocumentTests(unittest.TestCase):
    doc_id: int = 1

    def setUp(self) -> None:
        app = create_app()
        app.testing = True
        self.app = app.test_client()

    def test_01_document_home(self):
        response = self.app.get(
            "api/document", headers=testing_headers, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])

    def test_02_document_new_document(self):
        response = self.app.post(
            "api/document/new",
            headers=testing_headers,
            follow_redirects=True,
            json={
                "name": "Testing Document",
                "description": "Testing document, for testing purposes.",
                "type": "OTHER",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["content"]["name"], "Testing Document")
        self.__class__.doc_id = response.json["content"]["id"]

    def test_03_document_view_document(self):
        response = self.app.get(
            "api/document/LIMBDOC-%s" % (self.__class__.doc_id),
            headers=testing_headers,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["content"]["name"], "Testing Document")

    def test_04_document_query(self):
        response = self.app.get(
            "api/document/LIMBDOC-%s" % (self.__class__.doc_id),
            json={"name": "Testing Document"},
            headers=testing_headers,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])

    def test_05_document_edit_document(self):
        edit_name: str = "Testing Document, Edited"

        response = self.app.put(
            "api/document/LIMBDOC-%s/edit" % (self.__class__.doc_id),
            json={"name": edit_name},
            headers=testing_headers,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["content"]["name"], edit_name)

    def test_06_document_lock_document(self):
        # Lock the document
        response = self.app.put(
            "api/document/LIMBDOC-%s/lock" % (self.__class__.doc_id),
            headers=testing_headers,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)
        self.assertEqual(response.json["content"]["is_locked"], True)

        # Unlock the document
        response = self.app.put(
            "api/document/LIMBDOC-%s/lock" % (self.__class__.doc_id),
            headers=testing_headers,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)
        self.assertEqual(response.json["content"]["is_locked"], False)


if __name__ == "__main__":
    unittest.main()
