import streamlit as st
import pandas as pd
from request import (
    get_stt_results_by_file_id,
)
from helper import get_files_ids, get_users_ids_name


def page_4():
    st.text("page4")

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
            stt_result = get_stt_results_by_file_id(selected_file_id[0])
            stt_result = pd.DataFrame(stt_result)

    if not stt_result.empty:
        st.data_editor(stt_result)

    # 이후 추가해야할 로직 > text_edit으로 수정이 가능하도록 > db에 데이터를 다시 보내서 수정을 하도록 해야함  > row추가 혹은 삭제를 만들어야함


#     if not stt_result.empty:
#         replace_col1, replace_col2, replace_col3, replace_col4 = st.columns(4)
#         file_id = selected_file_id[0]
#         with replace_col1:
#             old_text = st.text_input("Old Text")
#         with replace_col2:
#             new_text = st.text_input("New Text")
#         with replace_col3:
#             old_speaker = st.text_input("Old Speaker Label")
#         with replace_col4:
#             new_speaker = st.text_input("New Speaker Label")
#         btn_col1, btn_col2 = st.columns(2)
#         with btn_col1:
#             if st.button("단어 변경"):
#                 text_replace(file_id, old_text, new_text)
#                 st.experimental_rerun()
#         with btn_col2:
#             if st.button("발화자 변경"):
#                 speaker_replace(file_id, old_speaker, new_speaker)
#                 st.experimental_rerun()

#     for _, row in stt_result.iterrows():
#         unique_id = int(row["id"])
#         file_id = row["file_id"]
#         index = row["index"]
#         current_text = row["text_edited"]
#         current_speaker = row["speaker_label"]
#         stt_act_id = int(row["act_id"])
#         stt_act_name = get_stt_act_name(stt_act_id)

#         # 고유 키를 생성하기 위해 `id` 사용
#         unique_key_prefix = f"{unique_id}"

#         col1, col2 = st.columns([3, 0.5])

#         with col1:
#             edited_text = st.text_input(
#                 f"현재화행_{stt_act_name}",
#                 current_text,
#                 key=f"{unique_key_prefix}_text",
#             )

#         with col2:
#             st.text_input(
#                 f"row{index}", current_speaker, key=f"{unique_key_prefix}_speaker"
#             )

#         sa_col = st.columns([0.2, 0.2, 0.3, 0.6, 0.6])
#         with sa_col[0]:
#             save_button = st.button("Save", key=f"{unique_key_prefix}_save")
#             if save_button:
#                 response = edit_stt_result_text(file_id, index, edited_text)
#                 if response == 200:
#                     st.experimental_rerun()
#                 else:
#                     st.error(f"Failed to update Row {index}. Please try again.")

#         with sa_col[1]:
#             add_row = st.button("Add", key=f"{unique_key_prefix}_add")
#             if add_row:
#                 selected_index = index
#                 new_index = index + 1
#                 response = add_row_data(file_id, selected_index, new_index)
#                 if response == 200:
#                     st.experimental_rerun()
#                 else:
#                     st.error(f"Failed to update Row {index}. Please try again.")

#         with sa_col[2]:
#             del_row = st.button("Delete", key=f"{unique_key_prefix}_delete")
#             if del_row:
#                 selected_index = index
#                 response = delete_row_data(file_id, selected_index)
#                 if response == 200:
#                     st.experimental_rerun()
#                 else:
#                     st.error(f"Failed to update Row {index}. Please try again.")

#         with sa_col[3]:
#             selected_act_name = st.selectbox(
#                 "화행 선택", get_act_name(), key=f"{unique_key_prefix}_act"
#             )
#             if selected_act_name != "미설정":
#                 update_act_id(selected_act_name, unique_id)

#     edit_status_col = st.columns([0.5, 0.5, 0.5, 0.5])

#     with edit_status_col[0]:
#         complete_button = st.button("Edit complete", key="edit_complete")
#         if complete_button:
#             response = edit_status(file_id)


if __name__ == "__main__":
    page_4()
