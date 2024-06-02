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


    def test_sql_injection_upload(self):
        response = self.client.post('/upload', data = {
            'name': 'user@1.com"; drop table user; -- ',
            'category' : 'nature',
            'caption': 'take over',
            'description': 'taking over',
            'file': 'rando.jpeg'
        }, follow_redirects = True)
        assert response.status_code == 200 #Assert to check database if name had drop the table user
    

    def test_sql_injection_signup(self):
        response = self.client.post('/signup', data = {
            'email' : 'user@1.com"; drop table user; -- ',
            'name' : 'SQL Attack',
            'password' : 'sql123'
        }, follow_redirects = True)
        assert response.status_code == 200 #Assert has to check the database to see if the user has drop the table user
    

    def test_sql_injection_login(self):
        response = self.client.post('/login', data = {
            'email' : 'user@1.com"; drop table user; -- ',
            'password' : 'sql123'
        }, follow_redirects = True)
        assert response.status_code == 200 #Assert has to check the database to see if the user has drop the table user
        

    def test_input_validation(self):
        response = self.client.post('/signup', data={
            'email': 'invalid-email',
            'name': '<script>alert("XSS Attack")</script>',
            'password': 'XSS'
        }, follow_redirects=True)
        assert response.status_code == 200 #Assert has to check if the alert is displayed on the page
        

    #Test for seesion fication is needed where the session id is changed every time the user logs into their account
    #Test for CSRF token is needed where the CSRF token is checked to ensure that the user is not a bot
    #Test for session timeout is needed where the session is timed out after a certain amount of time
    


    def test_sql_injection_search(self):
        response = self.client.post('/', data = {
            'search' : 'Berlin"; drop table user; -- ',
        }, follow_redirects = True)
        assert response.status_code == 200


    def test_xss_attack_search(self):
        response = self.client.post('/', data={
            'search': '<script>alert("XSS Attack")</script>',
        }, follow_redirects=True)
        assert response.status_code == 200 #Assert has to check if the alert is displayed on the page


    def test_failing_securely_search(self):
        response = self.client.post('/', data={
            'search': 'Testabcdefghy',
        }, follow_redirects=True)
        # code to check that text on screen includes "No results for the search \"Testabcdefghy"" goes here
        assert response.status_code == 200 #Assert has to check if the alert is displayed on the page


    def test_sql_injection_categories(self):
        response = self.client.post('/Nature', data={}, follow_redirects=True)
        # Code to test for SQL Injection goes here - this would include drop table user; -- 
        assert response.status_code == 200


    def test_xss_attack_categories(self):
        response = self.client.post('/Animals')
        # Code to test for XSS attacks goes here - this would include <script>alert("XSS Attack")</script>
        assert response.status_code == 200
    
    
    def test_failing_securely_categories(self):
        response = self.client.post('/Other')
        # Code to test that text on screen includes "No photos in category \"Other"" goes here
        assert response.status_code == 200


        



     