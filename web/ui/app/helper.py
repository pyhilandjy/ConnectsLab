from request import get_users, get_files, get_image_files, get_image_types


def get_users_ids():
    """users/user에서 id 데이터 갖고오기"""
    return [user.get("id") for user in get_users()]


def get_users_ids_name():
    """users/user에서 id, user_name 데이터 갖고오기"""
    return [(user.get("id"), user.get("user_name")) for user in get_users()]


def get_files_ids(user_id):
    """files/id 갖고오기"""
    return [files.get("id") for files in get_files(user_id)]


def get_image_id(id):
    """image_files/id 갖고오기"""
    return [image_files.get("id") for image_files in get_image_files(id)]


def get_image_type(user_id, start_date, end_date):
    """image_files/type 갖고오기"""
    return [
        image_files.get("type")
        for image_files in get_image_types(user_id, start_date, end_date)
    ]
