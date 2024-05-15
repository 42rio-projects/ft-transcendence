from .models import User


def validate_username(username):
    errors = {}
    if not username:
        errors["username_error"] = "Username is required"
    elif len(username) < 2:
        errors["username_error"] = "Username must be at least 2 characters long"
    elif User.objects.filter(username=username).exists():
        errors["username_error"] = "Username is already in use"

    return errors


def validate_email(email):
    errors = {}
    if User.objects.filter(email=email).exists():
        errors["email_error"] = "Email is already in use"

    return errors


def validate_password(password, password2):
    errors = {}
    if not password:
        errors["password_error"] = "Password is required"
    elif len(password) < 8:
        errors["password_error"] = "Password must be at least 8 characters long"

    if not password2:
        errors["password2_error"] = "Password confirmation is required"
    elif password != password2:
        errors["password2_error"] = "Passwords do not match"

    return errors


def validate_register(username, password, password2):
    errors = {}

    errors.update(validate_username(username))
    errors.update(validate_password(password, password2))

    return errors


def validate_update(user, username, email):
    errors = {}
    if username != user.username:
        errors.update(validate_username(username))

    if email != user.email:
        errors.update(validate_email(email))

    return errors
