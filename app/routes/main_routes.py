# app/routes/main_routes.py

from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
# Importing Flask utilities for blueprint creation, rendering templates, handling requests,
# accessing the current app context, redirects, URL generation, and flashing messages.

from flask_login import current_user, login_required
# Importing Flask-Login utilities for accessing the currently logged-in user and protecting routes.

from app.forms import CreatePostForm
# Importing the form class for creating posts.

from app.models import Post, User
# Importing the database models for posts and users.

from app import db

# Importing the database instance for handling database operations.

main_bp = Blueprint('main', __name__)


# Creating a Blueprint named 'main' to group related routes for the main pages.

@main_bp.route('/')
def home():
    """Render the home page with recent posts."""
    try:
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        # Fetch all posts from the database, ordered by the most recent first.

        return render_template('home.html', posts=posts)
        # Render the home page template and pass the posts to it.

    except Exception as e:
        current_app.logger.error(f"Error loading home page: {e}")
        # Log any exceptions that occur while fetching posts or rendering the template.

        return render_template('error.html', message="An error occurred while loading the home page."), 500
        # Render an error page with a 500 status code if an exception is caught.


@main_bp.route('/about')
def about():
    """Render the about page."""
    try:
        return render_template('about.html')
        # Render the about page template.

    except Exception as e:
        current_app.logger.error(f"Error loading about page: {e}")
        # Log any exceptions that occur while rendering the about page.

        return render_template('error.html', message="An error occurred while loading the about page."), 500
        # Render an error page with a 500 status code if an exception is caught.


@main_bp.route('/explore', methods=['GET', 'POST'])
@login_required  # Restricts access to authenticated users only.
def explore():
    """Render the explore page with all posts."""
    form = CreatePostForm()
    # Instantiate the form for creating a new post.

    if form.validate_on_submit():
        # If the form is valid upon submission:
        try:
            post = Post(title=form.title.data, content=form.content.data, author_id=current_user.id)
            # Create a new Post object with the form data and the current user's ID.

            db.session.add(post)
            # Add the new post to the database session.

            db.session.commit()
            # Commit the transaction to save the post to the database.

            flash('Post created successfully!', 'success')
            # Flash a success message to the user.

            return redirect(url_for('main.explore'))
            # Redirect the user back to the explore page.

        except Exception as e:
            current_app.logger.error(f"Error creating post: {e}")
            # Log any exceptions that occur during post creation.

            db.session.rollback()
            # Roll back the database transaction in case of an error.

            flash('An error occurred while creating the post.', 'danger')
            # Flash an error message to the user.

    try:
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        # Fetch all posts from the database, ordered by the most recent first.

        return render_template('explore.html', posts=posts, form=form)
        # Render the explore page template, passing the posts and the form to it.

    except Exception as e:
        current_app.logger.error(f"Error loading explore page: {e}")
        # Log any exceptions that occur while fetching posts or rendering the template.

        return render_template('error.html', message="An error occurred while loading the explore page."), 500
        # Render an error page with a 500 status code if an exception is caught.
