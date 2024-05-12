import pickle
from pathlib import path

import streamlit_authenticator as stauth

names = ["junyong"]
usernames = ["wnsdyd54"]
passwords = ["connects_lab"]

hashed_passwords = stauth.Hasher(passwords).generate()
