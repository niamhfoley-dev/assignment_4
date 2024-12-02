from datetime import datetime, timezone
# Importing utilities for handling timestamps with timezone awareness.

from flask_login import UserMixin
# Importing UserMixin to integrate user authentication with Flask-Login.

from app import db


# Importing the database instance for defining and managing models.

# -------------------------------
# User Model
# -------------------------------
class User(UserMixin, db.Model):
    # User's unique ID (primary key).
    id = db.Column(db.Integer, primary_key=True)

    # Username, must be unique and cannot be null.
    username = db.Column(db.String(150), unique=True, nullable=False)

    # Email, must be unique and cannot be null.
    email = db.Column(db.String(150), unique=True, nullable=False)

    # Hashed password, stored securely.
    password_hash = db.Column(db.String(128), nullable=False)

    # Optional fields for user profile.
    profile_picture = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.String(300), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)

    # Timestamp when the user joined, defaults to current UTC time.
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Many-to-many relationship for followers.
    followers = db.relationship(
        'User',
        secondary='follows',
        primaryjoin='User.id==follows.c.follower_id',
        secondaryjoin='User.id==follows.c.followed_id',
        backref='following'
    )

    # Boolean flag for private accounts.
    is_private = db.Column(db.Boolean, default=False)

    # User preferences (optional fields).
    preferred_garden_type = db.Column(db.String(50), nullable=True)
    preferred_planting_zone = db.Column(db.String(50), nullable=True)

    # One-to-many relationship with posts.
    posts = db.relationship('Post', back_populates='author')

    # Many-to-many relationships for likes on posts and comments.
    liked_posts = db.relationship('PostLike', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    liked_comments = db.relationship('CommentLike', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, username, email, password_hash, **kwargs):
        # Constructor to initialize a user with optional additional attributes.
        self.username = username
        self.email = email
        self.password_hash = password_hash
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<User {self.username}>"


# -------------------------------
# Follow Model
# -------------------------------
class Follow(db.Model):
    __tablename__ = 'follows'
    # Composite primary key for follower and followed IDs.
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # Timestamp for when the follow action occurred.
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))


# -------------------------------
# PostLike Model
# -------------------------------
class PostLike(db.Model):
    __tablename__ = 'post_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PostLike User {self.user_id} likes Post {self.post_id}>"


# -------------------------------
# PostDislike Model
# -------------------------------
class PostDislike(db.Model):
    __tablename__ = 'post_dislikes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PostDislike User {self.user_id} dislikes Post {self.post_id}>"


# -------------------------------
# CommentLike Model
# -------------------------------
class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<CommentLike User {self.user_id} likes Comment {self.comment_id}>"


# -------------------------------
# Post Model
# -------------------------------
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # Title of the post.
    content = db.Column(db.Text, nullable=False)  # Content of the post.
    date_posted = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Post timestamp.
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key for the author.

    # Relationship with User.
    author = db.relationship('User', back_populates='posts', lazy=True)

    # Relationships for likes and dislikes.
    likes = db.relationship('PostLike', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    dislikes = db.relationship('PostDislike', backref='post', lazy='dynamic', cascade="all, delete-orphan")

    # Additional optional fields.
    image_url = db.Column(db.String(300), nullable=True)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    tags = db.Column(db.String(200), nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    edited_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, title, content, author_id, **kwargs):
        # Constructor to initialize a post with optional additional attributes.
        self.title = title
        self.content = content
        self.author_id = author_id
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Post {self.title}>"


# -------------------------------
# Comment Model
# -------------------------------
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # Content of the comment.
    date_posted = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Comment timestamp.
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key for the author.
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)  # Foreign key for the associated post.

    # Relationship with User.
    author = db.relationship('User', backref=db.backref('comments', lazy=True))

    # Relationship for likes on the comment.
    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic', cascade="all, delete-orphan")

    # Fields for threaded replies.
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent_comment', remote_side=[id]), lazy=True)

    # Additional optional fields.
    is_flagged = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, content, author_id, post_id, **kwargs):
        # Constructor to initialize a comment with optional additional attributes.
        self.content = content
        self.author_id = author_id
        self.post_id = post_id
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Comment {self.id} by User {self.author_id} on Post {self.post_id}>"
