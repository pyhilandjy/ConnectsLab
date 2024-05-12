import streamlit as st
import bcrypt
from request import login


def main_ui():
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.title("Connects-lab")
    else:
        st.title("Login Page")
        id = st.text_input("ID")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login(id)
            if user:
                pw = user[0]["pw"]
                role = user[0]["role_id"]
                if pw and bcrypt.checkpw(password.encode("utf-8"), pw.encode("utf-8")):
                    if role == 1:
                        st.session_state["logged_in"] = True
                        st.session_state["user_role"] = "admin"
                        st.success("Login successful as admin!")
                        st.experimental_rerun()
                    else:
                        st.error("You are not authorized as admin")
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Invalid username or password")

        if not st.session_state.get("logged_in", False):
            st.write("Please log in to access admin features.")


if __name__ == "__main__":
    main_ui()
