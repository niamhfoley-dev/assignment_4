from flask import Blueprint, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Post, PostLike, Comment, CommentLike
from app.utils import add_like, remove_like


like_bp = Blueprint('like', __name__)


@like_bp.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    """Route for liking a post."""
    try:
        post = Post.query.get_or_404(post_id)  # Fetch the post
        if add_like(current_user, Post, PostLike, post_id):
            flash('Post liked!', 'success')
        else:
            flash('You have already liked this post.', 'info')
        return redirect(url_for('post.post_detail', post_id=post_id))

    except Exception as e:
        current_app.logger.error(f"Error in like_post route for post {post_id}: {e}")
        flash('An error occurred while trying to like the post.', 'danger')
        return redirect(url_for('post.post_detail', post_id=post_id))


@like_bp.route('/unlike_post/<int:post_id>', methods=['POST'])
@login_required
def unlike_post(post_id):
    """Route for unliking a post."""
    try:
        if remove_like(current_user, PostLike, post_id):
            flash('Post unliked.', 'success')
        else:
            flash('You have not liked this post.', 'info')
        return redirect(url_for('post.post_detail', post_id=post_id))

    except Exception as e:
        current_app.logger.error(f"Error in unlike_post route for post {post_id}: {e}")
        flash('An error occurred while trying to unlike the post.', 'danger')
        return redirect(url_for('post.post_detail', post_id=post_id))


@like_bp.route('/like_comment/<int:comment_id>', methods=['POST'])
@login_required
def like_comment(comment_id):
    """Route for liking a comment."""
    try:
        comment = Comment.query.get_or_404(comment_id)  # Fetch the comment
        if add_like(current_user, Comment, CommentLike, comment_id):
            flash('Comment liked!', 'success')
        else:
            flash('You have already liked this comment.', 'info')
        return redirect(url_for('post.post_detail', post_id=comment.post_id))

    except Exception as e:
        current_app.logger.error(f"Error in like_comment route for comment {comment_id}: {e}")
        flash('An error occurred while trying to like the comment.', 'danger')
        return redirect(url_for('post.post_detail', post_id=comment.post_id))


@like_bp.route('/unlike_comment/<int:comment_id>', methods=['POST'])
@login_required
def unlike_comment(comment_id):
    """Route for unliking a comment."""
    try:
        comment = Comment.query.get_or_404(comment_id)  # Fetch the comment
        if remove_like(current_user, CommentLike, comment_id):
            flash('Comment unliked.', 'success')
        else:
            flash('You have not liked this comment.', 'info')
        return redirect(url_for('post.post_detail', post_id=comment.post_id))
    except Exception as e:
        current_app.logger.error(f"Error in unlike_comment route for comment {comment_id}: {e}")
        flash('An error occurred while trying to unlike the comment.', 'danger')
        return redirect(url_for('post.post_detail', post_id=comment.post_id))
