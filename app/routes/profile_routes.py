# app/routes/profile_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.forms import UpdateAccountForm
from app.models import User, Post, Follow
from app import db

profile_bp = Blueprint('profile', __name__, url_prefix='/users')


@profile_bp.route('/<string:username>')
@login_required
def user_profile(username):
    """Display a user's profile and posts."""
    try:
        user = User.query.filter_by(username=username).first_or_404()
        posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
        if current_user.id != user.id:
            print(current_user.following)
            return render_template('profile/public_profile.html', user=user, current_user=current_user, posts=posts)
        else:
            return render_template('profile/profile.html', user=user, posts=posts)
    except Exception as e:
        current_app.logger.error(f"Error loading profile for {username}: {e}")
        return render_template('error.html', message="An error occurred while loading the profile."), 500


@profile_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """Allow the current user to update their account information."""
    try:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            # Handle profile picture update if applicable
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('profile.account'))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
        return render_template('account.html', form=form)
    except Exception as e:
        current_app.logger.error(f"Error updating account for {current_user.username}: {e}")
        return render_template('error.html', message="An error occurred while updating your account."), 500


@profile_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def toggle_follow(user_id):
    """Toggle follow/unfollow for a user."""
    try:
        user = User.query.get_or_404(user_id)
        if user == current_user:
            return jsonify({'error': 'You cannot follow yourself.'}), 400

        if user in current_user.following:
            # Unfollow
            current_user.following.remove(user)
            db.session.commit()
            return jsonify({'status': 'unfollowed'}), 200
        else:
            # Follow
            current_user.following.append(user)
            db.session.commit()
            return jsonify({'status': 'followed'}), 200
    except Exception as e:
        current_app.logger.error(f"Error toggling follow: {e}")
        return jsonify({'error': 'An error occurred.'}), 500


@profile_bp.route('/<string:username>/unfollow', methods=['POST'])
@login_required
def unfollow_user(username):
    """Unfollow a user."""
    try:
        user_to_unfollow = User.query.filter_by(username=username).first_or_404()
        if user_to_unfollow == current_user:
            flash('You cannot unfollow yourself!', 'danger')
            return redirect(url_for('profile.user_profile', username=username))
        current_user.unfollow(user_to_unfollow)
        db.session.commit()
        flash(f'You have unfollowed {username}.', 'info')
        return redirect(url_for('profile.user_profile', username=username))
    except Exception as e:
        current_app.logger.error(f"Error unfollowing user {username}: {e}")
        return render_template('error.html', message="An error occurred while unfollowing the user."), 500
