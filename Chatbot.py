import requests
import streamlit as st
import json

# Define the API endpoint
api_url = "http://127.0.0.1:8001/full_flow"

with st.sidebar:
    "[Property Finder Chatbot!]"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Gemma 2b-it")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "results" not in st.session_state:
    st.session_state["results"] = []

if "current_index" not in st.session_state:
    st.session_state["current_index"] = 0

def display_properties(start_index):
    end_index = start_index + 3
    for i in range(start_index, end_index):
        if i < len(st.session_state["results"]):
            property = st.session_state["results"][i]
            with st.container():
                st.write("Name: ", property.get("NAME"))
                st.write("TITLE: ", property.get("TITLE"))
                st.write("DETAILS: ", property.get("DETAILS"))
                st.write("PRICE: ", property.get("PRICE"))

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Prepare the payload for the API request
    payload = {
        "message": prompt
    }

    # Send the POST request to the API and handle the streaming response
    response = requests.post(api_url, json=payload)

    if response.status_code == 200:
        st.write_stream(response.iter_content(decode_unicode="UTF-8"))
    else:
        msg = "Sorry, there was an error processing your request."
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

if st.session_state["results"]:
    display_properties(st.session_state["current_index"])

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.session_state["current_index"] > 0:
            if st.button("< Previous"):
                st.session_state["current_index"] -= 1
                display_properties(st.session_state["current_index"])

    with col2:
        st.write("Page", st.session_state["current_index"] // 3 + 1)

    with col3:
        if st.session_state["current_index"] < len(st.session_state["results"]) - 3:
            if st.button("Next >"):
                st.session_state["current_index"] += 1
                display_properties(st.session_state["current_index"])
