import unittest
from app import create_app

class BasicTests(unittest.TestCase):

    def setUp(self) -> None:
        app = create_app()
        app.testing = True
        self.app = app.test_client()

    def test_main(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
