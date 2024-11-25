# app/routes/comment_routes.py
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, session
from flask_login import login_required, current_user
from app.forms import CommentForm
from app.models import Comment, Post
from app import db

comment_bp = Blueprint('comment', __name__, url_prefix='/comments')


@comment_bp.route('/create/<int:post_id>', methods=['POST'])
@login_required
def create_comment(post_id):
    """Create a new comment on a post."""
    try:
        last_comment_time = session.get('last_comment_time')
        if last_comment_time and datetime.now(timezone.utc) < last_comment_time + timedelta(seconds=30):
            flash("You're commenting too fast! Please wait a moment.", "warning")
            return redirect(url_for('post.post_detail', post_id=post_id))

        form = CommentForm()
        if form.validate_on_submit():
            post = Post.query.get_or_404(post_id)
            comment = Comment(content=form.content.data, post=post, author_id=current_user.id, post_id=post_id)

            db.session.add(comment)
            db.session.commit()
            session['last_comment_time'] = datetime.now(timezone.utc)
            flash('Your comment has been posted.', 'success')
            return redirect(url_for('post.post_detail', post_id=post_id))
        else:
            flash('Failed to post comment.', 'danger')
            return redirect(url_for('post.post_detail', post_id=post_id))
    except Exception as e:
        current_app.logger.error(f"Error creating comment on post {post_id}: {e}")
        return render_template('error.html', message="An error occurred while posting the comment."), 500


@comment_bp.route('/<int:comment_id>/update', methods=['GET', 'POST'])
@login_required
def update_comment(comment_id):
    """Update an existing comment."""
    try:
        comment = Comment.query.get_or_404(comment_id)

        # Ensure that only the comment's author can edit it
        if comment.comment_author != current_user:
            abort(403)  # Forbidden

        form = CommentForm()

        # Pre-populate form with current comment content for GET requests
        if request.method == 'GET':
            form.content.data = comment.content

        # Validate and process the form on POST requests
        if form.validate_on_submit():
            # Update the comment content
            comment.content = form.content.data
            comment.edited_at = datetime.now(timezone.utc)  # Update edit timestamp
            db.session.commit()
            flash('Your comment has been updated.', 'success')
            return redirect(url_for('post.post_detail', post_id=comment.post_id))

        return render_template('comment/forms/update_comment.html', form=form, comment=comment)

    except Exception as e:
        current_app.logger.error(f"Error updating comment {comment_id}: {e}")
        return render_template('error.html', message="An error occurred while updating the comment."), 500


@comment_bp.route('/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment."""
    try:
        comment = Comment.query.get_or_404(comment_id)
        if comment.comment_author != current_user:
            abort(403)  # Forbidden
        db.session.delete(comment)
        db.session.commit()
        flash('Your comment has been deleted.', 'info')
        return redirect(url_for('post.post_detail', post_id=comment.post_id))
    except Exception as e:
        current_app.logger.error(f"Error deleting comment {comment_id}: {e}")
        return render_template('error.html', message="An error occurred while deleting the comment."), 500
