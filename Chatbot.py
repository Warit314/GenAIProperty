import requests
import streamlit as st
import json

# Define the API endpoint
base_api_url = "http://127.0.0.1:8001"
st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Gemma 2b-it")
st.caption("Source: https://github.com/Warit314/GenAIRecuitment")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "results" not in st.session_state:
    st.session_state["results"] = []

if "current_index" not in st.session_state:
    st.session_state["current_index"] = 0

def display_properties():
    result=st.session_state["results"]
    columns = st.columns(len(result))  # Create 3 columns

    for i in range(len(result)):

        if i < len(result):
            property = result[i]
            col_index = i % len(result)  # Determine the column to place the property in
            with columns[col_index].container(border=True):  # Place the property in the appropriate column
                st.write(f"{property.get('TITLE')}")
                st.write("**Price:** ", property.get("PRICE"))

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    #payload for api requests
    payload = {
        "message": prompt
    }

    #to get widgets
    response = requests.post(f"{base_api_url}/generate_query_and_query_sqlite", json=payload, stream=True)

    st.session_state["results"]=response.json()

    if st.session_state["results"]:
        st.write("Found Properties:")
        display_properties()


    chatbot_payload= {
        "message": prompt,
        "query_result": response.text
    }
    # Send the POST request to the API and handle the streaming response
    with requests.post(f"{base_api_url}/chat_bot", json=chatbot_payload, stream=True) as response:
        if response.status_code == 200:
            st.write_stream(response.iter_content(decode_unicode=True))
        else:
            msg = "Sorry, there was an error processing your request."
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)



