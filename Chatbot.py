import requests
import streamlit as st
import pandas as pd
import pydeck as pdk
import json
import uuid

# Define the API endpoint
base_api_url = "http://uvicorn:8001"

# Title and caption
st.title("💬 Property Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Gemma 2b-it")
st.caption("Source: https://github.com/Warit314/GenAIRecuitment")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me about property you have selected, or Search through me!"}]
if "results" not in st.session_state:
    st.session_state["results"] = []
if "selected_properties" not in st.session_state:
    st.session_state["selected_properties"] = []

# Cache plot map data so it doesn't reload every time
@st.cache_data
def plot_map(df):
    st.write("## Property Map (non-interactive)")
    property_layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position=['LONGITUDE', 'LATITUDE'],
        get_radius=50,
        get_color=[0, 0, 0],
        pickable=True,
        auto_highlight=True
    )
    tooltip = {
        "html": "<b>{NAME}</b><br>Latitude: {LATITUDE}<br>Longitude: {LONGITUDE}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
    view_state = pdk.ViewState(
        latitude=df['LATITUDE'].mean(),
        longitude=df['LONGITUDE'].mean(),
        zoom=11,
        pitch=50,
    )
    r = pdk.Deck(
        layers=[property_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=None
    )
    st.pydeck_chart(r)

def ask_chatbot(prompt, response):
    chatbot_payload = {
        "message": prompt,
        "query_result": json.dumps(response, indent=3,ensure_ascii=False)
    }
    with requests.post(f"{base_api_url}/chat_bot", json=chatbot_payload, stream=True) as response:
        if response.status_code == 200:
            st.write_stream(response.iter_content(decode_unicode=True))
        else:
            msg = "Sorry, there was an error processing your request."
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)

def llm_generate_query(prompt):
    payload = {"message": prompt}
    response = requests.post(f"{base_api_url}/generate_query_and_query_sqlite", json=payload, stream=True)
    st.session_state["results"] = response.json()

def display_properties(result):

    for i, property in enumerate(result):
        checkbox_key = f"checkbox_{i}"
        with st.container(border=True):
            st.caption(i + 1)
            st.write(f"{property.get('TITLE')}")
            st.write("**Price:** ", property.get("PRICE"))


def fetch_map_data():
    response = requests.get(f"{base_api_url}/Get_map_plot_data")
    if response.status_code == 200:
        map_data = response.json()
        df = pd.DataFrame(map_data)
        plot_map(df)
        return df
    else:
        st.error('Failed to fetch data to plot the map!')
        return None

def main():
    df = fetch_map_data()
    if df is not None:
        selected_property = st.sidebar.selectbox(
            'Select a property to ask AI or Search Through LLM:',
            df['NAME']
        )
        search_through_llm = st.sidebar.toggle("Search Through LLM")  # Fixed from toggle to checkbox
        
        if selected_property and not search_through_llm:
            selected_info = df[df['NAME'] == selected_property].iloc[0]
            payload = {
                "message": f"SELECT name,title,details, price, routed_distance, routed_time, nearest_stations,pool,sauna,fitness,jacuzzi,keycard,laundry,parking,shuttle,allowPet,security,restaurant FROM sample_data WHERE name = '{selected_info['NAME']}' LIMIT 3"
            }
            response = requests.post(f"{base_api_url}/Query_Sqlite", json=payload)
            st.session_state["results"] = response.json()
            display_properties(st.session_state["results"])
        
        # Display messages after properties are displayed
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # Handle chat input
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            if st.session_state["results"] == [] or search_through_llm:
                llm_generate_query(prompt)
                if st.session_state["results"]:
                    st.caption("Found Properties:")
                    display_properties(st.session_state["results"])
                ask_chatbot(prompt, st.session_state["results"])
            else:
                display_properties(st.session_state["results"])
                ask_chatbot(prompt, st.session_state["results"])

if __name__ == "__main__":
    main()
