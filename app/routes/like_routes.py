from flask import Blueprint, redirect, url_for, flash, current_app
# Importing Flask utilities for blueprint creation, redirection, flashing messages,
# generating URLs, and accessing the current app context.

from flask_login import login_required, current_user
# Importing Flask-Login utilities to restrict access to authenticated users and retrieve the current user.

from app.models import Post, PostLike, Comment, CommentLike
# Importing database models for posts, post likes, comments, and comment likes.

from app.utils import add_like, remove_like
# Importing utility functions for handling like and unlike operations.

like_bp = Blueprint('like', __name__)
# Creating a Blueprint named 'like' to group related like/unlike routes.

@like_bp.route('/like_post/<int:post_id>', methods=['POST'])
@login_required  # Restricts access to authenticated users only.
def like_post(post_id):
    """Route for liking a post."""
    try:
        post = Post.query.get_or_404(post_id)
        # Retrieve the post by its ID or return a 404 error if it doesn't exist.

        if add_like(current_user, Post, PostLike, post_id):
            # Attempt to add a like for the post. If successful:
            flash('Post liked!', 'success')
            # Flash a success message.
        else:
            flash('You have already liked this post.', 'info')
            # Flash an informational message if the post was already liked.

        return redirect(url_for('post.post_detail', post_id=post_id))
        # Redirect back to the post detail page.

    except Exception as e:
        current_app.logger.error(f"Error in like_post route for post {post_id}: {e}")
        # Log any exceptions that occur during the like operation.
        flash('An error occurred while trying to like the post.', 'danger')
        # Flash an error message.
        return redirect(url_for('post.post_detail', post_id=post_id))
        # Redirect back to the post detail page.

@like_bp.route('/unlike_post/<int:post_id>', methods=['POST'])
@login_required  # Restricts access to authenticated users only.
def unlike_post(post_id):
    """Route for unliking a post."""
    try:
        if remove_like(current_user, PostLike, post_id):
            # Attempt to remove a like for the post. If successful:
            flash('Post unliked.', 'success')
            # Flash a success message.
        else:
            flash('You have not liked this post.', 'info')
            # Flash an informational message if the post was not previously liked.

        return redirect(url_for('post.post_detail', post_id=post_id))
        # Redirect back to the post detail page.

    except Exception as e:
        current_app.logger.error(f"Error in unlike_post route for post {post_id}: {e}")
        # Log any exceptions that occur during the unlike operation.
        flash('An error occurred while trying to unlike the post.', 'danger')
        # Flash an error message.
        return redirect(url_for('post.post_detail', post_id=post_id))
        # Redirect back to the post detail page.

@like_bp.route('/like_comment/<int:comment_id>', methods=['POST'])
@login_required  # Restricts access to authenticated users only.
def like_comment(comment_id):
    """Route for liking a comment."""
    try:
        comment = Comment.query.get_or_404(comment_id)
        # Retrieve the comment by its ID or return a 404 error if it doesn't exist.

        if add_like(current_user, Comment, CommentLike, comment_id):
            # Attempt to add a like for the comment. If successful:
            flash('Comment liked!', 'success')
            # Flash a success message.
        else:
            flash('You have already liked this comment.', 'info')
            # Flash an informational message if the comment was already liked.

        return redirect(url_for('post.post_detail', post_id=comment.post_id))
        # Redirect back to the post detail page where the comment is located.

    except Exception as e:
        current_app.logger.error(f"Error in like_comment route for comment {comment_id}: {e}")
        # Log any exceptions that occur during the like operation.
        flash('An error occurred while trying to like the comment.', 'danger')
        # Flash an error message.
        return redirect(url_for('post.post_detail', post_id=comment.post_id))
        # Redirect back to the post detail page where the comment is located.

@like_bp.route('/unlike_comment/<int:comment_id>', methods=['POST'])
@login_required  # Restricts access to authenticated users only.
def unlike_comment(comment_id):
    """Route for unliking a comment."""
    try:
        comment = Comment.query.get_or_404(comment_id)
        # Retrieve the comment by its ID or return a 404 error if it doesn't exist.

        if remove_like(current_user, CommentLike, comment_id):
            # Attempt to remove a like for the comment. If successful:
            flash('Comment unliked.', 'success')
            # Flash a success message.
        else:
            flash('You have not liked this comment.', 'info')
            # Flash an informational message if the comment was not previously liked.

        return redirect(url_for('post.post_detail', post_id=comment.post_id))
        # Redirect back to the post detail page where the comment is located.

    except Exception as e:
        current_app.logger.error(f"Error in unlike_comment route for comment {comment_id}: {e}")
        # Log any exceptions that occur during the unlike operation.
        flash('An error occurred while trying to unlike the comment.', 'danger')
        # Flash an error message.
        return redirect(url_for('post.post_detail', post_id=comment.post_id))
        # Redirect back to the post detail page where the comment is located.
