def validate_register(username, password, password2):
    errors = {}
    if not username:
        errors["username_error"] = "Username is required"
    elif len(username) < 2:
        errors["username_error"] = "Username must be at least 2 characters long"

    if not password:
        errors["password_error"] = "Password is required"
    elif len(password) < 8:
        errors["password_error"] = "Password must be at least 8 characters long"

    if not password2:
        errors["password2_error"] = "Password confirmation is required"
    elif password != password2:
        errors["password2_error"] = "Passwords do not match"

    return errors