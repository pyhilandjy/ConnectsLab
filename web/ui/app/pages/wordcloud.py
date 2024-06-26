import streamlit as st
from datetime import date
from zipfile import ZipFile

from request import create_wordcloud, create_violinplot
from helper import get_users_ids_name, get_image_type
from request import get_image_files


def page_3():
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.title("날짜 범위로 필터링된 wordcloud")

        start_date = st.date_input("시작 날짜", date.today())
        end_date = st.date_input("종료 날짜", date.today())
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        user_id = get_users_ids_name()
        selected_user_id = st.selectbox("사용자 ID 선택", user_id)

        type = get_image_type(selected_user_id[0], start_date, end_date)
        selected_type = st.selectbox("type 선택", type)

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("이미지 조회"):
                wordcloud_image = get_image_files(
                    selected_user_id[0], start_date, end_date, selected_type
                )
                if wordcloud_image is not None:
                    with ZipFile(wordcloud_image, "r") as zip_ref:
                        zip_files = zip_ref.namelist()
                        for file_name in zip_files:
                            with zip_ref.open(file_name) as file:
                                img_bytes = file.read()
                                st.image(
                                    img_bytes, caption=file_name, output_format="PNG"
                                )
                else:
                    st.error("Failed to load images.")
        with col2:
            if st.button("워드클라우드 생성"):
                wordcloud_image = create_wordcloud(
                    selected_user_id[0], start_date, end_date
                )
                if wordcloud_image:
                    st.image(wordcloud_image)
        with col3:
            if st.button("발화량 플롯 생성"):
                wordcloud_image = create_violinplot(
                    selected_user_id[0], start_date, end_date
                )
                if wordcloud_image:
                    st.image(wordcloud_image)


if __name__ == "__main__":
    page_3()
