# app/routes/comment_routes.py

from datetime import datetime, timedelta, timezone
# Importing datetime utilities for handling timestamps and timezones.

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, session
# Importing Flask utilities for blueprint creation, template rendering, redirects, flashing messages,
# handling requests, accessing the app context, aborting, and managing sessions.

from flask_login import login_required, current_user
# Importing Flask-Login utilities for protecting routes and accessing the currently logged-in user.

from app.forms import CommentForm
# Importing the form class for comment creation and updates.

from app.models import Comment, Post
# Importing the database models for comments and posts.

from app import db
# Importing the database instance for managing database operations.

comment_bp = Blueprint('comment', __name__, url_prefix='/comments')
# Creating a Blueprint for comment-related routes, with a URL prefix of '/comments'.


@comment_bp.route('/create/<int:post_id>', methods=['POST'])
@login_required  # Restricts access to authenticated users only.
def create_comment(post_id):
    """Create a new comment on a post."""
    try:
        last_comment_time = session.get('last_comment_time')
        # Get the last comment timestamp from the session.

        if last_comment_time and datetime.now(timezone.utc) < last_comment_time + timedelta(seconds=30):
            # Throttle comments by requiring at least 30 seconds between submissions.
            flash("You're commenting too fast! Please wait a moment.", "warning")
            # Flash a warning message if the user is commenting too quickly.
            return redirect(url_for('post.post_detail', post_id=post_id))
            # Redirect back to the post detail page.

        form = CommentForm()
        # Instantiate the comment form.

        if form.validate_on_submit():
            # If the form is valid upon submission:
            post = Post.query.get_or_404(post_id)
            # Retrieve the post being commented on or return a 404 error.

            comment = Comment(content=form.content.data, post=post, author_id=current_user.id, post_id=post_id)
            # Create a new Comment instance with the form data and the current user's ID.

            db.session.add(comment)
            # Add the new comment to the database session.

            db.session.commit()
            # Commit the transaction to save the comment to the database.

            session['last_comment_time'] = datetime.now(timezone.utc)
            # Update the session with the current timestamp to enforce throttling.

            flash('Your comment has been posted.', 'success')
            # Flash a success message.

            return redirect(url_for('post.post_detail', post_id=post_id))
            # Redirect back to the post detail page.

        else:
            flash('Failed to post comment.', 'danger')
            # Flash an error message if form validation fails.
            return redirect(url_for('post.post_detail', post_id=post_id))
            # Redirect back to the post detail page.

    except Exception as e:
        current_app.logger.error(f"Error creating comment on post {post_id}: {e}")
        # Log any exceptions that occur during comment creation.
        return render_template('error.html', message="An error occurred while posting the comment."), 500
        # Render an error template with a 500 status code if an exception is caught.


@comment_bp.route('/<int:comment_id>/update', methods=['GET', 'POST'])
@login_required  # Restricts access to authenticated users only.
def update_comment(comment_id):
    """Update an existing comment."""
    try:
        comment = Comment.query.get_or_404(comment_id)
        # Retrieve the comment to be updated or return a 404 error.

        if comment.comment_author != current_user:
            # Ensure that only the author of the comment can edit it.
            abort(403)  # Return a 403 Forbidden error if the user is not the author.

        form = CommentForm()
        # Instantiate the comment form.

        if request.method == 'GET':
            # For GET requests, pre-populate the form with the current comment content.
            form.content.data = comment.content

        if form.validate_on_submit():
            # For POST requests, validate and process the form:
            comment.content = form.content.data
            # Update the comment's content with the form data.

            comment.edited_at = datetime.now(timezone.utc)
            # Update the comment's "edited_at" timestamp.

            db.session.commit()
            # Commit the changes to the database.

            flash('Your comment has been updated.', 'success')
            # Flash a success message.

            return redirect(url_for('post.post_detail', post_id=comment.post_id))
            # Redirect back to the post detail page.

        return render_template('comment/forms/update_comment.html', form=form, comment=comment)
        # Render the comment update form template with the current form and comment data.

    except Exception as e:
        current_app.logger.error(f"Error updating comment {comment_id}: {e}")
        # Log any exceptions that occur during comment updates.
        return render_template('error.html', message="An error occurred while updating the comment."), 500
        # Render an error template with a 500 status code if an exception is caught.


@comment_bp.route('/<int:comment_id>/delete', methods=['POST'])
@login_required  # Restricts access to authenticated users only.
def delete_comment(comment_id):
    """Delete a comment."""
    try:
        comment = Comment.query.get_or_404(comment_id)
        # Retrieve the comment to be deleted or return a 404 error.

        if comment.comment_author != current_user:
            # Ensure that only the author of the comment can delete it.
            abort(403)  # Return a 403 Forbidden error if the user is not the author.

        db.session.delete(comment)
        # Mark the comment for deletion.

        db.session.commit()
        # Commit the transaction to remove the comment from the database.

        flash('Your comment has been deleted.', 'info')
        # Flash an informational message.

        return redirect(url_for('post.post_detail', post_id=comment.post_id))
        # Redirect back to the post detail page.

    except Exception as e:
        current_app.logger.error(f"Error deleting comment {comment_id}: {e}")
        # Log any exceptions that occur during comment deletion.
        return render_template('error.html', message="An error occurred while deleting the comment."), 500
        # Render an error template with a 500 status code if an exception is caught.
