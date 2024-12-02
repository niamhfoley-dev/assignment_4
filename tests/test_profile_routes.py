import unittest
from flask import url_for, jsonify
from app import create_app, db
from app.models import User, Post, Follow


class ProfileRoutesTestCase(unittest.TestCase):
    """Test cases for profile routes."""

    @classmethod
    def setUpClass(cls):
        """Set up testing environment."""
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()
        db.create_all()

        # Create test users
        password_hash = 'hashed_password'
        cls.user1 = User(username='testuser1', email='testuser1@example.com', password_hash=password_hash)
        db.session.add(cls.user1)

        password_hash = 'hashed_password'
        cls.user2 = User(username='testuser2', email='testuser2@example.com', password_hash=password_hash)
        db.session.add(cls.user2)

        db.session.commit()

        # Log in as user1
        with cls.client.session_transaction() as session:
            session['_user_id'] = cls.user1.id

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """Set up test data before each test."""
        self.post1 = Post(title='User1 Post', content='Content by user1', author_id=self.user1.id)
        self.post2 = Post(title='User2 Post', content='Content by user2', author_id=self.user2.id)
        db.session.add_all([self.post1, self.post2])
        db.session.commit()

    def tearDown(self):
        """Clean up test data after each test."""
        db.session.query(Post).delete()
        db.session.query(Follow).delete()
        db.session.commit()

    def test_user_profile_own_profile(self):
        with self.app.test_request_context():
            """Test loading the current user's profile."""
            response = self.client.get(url_for('profile.user_profile', username=self.user1.username))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User1 Post', response.data)  # Post title

    def test_user_profile_other_profile(self):
        with self.app.test_request_context():
            """Test loading another user's public profile."""
            response = self.client.get(url_for('profile.user_profile', username=self.user2.username))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User2 Post', response.data)  # Post title
        self.assertIn(b'Follow', response.data)  # Follow button for other users

    def test_user_profile_not_found(self):
        with self.app.test_request_context():
            """Test accessing a non-existent user's profile."""
            response = self.client.get(url_for('profile.user_profile', username='nonexistentuser'))

    def test_follow_user(self):
        with self.app.test_request_context():
            """Test following another user."""
            response = self.client.post(url_for('profile.toggle_follow', user_id=self.user2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.query.count(), 1)
        self.assertEqual(response.get_json()['status'], 'followed')

    def test_unfollow_user(self):
        """Test unfollowing another user."""
        # Pre-condition: User1 follows User2
        self.user1.following.append(self.user2)
        db.session.commit()
        with self.app.test_request_context():
            response = self.client.post(url_for('profile.toggle_follow', user_id=self.user2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.query.count(), 0)
        self.assertEqual(response.get_json()['status'], 'unfollowed')

    def test_follow_self_error(self):
        with self.app.test_request_context():
            """Test attempting to follow oneself."""
            response = self.client.post(url_for('profile.toggle_follow', user_id=self.user1.id))
        self.assertEqual(response.status_code, 400)
        self.assertIn('You cannot follow yourself.', response.get_json()['error'])


if __name__ == '__main__':
    unittest.main()
