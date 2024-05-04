
import streamlit as st
# from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
from streamlit.runtime.scriptrunner import get_script_run_ctx 
import json
import time
from streamlit_extras.switch_page_button import switch_page
import requests

load_dotenv(override=True)
st.session_state.debug = True

# save the current timestamp to the session state
st.session_state.timestamp = time.time()

st.set_page_config(
    page_title="MindStorms",
    page_icon="👋",
)

st.write("# Welcome to MindStorms! 👋🔮")

st.markdown(
"""
    # A hive mind for brainstorming
"""
)

PROFILE_ENDPOINT = 'http://127.0.0.1:5000/receive'

def get_name():
    return st.session_state.name if "name" in st.session_state else 'the user'

def set_name(name):
    if "name" in st.session_state:
        st.session_state.name = name
    else:
        st.session_state["name"] = name

# create a form which gives people 3 options
with st.form(key="my_form"):
    # get the user's name
    name = st.text_input("Your name", )
    set_name(name)

    # set work
    work = st.text_input("What do you work on?", )
    st.session_state.work = work

    if st.form_submit_button(label="Next"):
        resp = requests.get(PROFILE_ENDPOINT + '?name=' + name + '&work=' + work)
        switch_page("Chat")