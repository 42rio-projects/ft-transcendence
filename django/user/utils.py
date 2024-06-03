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


def validate_nickname(nickname):
    errors = {}
    if not nickname:
        return errors
    elif len(nickname) < 2:
        errors["nickname_error"] = "Nickname must be at least 2 characters long"
    elif User.objects.filter(nickname=nickname).exists():
        errors["nickname_error"] = "Nickname is already in use"

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


def validate_update(user, username, nickname):
    errors = {}
    if username != user.username:
        errors.update(validate_username(username))

    if nickname != user.nickname:
        errors.update(validate_nickname(nickname))

    return errors


def handle_user_action(user1, user2, action):
    if action == 'send-friend-invite':
        user1.add_friend(user2)
        return 'Friend invite sent'
    elif action == 'cancel-friend-invite':
        user1.cancel_friend_invite(user2)
        return 'Friend invite canceled'
    elif action == 'remove-friend':
        user1.del_friend(user2)
        return 'Friend removed'
    elif action == 'block':
        user1.block_user(user2)
        return 'User blocked'
    elif action == 'unblock':
        user1.unblock_user(user2)
        return 'User unblocked'
