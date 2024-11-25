# app/routes/main_routes.py

from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
from flask_login import current_user, login_required

from app.forms import CreatePostForm
from app.models import Post, User
from app import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Render the home page with recent posts."""

    try:
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        return render_template('home.html', posts=posts)
    except Exception as e:
        current_app.logger.error(f"Error loading home page: {e}")
        return render_template('error.html', message="An error occurred while loading the home page."), 500


@main_bp.route('/about')
def about():
    """Render the about page."""
    try:
        return render_template('about.html')
    except Exception as e:
        current_app.logger.error(f"Error loading about page: {e}")
        return render_template('error.html', message="An error occurred while loading the about page."), 500


@main_bp.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    """Render the explore page with all posts."""
    form = CreatePostForm()
    if form.validate_on_submit():
        try:
            # Assign current_user.id to user_id for the post
            post = Post(title=form.title.data, content=form.content.data, author_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('main.explore'))
        except Exception as e:
            current_app.logger.error(f"Error creating post: {e}")
            db.session.rollback()
            flash('An error occurred while creating the post.', 'danger')

    # Fetch posts to display on the explore page
    try:
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        return render_template('explore.html', posts=posts, form=form)
    except Exception as e:
        current_app.logger.error(f"Error loading explore page: {e}")
        return render_template('error.html', message="An error occurred while loading the explore page."), 500


@main_bp.route('/search')
def search():
    """Handle search queries for posts and users."""
    try:
        query = request.args.get('q', '')
        if query:
            posts = Post.query.filter(Post.content.ilike(f'%{query}%')).all()
            users = User.query.filter(User.username.ilike(f'%{query}%')).all()
            return render_template('search_results.html', posts=posts, users=users, query=query)
        else:
            return redirect(url_for('main.home'))
    except Exception as e:
        current_app.logger.error(f"Error during search: {e}")
        return render_template('error.html', message="An error occurred during the search."), 500
