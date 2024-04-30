import streamlit as st
import pandas as pd
from request import (
    get_stt_results_by_file_id,
    text_replace,
    speaker_replace,
    edit_stt_result_text,
    index_increase,
    add_row_data,
)
from helper import get_files_ids, get_users_ids_name


def add_row(index):
    new_row = st.session_state.df.iloc[index].copy()
    st.session_state.df = st.session_state.df.append(new_row, ignore_index=True)


def page_2():
    st.text("page2")

    st.title("STT_RESULTS")

    col_1, col_2 = st.columns([1, 1])

    with col_1:
        # 회원 아이디 불러오는 함수
        selected_user_id = st.selectbox("회원 아이디 선택", get_users_ids_name())

    with col_2:
        # 회원아이디의 file_id 불러오는 함수

        if selected_user_id:

            selected_file_id = st.selectbox(
                "파일 id",
                get_files_ids(selected_user_id[0]),
                placeholder="Select file_id",
            )
            stt_result = get_stt_results_by_file_id(selected_file_id)
            stt_result = pd.DataFrame(stt_result)

    # 이후 추가해야할 로직 > text_edit으로 수정이 가능하도록 > db에 데이터를 다시 보내서 수정을 하도록 해야함  > row추가 혹은 삭제를 만들어야함

    if not stt_result.empty:
        replace_col1, replace_col2, replace_col3, replace_col4 = st.columns(4)
        file_id = selected_file_id
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

    for i in stt_result["index"]:
        current_text = stt_result.at[i - 1, "text_edited"]
        current_speaker = stt_result.at[i - 1, "speaker_label"]

        col1, col2 = st.columns([3, 0.5])

        with col1:
            edited_text = st.text_input(f"Row {i}", current_text)

        with col2:
            st.text_input(f"Row {i}", current_speaker)

        sa_col = st.columns([0.2, 0.2, 0.8, 0.8])  # 버튼을 위한 새로운 컬럼 설정
        with sa_col[0]:
            save_button = st.button("Save", key=f"save_{i}")
            if save_button:
                index = i
                response = edit_stt_result_text(file_id, index, edited_text)
                if response == 200:
                    st.experimental_rerun()
                else:
                    st.error(f"Failed to update Row {i}. Please try again.")

        with sa_col[1]:
            add_row = st.button("Add", key=f"add_{i}")
            if add_row:
                selected_index = i
                new_index = i + 1
                index_increase(file_id, selected_index)
                response = add_row_data(file_id, selected_index, new_index)
                if response == 200:
                    st.experimental_rerun()
                else:
                    st.error(f"Failed to update Row {i}. Please try again.")


if __name__ == "__main__":
    page_2()
