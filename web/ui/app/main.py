import streamlit as st
import bcrypt
from request import login


def main_ui():
    # 페이지 타이틀 설정
    st.title("Connects-lab")

    # 세션 상태에서 로그인 확인
    if st.session_state.get("logged_in"):
        # 로그인 성공 후 표시할 내용
        st.write("You are logged in as admin.")
        if st.button("Logout"):
            # 로그아웃 버튼이 클릭되면 로그인 상태를 초기화
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.experimental_rerun()
    else:
        # 로그인 페이지 제목
        st.title("Login Page")
        id = st.text_input("ID")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login(id)
            if user:
                pw = user[0]["pw"]
                role = user[0]["role_id"]
                # 비밀번호 검증
                if pw and bcrypt.checkpw(password.encode("utf-8"), pw.encode("utf-8")):
                    if role == 1:
                        # 관리자로 로그인 성공 시, 세션 상태 설정
                        st.session_state.logged_in = True
                        st.session_state.user_role = "admin"
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
