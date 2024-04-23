import streamlit as st
import pandas as pd
from request import get_stt_results_by_file_id
from helper import get_files_ids, get_users_ids_name


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
    st.dataframe(stt_result)


if __name__ == "__main__":
    page_2()
