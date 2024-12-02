from flask_wtf import FlaskForm
# Importing FlaskForm, the base class for creating forms with Flask-WTF.

from flask_wtf.file import FileField, FileAllowed
# Importing file-related fields and validators for handling file uploads.

from wtforms.fields.simple import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
# Importing basic field types such as string, password, submit, boolean, and textarea fields.

from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
# Importing common validators for form fields, such as required fields, email validation, length constraints,
# equality checks, and custom validation errors.

from flask_login import current_user
# Importing the current_user object to access the currently logged-in user's information.

from app.models import User


# Importing the User model for querying the database during validation.

# -------------------------------
# Registration Form
# -------------------------------
class RegistrationForm(FlaskForm):
    # Field for username with data requirement and length constraints (2-20 characters).
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    # Field for email with data requirement and email format validation.
    email = StringField('Email', validators=[DataRequired(), Email()])

    # Field for password with data requirement.
    password = PasswordField('Password', validators=[DataRequired()])

    # Field for confirming password with data requirement and equality check with the password field.
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    # Submit button for the form.
    submit = SubmitField('Register')


# -------------------------------
# Login Form
# -------------------------------
class LoginForm(FlaskForm):
    # Field for email with data requirement and email format validation.
    email = StringField('Email', validators=[DataRequired(), Email()])

    # Field for password with data requirement.
    password = PasswordField('Password', validators=[DataRequired()])

    # Boolean checkbox for "Remember Me" functionality.
    remember = BooleanField('Remember Me')

    # Submit button for the form.
    submit = SubmitField('Login')


# -------------------------------
# Create Post Form
# -------------------------------
class CreatePostForm(FlaskForm):
    # Field for post title with data requirement and a maximum length of 200 characters.
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])

    # Text area field for post content with data requirement.
    content = TextAreaField('Content', validators=[DataRequired()])

    # Submit button for the form.
    submit = SubmitField('Post')


# -------------------------------
# Comment Form
# -------------------------------
class CommentForm(FlaskForm):
    # Text area field for comment content with data requirement and length constraints (1-300 characters).
    content = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=1, max=300, message="Comment must be between 1 and 300 characters.")
    ])

    # Submit button for the form.
    submit = SubmitField('Post Comment')

    # Custom validation method for comment content.
    def validate_content(self, field):
        prohibited_words = ["spam", "advertisement", "clickbait"]
        # List of prohibited words to filter out.

        if any(word in field.data.lower() for word in prohibited_words):
            # Raise a validation error if the content contains any prohibited words.
            raise ValidationError("Your comment contains prohibited words. Please remove them.")


# -------------------------------
# Update Account Form
# -------------------------------
class UpdateAccountForm(FlaskForm):
    # Field for username with data requirement and length constraints (3-20 characters).
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=20)]
    )

    # Field for email with data requirement and email format validation.
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )

    # File upload field for profile picture with validation to allow only specific file types.
    profile_picture = FileField(
        'Update Profile Picture',
        validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')]
    )

    # Submit button for the form.
    submit = SubmitField('Update Account')

    # Custom validation method for username.
    def validate_username(self, username):
        # Check if the new username is already taken, excluding the current user.
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("This username is already taken. Please choose a different one.")

    # Custom validation method for email.
    def validate_email(self, email):
        # Check if the new email is already in use, excluding the current user.
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("This email is already in use. Please choose a different one.")
