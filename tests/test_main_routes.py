import unittest
from app import create_app, db
from app.models import User, Post
from flask import url_for


class MainRoutesTestCase(unittest.TestCase):
    """Test cases for main routes."""

    @classmethod
    def setUpClass(cls):
        """Set up testing environment."""
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()
        db.create_all()

        # Create a test user
        password_hash = 'hashed_password'
        cls.user = User(username='testuser', email='testuser@example.com', password_hash=password_hash)
        db.session.add(cls.user)
        db.session.commit()

        # Log in the test user
        with cls.client.session_transaction() as session:
            session['_user_id'] = cls.user.id

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """Set up test data before each test."""
        # Create a test post
        self.post = Post(title='Test Post', content='Test content', author_id=self.user.id)
        db.session.add(self.post)
        db.session.commit()

    def tearDown(self):
        """Clean up test data after each test."""
        db.session.query(Post).delete()
        db.session.commit()

    def test_home_page_success(self):
        with self.app.test_request_context():
            """Test the home page loads successfully with posts."""
            response = self.client.get(url_for('main.home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post', response.data)  # Check if post title appears on the page

    def test_explore_page_success(self):
        with self.app.test_request_context():
            """Test the explore page loads successfully with posts."""
            response = self.client.get(url_for('main.explore'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post', response.data)  # Check if post title appears on the explore page

    def test_create_post_success(self):
        with self.app.test_request_context():
            """Test creating a new post successfully."""
            response = self.client.post(url_for('main.explore'), data={
                'title': 'New Post',
                'content': 'This is a new post content.'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post created successfully!', response.data)  # Flash message
        self.assertEqual(Post.query.count(), 2)  # Original post + new post

    def test_create_post_invalid_form(self):
        with self.app.test_request_context():
            """Test creating a post with invalid form data."""
            response = self.client.post(url_for('main.explore'), data={
                'title': '',  # Empty title
                'content': ''
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.query.count(), 1)  # No new post added

    def test_explore_page_requires_login(self):
        """Test that the explore page requires login."""
        with self.client.session_transaction() as session:
            session.clear()  # Log out user
        with self.app.test_request_context():
            response = self.client.get(url_for('main.explore'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
