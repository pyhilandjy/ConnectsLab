from request import (
    get_users,
    get_files,
    get_image_types,
    get_image_files,
    stt_act_info,
    get_act_names,
)


def get_users_ids():
    """users/user에서 id 데이터 갖고오기"""
    return [user.get("id") for user in get_users()]


def get_users_ids_name():
    """users/user에서 id, user_name 데이터 갖고오기"""
    return [(user.get("id"), user.get("user_name")) for user in get_users()]


def get_files_ids(user_id):
    """files/id 갖고오기"""
    return [(files.get("id"), files.get("edit_status")) for files in get_files(user_id)]


def get_image_file_path(user_id, end_date, start_date, type):
    """image_files/image_path 갖고오기"""
    return [
        get_image_files.get("image_path")
        for get_image_files in get_image_files(user_id, start_date, end_date, type)
    ]


def get_image_type(user_id, start_date, end_date):
    """image_files/type 갖고오기"""
    return [
        image_files.get("type")
        for image_files in get_image_types(user_id, start_date, end_date)
    ]


def get_stt_act_name(act_id):
    """files/id 갖고오기"""
    act = stt_act_info(act_id)
    return act[0]["act_name"]


def get_act_name():
    """users/user에서 id 데이터 갖고오기"""
    return [act.get("act_name") for act in get_act_names()]
