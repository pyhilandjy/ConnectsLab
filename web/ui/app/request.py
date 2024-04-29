import streamlit as st
import requests
from PIL import Image
from io import BytesIO

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
    response = requests.post(url=backend_url + "/stt/image_files/images/", json=data)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None


def get_image_types(user_id, start_date, end_date):
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


def text_replace(file_id, index, new_text, new_speaker_label):
    data = {
        "file_id": file_id,
        "index": index,
        "new_text": new_text,
        "new_speaker_label": new_speaker_label,
    }
    response = requests.put(url=backend_url + "/stt/stt_results/update/", json=data)
    if response.status_code == 200:
        st.success("Update successful!")
    else:
        st.error("Failed to update. Please check the input and try again.")
