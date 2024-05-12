import streamlit as st
import requests
from PIL import Image
from io import BytesIO

backend_url = st.secrets["backend_url"]


def get_users():
    """users table 정보를 모두 요청"""
    response = requests.post(backend_url + "/users/")
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
    response = requests.post(url=backend_url + "/stt/results-by-file_id/", json=data)
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
    """워드클라우스 생성"""
    data = {"user_id": user_id, "start_date": start_date, "end_date": end_date}
    response = requests.post(url=backend_url + "/stt/create/wordcloud/", json=data)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        return image
    else:
        st.error("Failed to generate wordcloud")
        return None


def create_violinplot(user_id, start_date, end_date):
    """바이올린플롯 생성"""
    data = {"user_id": user_id, "start_date": start_date, "end_date": end_date}
    response = requests.post(url=backend_url + "/stt/create/violinplot/", json=data)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        return image
    else:
        st.error("Failed to generate violinplot")
        return None


def text_replace(file_id, old_text, new_text):
    """동일 오타 한번에 처리"""
    data = {
        "file_id": file_id,
        "old_text": old_text,
        "new_text": new_text,
    }
    response = requests.post(url=backend_url + "/stt/results/update_text/", json=data)
    if response.status_code == 200:
        st.success("Update successful!")
    else:
        st.error("Failed to update. Please check the input and try again.")


def speaker_replace(file_id, old_speaker, new_speaker):
    """동일 발화자 한번에 처리"""
    data = {
        "file_id": file_id,
        "old_speaker": old_speaker,
        "new_speaker": new_speaker,
    }
    response = requests.post(
        url=backend_url + "/stt/results/update_speaker/", json=data
    )
    if response.status_code == 200:
        st.success("Update successful!")
    else:
        st.error("Failed to update. Please check the input and try again.")


def edit_stt_result_text(file_id, index, new_text):
    """
    row별 text를 수정
    """
    data = {
        "file_id": file_id,
        "index": index,
        "new_text": new_text,
    }
    response = requests.post(
        url=backend_url + "/stt/results/update_text_edit/", json=data
    )
    if response.status_code == 200:
        return response.status_code
    else:
        st.error("Failed to update.")


@st.cache_data
def add_row_data(file_id, selected_index, new_index):
    """
    선택된 row의 복사본 밑으로 추가
    """
    data = {
        "file_id": file_id,
        "selected_index": selected_index,
        "new_index": new_index,
    }
    response = requests.post(
        url=backend_url + "/stt/results/posts/index_data/", json=data
    )
    if response.status_code == 200:
        return response.status_code
    else:
        st.error("Failed to update.")


def delete_row_data(file_id, selected_index):
    """
    선택된 row 삭제
    """
    data = {
        "file_id": file_id,
        "selected_index": selected_index,
    }
    response = requests.post(
        url=backend_url + "/stt/results/index_delete_data/", json=data
    )
    if response.status_code == 200:
        return response.status_code
    else:
        st.error("Failed to update.")


def edit_status(file_id):
    """
    수정 작업상태 변경
    """
    data = {
        "file_id": file_id,
    }
    response = requests.post(url=backend_url + "/stt/results/eidt_status/", json=data)
    if response.status_code == 200:
        return response.status_code
    else:
        st.error("Failed to update.")


def stt_act_info(act_id):
    """
    stt의 act_id로 act_name 반환
    """
    data = {
        "act_id": act_id,
    }
    response = requests.post(url=backend_url + "/stt/results/speech_act/", json=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to update.")


def get_act_names():
    """speech_act table 정보를 모두 요청"""
    response = requests.get(backend_url + "/stt/get/speech_act/")
    if response.status_code == 200:
        return response.json()
    else:
        return []


def update_act_id(act_name, stt_id):
    """
    선택된 act_name을 stt_result의 act_id로 업데이트
    """
    data = {"selected_act_name": act_name, "unique_id": stt_id}
    response = requests.post(url=backend_url + "/stt/update/act_id/", json=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to update.")


def login(id):
    """
    user의 비밀번호, role_id를 반환하는 앤드포인트
    """
    data = {"id": id}
    response = requests.post(url=backend_url + "/users/login", json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return []
