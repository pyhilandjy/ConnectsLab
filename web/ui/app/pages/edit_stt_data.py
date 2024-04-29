import streamlit as st
import pandas as pd
from request import get_stt_results_by_file_id
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
        # 단어 변경 입력 받기
        old_word = st.text_input("변경할 단어 입력")
        new_word = st.text_input("새로운 단어 입력")
        if st.button("Replace Words"):
            stt_result["text_edited"] = stt_result["text_edited"].str.replace(
                old_word, new_word, regex=True
            )
            st.success("단어 변경 완료!")

        st.write("STT 결과 수정:")
    for i in stt_result.index:
        current_text = stt_result.at[i, "text_edited"]
        current_speaker = stt_result.at[i, "speaker_label"]

        col1, col2 = st.columns([3, 0.5])

        with col1:
            edited_text = st.text_input(f"Row {i+1} Text", current_text)

        with col2:
            speaker_label = st.text_input(f"Row {i+1} Speaker", current_speaker)

        stt_result.at[i, "text_edited"] = edited_text
        stt_result.at[i, "speaker_label"] = speaker_label


if __name__ == "__main__":
    page_2()
