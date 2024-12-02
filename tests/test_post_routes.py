import unittest
from flask import url_for, jsonify
from app import create_app, db
from app.models import User, Post, Comment, PostLike, PostDislike, CommentLike


class PostRoutesTestCase(unittest.TestCase):
    """Test cases for post routes."""

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
        db.session.query(Comment).delete()
        db.session.query(PostLike).delete()
        db.session.query(PostDislike).delete()
        db.session.query(Post).delete()
        db.session.commit()

    def test_create_post_success(self):
        with self.app.test_request_context():
            """Test creating a new post successfully."""
            response = self.client.post(url_for('post.create_post'), data={
            'title': 'New Post',
            'content': 'New post content'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your post has been created!', response.data)
        self.assertEqual(Post.query.count(), 2)  # Original post + new post

    def test_post_detail_success(self):
        with self.app.test_request_context():
            """Test the post detail page loads successfully with comments."""
            response = self.client.get(url_for('post.post_detail', post_id=self.post.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post', response.data)  # Post title
        self.assertIn(b'Test content', response.data)  # Post content

    def test_toggle_post_like(self):
        with self.app.test_request_context():
            """Test toggling a like on a post."""
            response = self.client.post(url_for('post.toggle_post_reaction', post_id=self.post.id, reaction='like'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PostLike.query.count(), 1)

        # Toggle off
        with self.app.test_request_context():
            response = self.client.post(url_for('post.toggle_post_reaction', post_id=self.post.id, reaction='like'))
            self.assertEqual(response.status_code, 200)
        self.assertEqual(PostLike.query.count(), 0)

    def test_toggle_post_dislike(self):
        with self.app.test_request_context():
            """Test toggling a dislike on a post."""
            response = self.client.post(url_for('post.toggle_post_reaction', post_id=self.post.id, reaction='dislike'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PostDislike.query.count(), 1)

        with self.app.test_request_context():
            # Toggle off
            response = self.client.post(url_for('post.toggle_post_reaction', post_id=self.post.id, reaction='dislike'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PostDislike.query.count(), 0)

    def test_toggle_comment_like(self):
        """Test toggling a like on a comment."""
        comment = Comment(content='Test comment', post_id=self.post.id, author_id=self.user.id)
        db.session.add(comment)
        db.session.commit()
        with self.app.test_request_context():
            response = self.client.post(url_for('post.toggle_comment_like', comment_id=comment.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CommentLike.query.count(), 1)

        with self.app.test_request_context():
            # Toggle off
            response = self.client.post(url_for('post.toggle_comment_like', comment_id=comment.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CommentLike.query.count(), 0)

    def test_update_post_success(self):
        with self.app.test_request_context():
            """Test updating a post successfully."""
            response = self.client.post(url_for('post.update_post', post_id=self.post.id), data={
            'title': 'Updated Post',
            'content': 'Updated content'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your post has been updated!', response.data)
        self.assertEqual(Post.query.first().title, 'Updated Post')

    def test_delete_post_success(self):
        with self.app.test_request_context():
            """Test deleting a post successfully."""
            response = self.client.post(url_for('post.delete_post', post_id=self.post.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your post has been deleted.', response.data)
        self.assertEqual(Post.query.count(), 0)

    def test_reply_to_comment_success(self):
        """Test replying to a comment."""
        comment = Comment(content='Test comment', post_id=self.post.id, author_id=self.user.id)
        db.session.add(comment)
        db.session.commit()
        with self.app.test_request_context():
            response = self.client.post(
            url_for('post.reply_comment', post_id=self.post.id, comment_id=comment.id),
                data={'content': 'Test reply'},
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reply posted successfully!', response.data)
        self.assertEqual(Comment.query.count(), 2)  # Original comment + reply
