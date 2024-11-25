from datetime import datetime, timezone

from flask_login import UserMixin

from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Profile Fields
    profile_picture = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.String(300), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Social Fields (many-to-many relationship for followers)
    followers = db.relationship(
        'User',
        secondary='follows',
        primaryjoin='User.id==follows.c.follower_id',
        secondaryjoin='User.id==follows.c.followed_id',
        backref='following'
    )

    # Preferences and Settings
    is_private = db.Column(db.Boolean, default=False)
    preferred_garden_type = db.Column(db.String(50), nullable=True)
    preferred_planting_zone = db.Column(db.String(50), nullable=True)

    # One-to-many relationship with posts
    posts = db.relationship('Post', back_populates='author')

    # Relationships for likes (many-to-many relationships)
    liked_posts = db.relationship('PostLike', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    liked_comments = db.relationship('CommentLike', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, username, email, password_hash, **kwargs):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        # Set additional attributes if provided
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<User {self.username}>"


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Timezone-aware timestamp


class PostLike(db.Model):
    __tablename__ = 'post_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Timezone-aware timestamp

    def __repr__(self):
        return f"<PostLike User {self.user_id} likes Post {self.post_id}>"


class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Timezone-aware timestamp

    def __repr__(self):
        return f"<CommentLike User {self.user_id} likes Comment {self.comment_id}>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Timezone-aware timestamp
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key renamed to author_id

    # Relationship with User
    author = db.relationship('User', back_populates='posts', lazy=True)  # Unique backref 'posts' to avoid conflict

    # Relationship for likes
    likes = db.relationship('PostLike', backref='post', lazy='dynamic', cascade="all, delete-orphan")

    # Additional Fields
    image_url = db.Column(db.String(300), nullable=True)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    tags = db.Column(db.String(200), nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    edited_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, title, content, author_id, **kwargs):
        self.title = title
        self.content = content
        self.author_id = author_id
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Post {self.title}>"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Timezone-aware timestamp
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Renamed to author_id
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    # Relationship with User
    author = db.relationship('User', backref=db.backref('comments', lazy=True))  # Unique backref 'comments'

    # Relationship for likes
    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic', cascade="all, delete-orphan")

    # Additional Fields
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent_comment', remote_side=[id]), lazy=True)
    is_flagged = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, content, author_id, post_id, **kwargs):
        self.content = content
        self.author_id = author_id
        self.post_id = post_id
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Comment {self.id} by User {self.author_id} on Post {self.post_id}>"
