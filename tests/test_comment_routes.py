import unittest
from app import create_app, db
from app.models import User, Post, Comment
from flask import url_for
from flask_login import login_user


class CommentRoutesTestCase(unittest.TestCase):
    """Test cases for comment routes."""

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
        cls.user = User(username='testuser', email='testuser@example3.com', password_hash=password_hash)
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

    def test_create_comment_success(self):
        with self.app.test_request_context():
            """Test creating a comment successfully."""
            response = self.client.post(url_for('comment.create_comment', post_id=self.post.id), data={
                'content': 'This is a test comment.'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.query.count(), 1)

    def test_create_comment_rate_limit(self):
        with self.app.test_request_context():
            """Test the rate limit for creating comments."""
            # Post a comment
            self.client.post(url_for('comment.create_comment', post_id=self.post.id), data={
                'content': 'First comment.'
            }, follow_redirects=True)

        with self.app.test_request_context():
            # Attempt to post another comment immediately
            response = self.client.post(url_for('comment.create_comment', post_id=self.post.id), data={
                'content': 'Second comment.'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_update_comment_success(self):
        """Test updating a comment successfully."""
        # Create a comment
        comment = Comment(content='Original comment', post_id=self.post.id, author_id=self.user.id)
        db.session.add(comment)
        db.session.commit()

        with self.app.test_request_context():
            # Update the comment
            response = self.client.post(url_for('comment.update_comment', comment_id=comment.id), data={
                'content': 'Updated comment'
            }, follow_redirects=True)

    def test_update_comment_unauthorized(self):
        """Test that unauthorized users cannot update comments."""
        # Create a comment by another user
        another_user = User(username='anotherusercgjfcgfcgfc', email='anotheruser@jgcjhcexample.com', password_hash='password')
        db.session.add(another_user)
        db.session.commit()
        comment = Comment(content='Their comment', post_id=self.post.id, author_id=another_user.id)
        db.session.add(comment)
        db.session.commit()

        with self.app.test_request_context():
            # Attempt to update the comment as the test user
            response = self.client.post(url_for('comment.update_comment', comment_id=comment.id), data={
                'content': 'Unauthorized update'
            }, follow_redirects=True)

    def test_delete_comment_success(self):
        """Test deleting a comment successfully."""
        # Create a comment
        comment = Comment(content='Comment to delete', post_id=self.post.id, author_id=self.user.id)
        db.session.add(comment)
        db.session.commit()

        with self.app.test_request_context():
            # Delete the comment
            response = self.client.post(url_for('comment.delete_comment', comment_id=comment.id), follow_redirects=True)

    def test_delete_comment_unauthorized(self):
        """Test that unauthorized users cannot delete comments."""
        # Create a comment by another user
        another_user = User(username='anotheruser', email='anotheruser@example.com', password_hash='pass')
        db.session.add(another_user)
        db.session.commit()
        comment = Comment(content='Their comment', post_id=self.post.id, author_id=another_user.id)
        db.session.add(comment)
        db.session.commit()

        with self.app.test_request_context():
            # Attempt to delete the comment as the test user
            response = self.client.post(url_for('comment.delete_comment', comment_id=comment.id), follow_redirects=True)
