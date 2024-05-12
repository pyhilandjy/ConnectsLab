import streamlit as st
import pandas as pd
from request import (
    get_stt_results_by_file_id,
    edit_status,
)
from helper import get_files_ids, get_users_ids_name

from pages.services.services import replace_table_controls, row_edit_controls


def page_2():
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.text("page2")
        st.title("STT_RESULTS")

        col_1, col_2 = st.columns([1, 1])

        with col_1:
            # 회원 아이디 불러오는 함수
            selected_user_id = st.selectbox("회원 아이디 선택", get_users_ids_name())

        with col_2:
            if selected_user_id:
                selected_file_id = st.selectbox(
                    "파일 id",
                    get_files_ids(selected_user_id[0]),
                    placeholder="Select file_id",
                )
                try:
                    stt_result = get_stt_results_by_file_id(selected_file_id[0])
                    stt_result = pd.DataFrame(stt_result)
                except Exception as e:
                    st.error(f"STT 결과를 불러오는데 실패했습니다: {e}")

        if not stt_result.empty:
            replace_table_controls(selected_file_id[0])
            for _, row in stt_result.iterrows():
                row_edit_controls(row)

        edit_status_col = st.columns([0.5, 0.5, 0.5, 0.5])
        with edit_status_col[0]:
            complete_button = st.button("Edit complete", key="edit_complete")
            if complete_button:
                response = edit_status(selected_file_id[0])
                if response == 200:
                    st.success("Status updated successfully.")
                else:
                    st.error("Failed to update status.")


if __name__ == "__main__":
    page_2()
