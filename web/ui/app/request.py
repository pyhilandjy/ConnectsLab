import streamlit as st
import requests
from PIL import Image
from io import BytesIO

backend_url = st.secrets["backend_url"]


def get_users():
    """users table 정보를 모두 요청"""
    response = requests.get(backend_url + "/users/")
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_files(user_id):
    """user_id 별 files table 모두 요청"""
    data = {"user_id": user_id}
    response = requests.post(url=backend_url + "/files/", json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def send_file(file, user_id):
    """user_id의 audio file을 적재하기 위해 요청"""
    files = {"file": (file.name, file, file.type)}
    data = {"user_id": user_id}
    response = requests.post(backend_url + "/audio/uploadfile/", files=files, data=data)
    return response


def get_stt_results_by_file_id(file_id):
    """파일 아이디별로 stt 결과값 요청"""
    data = {"file_id": file_id}
    response = requests.post(
        url=backend_url + "/stt/stt-results-by-file_id/", json=data
    )
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_image_files(user_id, start_date, end_date, type):
    """만들어진 image_file을 요청"""
    data = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
        "type": type,
    }
    response = requests.post(url=backend_url + "/stt/image_files/images/", json=data)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None


def get_image_types(user_id, start_date, end_date):
    """image_files 테이블에서 이미지의 타입을 요청"""
    data = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }
    response = requests.post(
        url=backend_url + "/stt/image_files/image_type/", json=data
    )
    if response.status_code == 200:
        return response.json()
    else:
        return []


def create_wordcloud(user_id, start_date, end_date):
    data = {"user_id": user_id, "start_date": start_date, "end_date": end_date}
    response = requests.post(url=backend_url + "/stt/create-wordcloud/", json=data)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        return image
    else:
        st.error("Failed to generate wordcloud")
        return None


def create_violinplot(user_id, start_date, end_date):
    data = {"user_id": user_id, "start_date": start_date, "end_date": end_date}
    response = requests.post(url=backend_url + "/stt/create-violinplot/", json=data)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        return image
    else:
        st.error("Failed to generate violinplot")
        return None


def text_replace(file_id, old_text, new_text):
    data = {
        "file_id": file_id,
        "old_text": old_text,
        "new_text": new_text,
    }
    response = requests.post(
        url=backend_url + "/stt/stt_results/update_text/", json=data
    )
    if response.status_code == 200:
        st.success("Update successful!")
    else:
        st.error("Failed to update. Please check the input and try again.")


def speaker_replace(file_id, old_speaker, new_speaker):
    data = {
        "file_id": file_id,
        "old_speaker": old_speaker,
        "new_speaker": new_speaker,
    }
    response = requests.post(
        url=backend_url + "/stt/stt_results/update_speaker/", json=data
    )
    if response.status_code == 200:
        st.success("Update successful!")
    else:
        st.error("Failed to update. Please check the input and try again.")


def edit_stt_result_text(file_id, index, new_text):
    """
    text를 ui에서 수정하여 db update 요청
    """
    data = {
        "file_id": file_id,
        "index": index,
        "new_text": new_text,
    }
    response = requests.post(
        url=backend_url + "/stt/stt_results/update_text_edit/", json=data
    )
    if response.status_code == 200:
        return response.status_code
    else:
        st.error("Failed to update.")


def index_increase(file_id, selected_index):
    """
    text를 ui에서 수정하여 db update 요청
    """
    data = {
        "file_id": file_id,
        "selected_index": selected_index,
    }
    response = requests.post(
        url=backend_url + "/stt/stt_results/selected_index_increase/", json=data
    )
    if response.status_code == 200:
        return response.status_code
    else:
        st.error("Failed to update.")


def add_row_data(file_id, selected_index, new_index):
    """
    text를 ui에서 수정하여 db update 요청
    """
    data = {
        "file_id": file_id,
        "selected_index": selected_index,
        "new_index": new_index,
    }
    response = requests.post(
        url=backend_url + "/stt/stt_results/add_index_data/", json=data
    )
    if response.status_code == 200:
        return response.status_code
    else:
        st.error("Failed to update.")
