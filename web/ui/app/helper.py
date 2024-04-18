from request import get_users, get_files


def get_users_ids():
    return [user.get("id") for user in get_users()]


def get_files_ids(user_id):
    return [files.get("id") for files in get_files(user_id)]
