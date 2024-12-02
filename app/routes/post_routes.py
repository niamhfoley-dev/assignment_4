# app/routes/post_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, jsonify
# Importing Flask utilities for creating blueprints, rendering templates, handling redirects,
# URL generation, flashing messages, processing requests, logging errors, aborting, and returning JSON responses.

from flask_login import login_required, current_user
# Importing Flask-Login utilities to restrict access to authenticated users and get the current user.

from app.forms import CreatePostForm, CommentForm
# Importing form classes for creating posts and comments.

from app.models import Post, Comment, CommentLike, PostLike, PostDislike
# Importing database models for posts, comments, and related like/dislike functionalities.

from app import db
# Importing the database instance for database operations.

post_bp = Blueprint('post', __name__, url_prefix='/posts')
# Creating a Blueprint named 'post' with a URL prefix of '/posts' for managing post-related routes.

@post_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new post."""
    try:
        form = CreatePostForm()
        # Instantiate the form for creating a post.

        if form.validate_on_submit():
            # If the form is valid upon submission:
            post = Post(title=form.title.data, content=form.content.data, author=current_user, author_id=current_user.id)
            # Create a new Post object with the form data and the current user's ID.

            db.session.add(post)
            # Add the post to the database session.

            db.session.commit()
            # Commit the transaction to save the post to the database.

            flash('Your post has been created!', 'success')
            # Flash a success message to the user.

            return redirect(url_for('main.home'))
            # Redirect to the home page.

        return render_template('post/create_post.html', form=form)
        # Render the post creation form template.

    except Exception as e:
        current_app.logger.error(f"Error creating post: {e}")
        # Log any exceptions during post creation.

        return render_template('error.html', message="An error occurred while creating the post."), 500
        # Render an error template with a 500 status code if an exception is caught.

@post_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    """Display post details and handle comments."""
    post = Post.query.get_or_404(post_id)
    # Retrieve the post by its ID or return a 404 error if it doesn't exist.

    comment_form = CommentForm()
    reply_form = CommentForm()
    # Instantiate forms for adding comments and replies.

    liked_post = PostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    # Check if the current user has liked the post.

    liked_comments = {
        comment.id: CommentLike.query.filter_by(user_id=current_user.id, comment_id=comment.id).first() is not None
        for comment in post.comments
    }
    # Track whether the current user has liked each comment on the post.

    if comment_form.validate_on_submit():
        # If a new comment is submitted and valid:
        new_comment = Comment(content=comment_form.content.data, author_id=current_user.id, post_id=post.id)
        # Create a new comment.

        db.session.add(new_comment)
        # Add the comment to the database session.

        db.session.commit()
        # Commit the transaction to save the comment.

        flash('Comment posted successfully!', 'success')
        # Flash a success message to the user.

        return redirect(url_for('post.post_detail', post_id=post.id))
        # Redirect back to the post detail page.

    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    # Fetch all comments for the post, ordered by most recent.

    return render_template(
        'post/post_detail.html',
        post=post,
        comments=comments,
        comment_form=comment_form,
        reply_form=reply_form,
        liked_post=liked_post,
        liked_comments=liked_comments
    )
    # Render the post detail template with all necessary data.

@post_bp.route('/post/<int:post_id>/<reaction>', methods=['POST'])
def toggle_post_reaction(post_id, reaction):
    """Toggle like or dislike on a post."""
    post = Post.query.get_or_404(post_id)
    # Retrieve the post by its ID or return a 404 error.

    user_id = current_user.id
    # Get the current user's ID.

    if reaction == 'like':
        # Handle like reaction:
        existing_like = PostLike.query.filter_by(post_id=post.id, user_id=user_id).first()
        if existing_like:
            db.session.delete(existing_like)
        else:
            db.session.add(PostLike(post_id=post.id, user_id=user_id))
        PostDislike.query.filter_by(post_id=post.id, user_id=user_id).delete()
    elif reaction == 'dislike':
        # Handle dislike reaction:
        existing_dislike = PostDislike.query.filter_by(post_id=post.id, user_id=user_id).first()
        if existing_dislike:
            db.session.delete(existing_dislike)
        else:
            db.session.add(PostDislike(post_id=post.id, user_id=user_id))
        PostLike.query.filter_by(post_id=post.id, user_id=user_id).delete()
    else:
        return jsonify({'error': 'Invalid reaction type'}), 400
        # Return a JSON error response if the reaction type is invalid.

    db.session.commit()
    # Commit the changes to the database.

    return jsonify({
        'likes': post.likes.count(),
        'dislikes': post.dislikes.count()
    })
    # Return the updated count of likes and dislikes as JSON.

@post_bp.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def toggle_comment_like(comment_id):
    """Toggle like on a comment."""
    comment = Comment.query.get_or_404(comment_id)
    # Retrieve the comment by its ID or return a 404 error.

    like = CommentLike.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()
    # Check if the current user has already liked the comment.

    if like:
        db.session.delete(like)
        # If already liked, remove the like.
    else:
        new_like = CommentLike(user_id=current_user.id, comment_id=comment_id)
        db.session.add(new_like)
        # If not liked, add a like.

    db.session.commit()
    # Commit the changes to the database.

    return jsonify(success=True)
    # Return a success response as JSON.

@post_bp.route('/post/<int:post_id>/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_comment(post_id, comment_id):
    """Reply to a comment."""
    reply_form = CommentForm()
    # Instantiate the reply form.

    if reply_form.validate_on_submit():
        # If the form is valid upon submission:
        reply = Comment(
            content=reply_form.content.data,
            user_id=current_user.id,
            post_id=post_id,
            parent_comment_id=comment_id,
            author_id=current_user.id
        )
        db.session.add(reply)
        db.session.commit()
        flash('Reply posted successfully!', 'success')
    return redirect(url_for('post.post_detail', post_id=post_id))
    # Redirect back to the post detail page.

@post_bp.route('/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    """Update an existing post."""
    try:
        post = Post.query.get_or_404(post_id)
        # Retrieve the post or return a 404 error.

        if post.author != current_user:
            abort(403)
            # Return a 403 Forbidden error if the current user is not the post author.

        form = CreatePostForm()
        # Instantiate the form for updating the post.

        if form.validate_on_submit():
            # If the form is valid upon submission:
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('post.post_detail', post_id=post.id))
        elif request.method == 'GET':
            # Pre-fill the form with the existing post data for GET requests.
            form.title.data = post.title
            form.content.data = post.content

        return render_template('create_post.html', form=form, legend='Update Post')
        # Render the post update form.

    except Exception as e:
        current_app.logger.error(f"Error updating post {post_id}: {e}")
        # Log any exceptions during post update.

        return render_template('error.html', message="An error occurred while updating the post."), 500
        # Render an error template with a 500 status code if an exception is caught.

@post_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post."""
    try:
        post = Post.query.get_or_404(post_id)
        # Retrieve the post or return a 404 error.

        if post.author != current_user:
            abort(403)
            # Return a 403 Forbidden error if the current user is not the post author.

        db.session.delete(post)
        # Mark the post for deletion.

        db.session.commit()
        # Commit the transaction to delete the post.

        flash('Your post has been deleted.', 'info')
        # Flash an informational message to the user.

        return redirect(url_for('main.home'))
        # Redirect to the home page.

    except Exception as e:
        current_app.logger.error(f"Error deleting post {post_id}: {e}")
        # Log any exceptions during post deletion.

        return render_template('error.html', message="An error occurred while deleting the post."), 500
        # Render an error template with a 500 status code if an exception is caught.
