# app/routes/post_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, jsonify
from flask_login import login_required, current_user
from app.forms import CreatePostForm, CommentForm
from app.models import Post, Comment, CommentLike, PostLike, PostDislike
from app import db

post_bp = Blueprint('post', __name__, url_prefix='/posts')


@post_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new post."""
    try:
        form = CreatePostForm()
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data, author=current_user, author_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('main.home'))
        return render_template('post/create_post.html', form=form)
    except Exception as e:
        current_app.logger.error(f"Error creating post: {e}")
        return render_template('error.html', message="An error occurred while creating the post."), 500


@post_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    comment_form = CommentForm()
    reply_form = CommentForm()

    # Track likes by the current user for posts and comments
    liked_post = PostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    liked_comments = {
        comment.id: CommentLike.query.filter_by(user_id=current_user.id, comment_id=comment.id).first() is not None
        for comment in post.comments
    }



    if comment_form.validate_on_submit():
        new_comment = Comment(content=comment_form.content.data, author_id=current_user.id, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment posted successfully!', 'success')
        return redirect(url_for('post.post_detail', post_id=post.id))

    # Query comments with ordering
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()

    return render_template(
        'post/post_detail.html',
        post=post,
        comments=comments,
        comment_form=comment_form,
        reply_form=reply_form,
        liked_post=liked_post,
        liked_comments=liked_comments
    )


@post_bp.route('/post/<int:post_id>/<reaction>', methods=['POST'])
def toggle_post_reaction(post_id, reaction):
    print(post_id, reaction)
    post = Post.query.get_or_404(post_id)
    user_id = current_user.id  # Assuming you're using Flask-Login

    if reaction == 'like':
        # Check if user already liked the post
        existing_like = PostLike.query.filter_by(post_id=post.id, user_id=user_id).first()
        if existing_like:
            db.session.delete(existing_like)
        else:
            db.session.add(PostLike(post_id=post.id, user_id=user_id))
        # Remove dislike if it exists
        PostDislike.query.filter_by(post_id=post.id, user_id=user_id).delete()
    elif reaction == 'dislike':
        # Check if user already disliked the post
        existing_dislike = PostDislike.query.filter_by(post_id=post.id, user_id=user_id).first()
        if existing_dislike:
            db.session.delete(existing_dislike)
        else:
            db.session.add(PostDislike(post_id=post.id, user_id=user_id))
        # Remove like if it exists
        PostLike.query.filter_by(post_id=post.id, user_id=user_id).delete()
    else:
        return jsonify({'error': 'Invalid reaction type'}), 400

    db.session.commit()
    return jsonify({
        'likes': post.likes.count(),
        'dislikes': post.dislikes.count()
    })



@post_bp.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def toggle_comment_like(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    like = CommentLike.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()

    if like:
        db.session.delete(like)
    else:
        new_like = CommentLike(user_id=current_user.id, comment_id=comment_id)
        db.session.add(new_like)

    db.session.commit()
    return jsonify(success=True)


@post_bp.route('/post/<int:post_id>/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_comment(post_id, comment_id):
    reply_form = CommentForm()
    if reply_form.validate_on_submit():
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


@post_bp.route('/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    """Update an existing post."""
    try:
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)  # Forbidden
        form = CreatePostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('post.post_detail', post_id=post.id))
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
        return render_template('create_post.html', form=form, legend='Update Post')
    except Exception as e:
        current_app.logger.error(f"Error updating post {post_id}: {e}")
        return render_template('error.html', message="An error occurred while updating the post."), 500


@post_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post."""
    try:
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)  # Forbidden
        db.session.delete(post)
        db.session.commit()
        flash('Your post has been deleted.', 'info')
        return redirect(url_for('main.home'))
    except Exception as e:
        current_app.logger.error(f"Error deleting post {post_id}: {e}")
        return render_template('error.html', message="An error occurred while deleting the post."), 500

