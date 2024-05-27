import unittest
from flask import current_app
from project import create_app, db
from project.models import User
from werkzeug.security import check_password_hash

class Test(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": 'sqlite://'} )
        self.app.config['WTF_CSRF_ENABLED'] = False  # no CSRF during tests
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None

    def test_app(self):
        assert self.app is not None
        assert current_app == self.app

    def test_sql_injection_signup(self):
        response = self.client.post('/signup', data = {
            'email' : 'user@1.com"; drop table user; -- ',
            'name' : 'SQL Attack',
            'password' : 'sql123'
        }, follow_redirects = True)
        assert response.status_code == 200

    def test_sql_injection_login(self):
        response = self.client.post('/login', data = {
            'email' : 'user@1.com"; drop table user; -- ',
            'password' : 'sql123'
        }, follow_redirects = True)
        assert response.status_code == 200

    def test_sql_injection_search(self):
        response = self.client.post('/', data = {
            'search' : 'Berlin"; drop table user; -- ',
        }, follow_redirects = True)
        assert response.status_code == 200

        



     