# app/routes/auth_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        return render_template('authentication/register.html', form=form)
    except Exception as e:
        current_app.logger.error(f"Error during registration: {e}")
        return render_template('error.html', message="An error occurred during registration."), 500


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash('You have been logged in!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Login unsuccessful. Please check email and password.', 'danger')
        return render_template('authentication/login.html', form=form)
    except Exception as e:
        current_app.logger.error(f"Error during login: {e}")
        return render_template('error.html', message="An error occurred during login."), 500


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    try:
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('main.home'))
    except Exception as e:
        current_app.logger.error(f"Error during logout: {e}")
        return render_template('error.html', message="An error occurred during logout."), 500
