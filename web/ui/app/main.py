import streamlit as st
import requests

from request import get_users, send_file


def main_ui():
    st.title("C_LAB")

    users = get_users()

    # selectbox
    selected_user_id = st.selectbox("Select user", 
                                    [user.get("id") for user in users], 
                                    placeholder="Select upload user",)

    # file upload
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None:
        response = send_file(file=uploaded_file, user_id=selected_user_id)
        if response.status_code == 200:
            st.success("File successfully uploaded")
        else:
            st.error("Failed to upload file")


if __name__ == "__main__":
    main_ui()
