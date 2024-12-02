# app/routes/auth_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
# Importing necessary Flask utilities for Blueprint, rendering templates, redirecting, flashing messages,
# handling requests, and accessing the current app context.

from app.forms import LoginForm, RegistrationForm
# Importing custom form classes for login and registration functionality.

from app.models import User
# Importing the User model for interacting with the database.

from app import db, bcrypt
# Importing the database instance (db) and bcrypt for password hashing and verification.

from flask_login import login_user, logout_user, login_required, current_user

# Importing Flask-Login utilities for user authentication and session management.

auth_bp = Blueprint('auth', __name__)


# Creating a Blueprint named 'auth' to group related authentication routes.

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    try:
        if current_user.is_authenticated:
            # If the user is already logged in, redirect them to the home page.
            return redirect(url_for('main.home'))

        form = RegistrationForm()
        # Instantiate the registration form.

        if form.validate_on_submit():
            # If the form is valid upon submission:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            # Hash the user's password securely using bcrypt.

            user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
            # Create a new User object with the submitted data.

            db.session.add(user)
            # Add the new user to the database session.

            db.session.commit()
            # Commit the transaction to save the user to the database.

            flash('Your account has been created! You can now log in.', 'success')
            # Flash a success message to the user.

            return redirect(url_for('auth.login'))
            # Redirect the user to the login page.

        return render_template('authentication/register.html', form=form)
        # Render the registration template and pass the form to it.

    except Exception as e:
        current_app.logger.error(f"Error during registration: {e}")
        # Log any exceptions that occur during registration.

        return render_template('error.html', message="An error occurred during registration."), 500
        # Render an error template with a 500 status code if an exception is caught.


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    try:
        if current_user.is_authenticated:
            # If the user is already logged in, redirect them to the home page.
            return redirect(url_for('main.home'))

        form = LoginForm()
        # Instantiate the login form.

        if form.validate_on_submit():
            # If the form is valid upon submission:
            user = User.query.filter_by(email=form.email.data).first()
            # Query the database for a user with the submitted email address.

            if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
                # Check if the user exists and the submitted password matches the stored hash.
                login_user(user, remember=form.remember.data)
                # Log in the user and handle the 'remember me' option.

                next_page = request.args.get('next')
                # Retrieve the next page to redirect to, if provided.

                flash('You have been logged in!', 'success')
                # Flash a success message to the user.

                return redirect(next_page) if next_page else redirect(url_for('main.home'))
                # Redirect to the next page if specified, otherwise redirect to the home page.

            else:
                flash('Login unsuccessful. Please check email and password.', 'danger')
                # Flash an error message if login fails.

        return render_template('authentication/login.html', form=form)
        # Render the login template and pass the form to it.

    except Exception as e:
        current_app.logger.error(f"Error during login: {e}")
        # Log any exceptions that occur during login.

        return render_template('error.html', message="An error occurred during login."), 500
        # Render an error template with a 500 status code if an exception is caught.


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    try:
        logout_user()
        # Log out the current user and end their session.

        flash('You have been logged out.', 'info')
        # Flash an informational message to the user.

        return redirect(url_for('main.home'))
        # Redirect the user to the home page.

    except Exception as e:
        current_app.logger.error(f"Error during logout: {e}")
        # Log any exceptions that occur during logout.

        return render_template('error.html', message="An error occurred during logout."), 500
        # Render an error template with a 500 status code if an exception is caught.
