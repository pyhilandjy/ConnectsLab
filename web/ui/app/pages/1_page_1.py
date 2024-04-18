import streamlit as st
from request import send_file
from helper import get_users_ids


def page_1():
    st.text("page1")

    # selectbox
    selected_user_id = st.selectbox(
        "Select user",
        get_users_ids(),
        placeholder="Select upload user",
    )

    # file upload
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None:
        response = send_file(file=uploaded_file, user_id=selected_user_id)
        if response.status_code == 200:
            st.success("File successfully uploaded")
        else:
            st.error("Failed to upload file")


if __name__ == "__main__":
    page_1()
