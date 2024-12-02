# app/routes/profile_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
# Importing Flask utilities for creating blueprints, rendering templates, handling redirects,
# generating URLs, flashing messages, handling requests, logging errors, and returning JSON responses.

from flask_login import login_required, current_user
# Importing Flask-Login utilities to restrict access to authenticated users and retrieve the current user.

from app.forms import UpdateAccountForm
# Importing the form class for updating user account information.

from app.models import User, Post, Follow
# Importing the database models for users, posts, and follow relationships.

from app import db
# Importing the database instance for managing database operations.

profile_bp = Blueprint('profile', __name__, url_prefix='/users')
# Creating a Blueprint named 'profile' with a URL prefix of '/users' for managing user profile-related routes.

@profile_bp.route('/<string:username>')
@login_required
def user_profile(username):
    """Display a user's profile and posts."""
    try:
        user = User.query.filter_by(username=username).first_or_404()
        # Retrieve the user by their username or return a 404 error if not found.

        posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
        # Fetch all posts authored by the user, ordered by the most recent.

        if current_user.id != user.id:
            # Check if the profile being viewed belongs to another user:
            return render_template('profile/public_profile.html', user=user, current_user=current_user, posts=posts)
            # Render the public profile template for the other user.
        else:
            # If the current user is viewing their own profile:
            return render_template('profile/profile.html', user=user, posts=posts)
            # Render the private profile template for the current user.

    except Exception as e:
        current_app.logger.error(f"Error loading profile for {username}: {e}")
        # Log any exceptions that occur while loading the profile.

        return render_template('error.html', message="An error occurred while loading the profile."), 500
        # Render an error template with a 500 status code if an exception is caught.

@profile_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def toggle_follow(user_id):
    """Toggle follow/unfollow for a user."""
    try:
        user = User.query.get_or_404(user_id)
        # Retrieve the user to follow/unfollow by their ID or return a 404 error if not found.

        if user == current_user:
            # Prevent users from following themselves:
            return jsonify({'error': 'You cannot follow yourself.'}), 400
            # Return a JSON error response with a 400 status code.

        if user in current_user.following:
            # If the user is already being followed by the current user:
            current_user.following.remove(user)
            # Remove the user from the current user's following list.

            db.session.commit()
            # Commit the changes to the database.

            return jsonify({'status': 'unfollowed'}), 200
            # Return a JSON response indicating the user has been unfollowed.

        else:
            # If the user is not currently being followed by the current user:
            current_user.following.append(user)
            # Add the user to the current user's following list.

            db.session.commit()
            # Commit the changes to the database.

            return jsonify({'status': 'followed'}), 200
            # Return a JSON response indicating the user has been followed.

    except Exception as e:
        current_app.logger.error(f"Error toggling follow: {e}")
        # Log any exceptions that occur during the follow/unfollow operation.

        return jsonify({'error': 'An error occurred.'}), 500
        # Return a JSON error response with a 500 status code if an exception is caught.
