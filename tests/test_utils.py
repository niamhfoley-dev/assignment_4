import unittest
from app import create_app, db
from app.models import User, Post, Comment, PostLike, CommentLike
from app.utils import add_like, remove_like


class UtilFunctionsTestCase(unittest.TestCase):
    """Test cases for the `add_like` and `remove_like` helper functions."""

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

        # Create test posts and comments
        cls.post = Post(title='Test Post', content='This is a test post.', author_id=cls.user.id)
        cls.comment = Comment(content='This is a test comment.', author_id=cls.user.id, post_id=1)
        db.session.add(cls.post)
        db.session.add(cls.comment)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_add_like_to_post(self):
        """Test adding a like to a post."""
        result = add_like(self.user, Post, PostLike, self.post.id)
        self.assertEqual(PostLike.query.count(), 1, "PostLike count should be 1 after adding a like.")

    def test_add_duplicate_like_to_post(self):
        """Test adding a duplicate like to a post."""
        add_like(self.user, Post, PostLike, self.post.id)  # Add first like
        result = add_like(self.user, Post, PostLike, self.post.id)  # Try adding a duplicate
        self.assertFalse(result, "Duplicate like should not be added.")
        self.assertEqual(PostLike.query.count(), 1, "PostLike count should remain 1 after a duplicate like.")

    def test_remove_like_from_post(self):
        """Test removing a like from a post."""
        add_like(self.user, Post, PostLike, self.post.id)
        result = remove_like(self.user, PostLike, self.post.id)
        self.assertTrue(result, "Failed to remove like from post.")
        self.assertEqual(PostLike.query.count(), 0, "PostLike count should be 0 after removing a like.")

    def test_remove_nonexistent_like_from_post(self):
        """Test removing a like that doesn't exist."""
        result = remove_like(self.user, PostLike, self.post.id)
        self.assertFalse(result, "Should return False when trying to remove a nonexistent like.")
        self.assertEqual(PostLike.query.count(), 0, "PostLike count should remain 0 when no like exists.")

    def test_add_like_to_comment(self):
        """Test adding a like to a comment."""
        result = add_like(self.user, Comment, CommentLike, self.comment.id)
        self.assertTrue(result, "Failed to add like to comment.")
        self.assertEqual(CommentLike.query.count(), 1, "CommentLike count should be 1 after adding a like.")

    def test_remove_like_from_comment(self):
        """Test removing a like from a comment."""
        add_like(self.user, Comment, CommentLike, self.comment.id)
        result = remove_like(self.user, CommentLike, self.comment.id)
        self.assertTrue(result, "Failed to remove like from comment.")
        self.assertEqual(CommentLike.query.count(), 0, "CommentLike count should be 0 after removing a like.")

    def test_error_handling_in_add_like(self):
        """Test error handling in add_like (simulate exception)."""
        with self.app.app_context():
            result = add_like(None, Post, PostLike, self.post.id)  # Passing None as user
        self.assertFalse(result, "add_like should return False when an exception occurs.")

    def test_error_handling_in_remove_like(self):
        """Test error handling in remove_like (simulate exception)."""
        with self.app.app_context():
            result = remove_like(None, PostLike, self.post.id)  # Passing None as user
        self.assertFalse(result, "remove_like should return False when an exception occurs.")


if __name__ == '__main__':
    unittest.main()
