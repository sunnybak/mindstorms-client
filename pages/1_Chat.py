import streamlit as st
from openai import OpenAI
import requests, json
import time

st.title("ChatGPT-like clone")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# awaiting_objective, chat, or reporting
if "client_state" not in st.session_state:
    st.session_state.client_state = "awaiting_objective"
    

FETCH_OBJECTIVE_URL = "http://127.0.0.1:5000"
NOTIFY_ENDPOINT = "http://127.0.0.1:5000/summary"


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def verify_objective(messages, objective):
    if len(messages) > 3:
        return True
    return False


def sys_prompt(objective):
    prompt = f'Chat with the user to meet this objective: "{objective}"'
    return prompt


if st.session_state.client_state == "awaiting_objective":
    while True:
        resp = requests.get(FETCH_OBJECTIVE_URL)
        if resp.status_code == 200:
            objective = resp.text
            st.session_state.objective = objective
            st.session_state.messages.append(
                {"role": "system", "content": sys_prompt(objective)}
            )
            with st.chat_message("system"):
                st.markdown("Objective: " + objective)
            st.session_state.client_state = "chat"
            break
        time.sleep(0.2)

if st.session_state.client_state == "chat":
    prompt = st.chat_input(st.session_state.objective)
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

        if verify_objective(st.session_state.messages, st.session_state.objective):
            # summarize the messages and answer the objective
            # send a post request to the server with the summary
            msgs = []
            for m in st.session_state.messages:
                msgs.append({"role": m["role"], "content": m["content"]})
            msgs.append(
                {
                    "role": "user",
                    "content": "Produce a short summary of this conversation.",
                }
            )
            response = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=msgs,
            )
            response = response.choices[0].message.content
            st.session_state.messages = []
            st.empty()

            with st.chat_message("system"):
                st.markdown("Summary: " + response)

            payload = {"summary": response}
            resp = requests.post(
                NOTIFY_ENDPOINT,
                data=json.dumps(payload),
                headers={
                    "Content-type": "application/json",
                    "Accept": "application/json",
                },
            )
            st.session_state.client_state = "awaiting_objective"

    but = st.button("Leave Conversation")
