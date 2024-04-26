import streamlit as st
import requests
from PIL import Image
import io

backend_url = st.secrets["backend_url"]


def get_users():
    response = requests.get(backend_url + "/users/")
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_files(user_id):
    data = {"user_id": user_id}
    response = requests.post(url=backend_url + "/files/", json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def send_file(file, user_id):
    files = {"file": (file.name, file, file.type)}
    data = {"user_id": user_id}
    response = requests.post(backend_url + "/audio/uploadfile/", files=files, data=data)
    return response


def get_stt_results_by_file_id(file_id):
    data = {"file_id": file_id}
    response = requests.post(
        url=backend_url + "/stt/stt-results-by-file_id/", json=data
    )
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_image_files(user_id, start_date, end_date, type):
    data = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
        "type": type,
    }
    response = requests.post(
        url=backend_url + "/stt/stt-results/image_file/", json=data
    )
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_image_types(user_id, start_date, end_date):
    data = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }
    response = requests.post(
        url=backend_url + "/stt/stt-results/image_type/", json=data
    )
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_wordcloud(user_id, start_date, end_date):
    data = {"user_id": user_id, "start_date": start_date, "end_date": end_date}
    response = requests.post(url=backend_url + "/stt/stt-results-wordcloud/", json=data)
    if response.status_code == 200:
        image_path = response.json()
        return image_path
    else:
        st.error("Failed to generate wordcloud")
        return None
