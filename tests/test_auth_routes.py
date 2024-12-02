import unittest
from app import create_app, db, bcrypt
from app.models import User
from flask import url_for


class AuthTestCase(unittest.TestCase):
    """Test case for authentication routes."""

    @classmethod
    def setUpClass(cls):
        """Set up the testing environment."""
        cls.app = create_app('testing')  # Use the testing configuration
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """Set up data before each test."""
        self.user_password = 'password123'
        self.user = User(
            username='testuser',
            email='testuser@example.com',
            password_hash=bcrypt.generate_password_hash(self.user_password).decode('utf-8')
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        """Clean up data after each test."""
        db.session.query(User).delete()
        db.session.commit()

    def test_register_get(self):
        with self.app.test_request_context():
            """Test the GET request for the register route."""
            response = self.client.get(url_for('auth.register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)  # Check for page content

    def test_register_post_success(self):
        with self.app.test_request_context():
            """Test the POST request for the register route with valid data."""
            response = self.client.post(url_for('auth.register'), data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been created!', response.data)  # Flash message
        self.assertIsNotNone(User.query.filter_by(email='newuser@example.com').first())

    def test_register_post_failure(self):
        with self.app.test_request_context():
            """Test the POST request for the register route with invalid data."""
            response = self.client.post(url_for('auth.register'), data={
                'username': '',
                'email': 'invalidemail',
                'password': '123',
                'confirm_password': '456'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'This field is required.', response.data)  # Validation error
        self.assertIsNone(User.query.filter_by(email='invalidemail').first())

    def test_login_get(self):
        with self.app.test_request_context():
            """Test the GET request for the login route."""
            response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)  # Check for page content

    def test_login_post_success(self):
        with self.app.test_request_context():
            """Test the POST request for the login route with valid credentials."""
            response = self.client.post(url_for('auth.login'), data={
                'email': self.user.email,
                'password': self.user_password
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged in!', response.data)  # Flash message

    def test_login_post_failure(self):
        with self.app.test_request_context():
            """Test the POST request for the login route with invalid credentials."""
            response = self.client.post(url_for('auth.login'), data={
                'email': 'wrong@example.com',
                'password': 'wrongpassword'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login unsuccessful. Please check email and password.', response.data)  # Flash message

    def test_logout(self):
        with self.app.test_request_context():
            """Test the logout route."""
            # Log in the user first
            self.client.post(url_for('auth.login'), data={
                'email': self.user.email,
                'password': self.user_password
            }, follow_redirects=True)
        with self.app.test_request_context():
            # Log out
            response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out.', response.data)  # Flash message
