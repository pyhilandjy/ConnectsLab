import streamlit as st
import pandas as pd
from request import get_stt_results
from helper import get_users_ids, get_files_ids


def page_2():
    st.text("page2")

    st.title("STT_RESULTS")

    col_1, col_2 = st.columns([1, 1])

    with col_1:
        # 회원 아이디 불러오는 함수

        selected_user_id = st.selectbox("회원 아이디 선택", get_users_ids())

    with col_2:

        if selected_user_id:

            selected_user_id = st.selectbox(
                "Select user",
                get_files_ids(selected_user_id),
                placeholder="Select file_id",
            )

    stt_result = get_stt_results()
    stt_result = pd.DataFrame(stt_result)
    st.dataframe(stt_result)


if __name__ == "__main__":
    page_2()
