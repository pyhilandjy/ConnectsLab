import streamlit as st
import asyncio
from request import (
    text_replace,
    speaker_replace,
    edit_stt_result_text,
    add_row_data,
    delete_row_data,
    update_act_id,
)
from helper import get_stt_act_name, get_act_name


def replace_table_controls(file_id):
    """단어, 발화자 수정 탭"""
    replace_col1, replace_col2, replace_col3, replace_col4 = st.columns(4)
    with replace_col1:
        old_text = st.text_input("Old Text")
    with replace_col2:
        new_text = st.text_input("New Text")
    with replace_col3:
        old_speaker = st.text_input("Old Speaker Label")
    with replace_col4:
        new_speaker = st.text_input("New Speaker Label")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("단어 변경"):
            text_replace(file_id, old_text, new_text)
            st.experimental_rerun()
    with btn_col2:
        if st.button("발화자 변경"):
            speaker_replace(file_id, old_speaker, new_speaker)
            st.experimental_rerun()


async def edit_stt_result_text(file_id, index, edited_text):
    """row text 수정후 저장"""
    response = await asyncio.to_thread(
        edit_stt_result_text, file_id, index, edited_text
    )
    return response


async def update_act_id(selected_act_name, unique_id):
    """act_id를 업데이트"""
    await asyncio.to_thread(update_act_id, selected_act_name, unique_id)


async def save_button(file_id, index, edited_text):
    """텍스트 수정 후 페이지 새로고침"""
    response = await edit_stt_result_text(file_id, index, edited_text)
    if response == 200:
        st.experimental_rerun()
    else:
        st.error(f"Failed to update Row {index}. Please try again.")


def add_button(file_id, index, new_index):
    """row add 버튼"""
    response = add_row_data(file_id, index, new_index)
    if response == 200:
        st.experimental_rerun()
    else:
        st.error(f"Failed to add Row {index}. Please try again.")


def delete_button(file_id, index):
    """row 삭제버튼"""
    response = delete_row_data(file_id, index)
    if response == 200:
        st.experimental_rerun()
    else:
        st.error(f"Failed to delete Row {index}. Please try again.")


def row_edit_controls(row):
    """저장, 추가, 삭제 버튼"""
    unique_id = int(row["id"])
    file_id = row["file_id"]
    index = row["index"]
    current_text = row["text_edited"]
    current_speaker = row["speaker_label"]
    stt_act_id = int(row["act_id"])
    stt_act_name = get_stt_act_name(stt_act_id)
    unique_key_prefix = f"{unique_id}"

    col1, col2 = st.columns([3, 0.5])

    with col1:
        edited_text = st.text_input(
            f"현재화행_{stt_act_name}",
            current_text,
            key=f"{unique_key_prefix}_text",
        )
    with col2:
        st.text_input(
            f"row{index}", current_speaker, key=f"{unique_key_prefix}_speaker"
        )

    sa_col = st.columns([0.2, 0.2, 0.3, 0.6, 0.6])
    with sa_col[0]:
        save_button = st.button("Save", key=f"{unique_key_prefix}_save")
        if save_button:
            asyncio.run(save_button(file_id, index, edited_text))

    with sa_col[1]:
        add_row = st.button("Add", key=f"{unique_key_prefix}_add")
        if add_row:
            new_index = index + 1
            add_button(file_id, index, new_index)

    with sa_col[2]:
        del_row = st.button("Delete", key=f"{unique_key_prefix}_delete")
        if del_row:
            delete_button(file_id, index)

    with sa_col[3]:
        selected_act_name = st.selectbox(
            "화행 선택", get_act_name(), key=f"{unique_key_prefix}_act"
        )
        if selected_act_name != "미설정":
            asyncio.run(update_act_id(selected_act_name, unique_id))
