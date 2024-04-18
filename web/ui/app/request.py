import streamlit as st
import requests

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


def get_stt_results(file_id):
    data = {"file_id": file_id}
    response = requests.post(url=backend_url + "/stt/", json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return []
