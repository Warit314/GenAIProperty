import requests
import streamlit as st
import pandas as pd
import pydeck as pdk
import json
# Define the API endpoint
base_api_url = "http://127.0.0.1:8001"
st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Gemma 2b-it")
st.caption("Source: https://github.com/Warit314/GenAIRecuitment")

# Cache plot map data so it doesn't reload everytime
@st.cache_data
def plot_map(df):
    property_layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position=['LONGITUDE', 'LATITUDE'],
        get_radius=100,
        get_color=[255, 0, 0],
        pickable=True,
        auto_highlight=True
    )
    
    # Define the tooltip
    tooltip = {
        "html": "<b>{NAME}</b><br>Latitude: {LATITUDE}<br>Longitude: {LONGITUDE}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    # Define the view state
    view_state = pdk.ViewState(
        latitude=df['LATITUDE'].mean(),
        longitude=df['LONGITUDE'].mean(),
        zoom=12,
        pitch=50,
    )

    # Create the deck.gl map
    r = pdk.Deck(
        layers=[property_layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )

    # Display the map in Streamlit
    st.pydeck_chart(r)

def ask_chatbot(prompt,response):
        chatbot_payload= {
            "message": prompt,
            "query_result": json.dumps(response,ensure_ascii=False)
        }
        # Send the POST request to the API and handle the streaming response
        with requests.post(f"{base_api_url}/chat_bot", json=chatbot_payload, stream=True) as response:
            if response.status_code == 200:
                st.write_stream(response.iter_content(decode_unicode=True))
            else:
                msg = "Sorry, there was an error processing your request."
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.chat_message("assistant").write(msg)

def llm_generate_query(prompt):
    #payload for api requests
    payload = {
        "message": prompt
    }

    #to get widgets
    response = requests.post(f"{base_api_url}/generate_query_and_query_sqlite", json=payload, stream=True)
    
    #SET STATE
    st.session_state["results"]=response.json()

def display_properties(result):
    st.write(f"# {result[0].get('NAME')}")#write the name of the condo by select the first one
    columns = st.columns(len(result))  # Create 3 columns

    for i in range(len(result)):

        if i < len(result):
            property = result[i]
            col_index = i % len(result)  # Determine the column to place the property in
            with columns[col_index].container(border=True):  # Place the property in the appropriate column
                st.write(f"{property.get('TITLE')}")
                st.write("**Price:** ", property.get("PRICE"))


#INIT
# Fetch data from API
response = requests.get(f"{base_api_url}/Get_map_plot_data")

if response.status_code == 200:
    map_data = response.json()
    df = pd.DataFrame(map_data)
    
    plot_map(df)
    
    
    # Dropdown for property selection in the sidebar with "Search Through LLM" as default value
    selected_property = st.sidebar.selectbox(
        'Select a property to ask AI or Search Through LLM:',
        df['NAME'],
    )
    search_through_llm = st.sidebar.toggle("Search Through LLM")
    # Display selected property details
    if selected_property and not search_through_llm:
        selected_info = df[df['NAME'] == selected_property].iloc[0]
        
        payload={
            "message": f"SELECT name,title,details, price, routed_distance, routed_time, nearest_stations,pool,sauna,fitness,jacuzzi,keycard,laundry,parking,shuttle,allowPet,security,restaurant FROM sample_data WHERE name = '{selected_info['NAME']}' LIMIT 3"
        }
        
        response = requests.post(f"{base_api_url}/Query_Sqlite" ,json=payload)

        st.session_state["results"]=response.json()
        display_properties(st.session_state["results"])
else:
    st.error('Failed to fetch data to plot the map!')
    print('Failed to fetch data to plot the map!')




if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me about any property in Thailand"}]
    
if "results" not in st.session_state:
    st.session_state["results"] = []

if "current_index" not in st.session_state:
    st.session_state["current_index"] = 0


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    #if the user didn't select property from drop down and ask directly
    if st.session_state["results"] ==None or search_through_llm:
        query_result=llm_generate_query(prompt)

        if st.session_state["results"]:
            st.write("Found Properties:")
            display_properties(st.session_state["results"])

        ask_chatbot(prompt,st.session_state["results"])


    else:
        display_properties(st.session_state["results"])
        ask_chatbot(prompt,st.session_state["results"])
