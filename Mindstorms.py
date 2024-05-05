import streamlit as st
from openai import OpenAI
import requests, json
import time

st.title("MindStorms 🧠🌩️")
st.subheader("Who is hotter - Donald Trump or Elon Musk?")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

CLIENT_CHAT_PROMPT = "Try to argue with the user about their proposition in a fun way. \
            Keep your responses short, concise, and conversational. \
            Provide valuable insights but remember that the user doesn't like long-winded answers."
            
FRAME_NEXT_QUESTION = 'I recently had a conversation with an AI about a certain topic. Here is the history: \
    {chat_history} \
    **END OF CONVERSATION** \
    Here is the current state of a larger ongoing debate on the same topic: \
    {objective}. \
    I want you to generate a comical reaction and question which continues the conversation.    \
    Make sure you cite the debate in some way and frame the question in context of that larger debate. \
    Keep the response short and fun - just a single comment/question/reference is enough! \
    Try to ask questions about aspects not covered yet in the conversation or the ongoing debate. \
    '

SUMMARY_PROMPT = "Write down the main point made by the user in the conversation."

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": CLIENT_CHAT_PROMPT}]

# awaiting_objective, chat, or reporting
if "client_state" not in st.session_state:
    st.session_state.client_state = "awaiting_objective"
    

FETCH_OBJECTIVE_URL = "http://192.168.1.71:5001/request_task"
NOTIFY_ENDPOINT = "http://192.168.1.71:5001/task_completed"


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message['role'] != 'system':
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def verify_objective(messages, objective):
    if len(messages) > 2:
        return True
    return False

def openai_call(prompt):
    response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": 'user', "content": prompt}
        ],
    )
    return response.choices[0].message.content

def request_objective():
    while True:
        resp = requests.get(FETCH_OBJECTIVE_URL)
        if resp.status_code == 200:
            st.session_state.task_json = resp.json()
            objective = st.session_state.task_json["description"]
            st.session_state.objective = objective
            chat_history = ""
            for m in st.session_state.messages:
                if m['role'] == 'user':
                    chat_history += m['role'] + ': ' + m["content"] + " \n"
            next_question = openai_call(
                FRAME_NEXT_QUESTION.format(chat_history=chat_history, objective=objective))
            st.session_state.messages.append(
                {"role": "assistant", "content": next_question}
            )
            with st.chat_message("assistant"):
                st.markdown(next_question)
            st.session_state.client_state = "chat"
            break
        time.sleep(0.2)
    print('Objective received: ' + objective)
    print('Question framed: ' + next_question)

if len(st.session_state.messages) == 1:
    request_objective()

prompt = st.chat_input("Type a message...")
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
                "role": "assistant",
                "content": SUMMARY_PROMPT,
            }
        )
        response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=msgs[-5:],
        )
        response = response.choices[0].message.content
        # st.session_state.messages = []
        st.empty()

        # with st.chat_message("system"):
        #     st.markdown("Summary: " + response)

        payload = dict(st.session_state.task_json, result=response)
        resp = requests.post(
            NOTIFY_ENDPOINT,
            data=json.dumps(payload),
            headers={
                "Content-type": "application/json",
                "Accept": "application/json",
            },
        )
        request_objective()

    # but = st.button("Leave Conversation")
