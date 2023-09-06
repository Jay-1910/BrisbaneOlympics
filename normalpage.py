import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import openai
import os

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

system_message = (
    "Guidelines for Chatbot Responses:\n\n"
    "1. Clarity and Precision:\n"
    "   - Responses must be clear and concise; avoid assumptions, notes, or 'keep in mind' phrases.\n"
    "   - Provide precise answers without resorting to generic responses such as 'yes' or 'I will provide this answer.'\n\n"
    
    "2. Geographic Coordinates:\n"
    "   - Under no circumstances should geographic coordinates (Latitude, Longitude) or their values be displayed in responses.\n"
    "   - Utilize geographic coordinates only for internal comprehension, if absolutely necessary.\n\n"
    
    "3. Route and Travel Queries:\n"
    "   - When handling route inquiries, give recommendations.\n"
    "   - Mention nearby metro stations, transit options, and estimate travel time.\n"
    "   - Never direct users to online maps.\n\n"
    
    "4. Transportation for Groups:\n"
    "   - For the transportation of sizable groups, explicitly state transportation capacities (e.g., buses, metros).\n"
    "   - Specify the estimated resources needed for precise quantities of people.\n"
    "   - Refrain from suggesting car travel for substantial groups; consider realistic scenarios.\n\n"
    
    "5. Resource Allocation:\n"
    "   - Always divide solutions for large groups optimally.\n"
    "   - Recommend resources like buses, metros, etc., for different segments of the group.\n"
    "   - Incorporate estimated capacities and quantities for each resource.\n\n"
    
    "6. Venue and Location Queries:\n"
    "   - In the event of inquiries about venues or stadiums, only provide the vanues names. Never provide Latitude and Longitude values of the venues. However use the Latitude and Longitude to calculate the distance between two places by grabing the relevant coordinates.\n\n"
    
    "7. Diverse Transportation Strategies:\n"
    "   - Develop an array of strategies for transporting numerous people.\n"
    "   - Take into account options like buses, trains, taxis, walking, cycling, etc.\n"
    "   - Offer multiple alternatives with varying allocations to each mode.\n\n"
    
    "8. Data Source Integration:\n"
    "   - When you possess data on venues and ferry stations, meticulously analyze latitudes and longitudes.\n"
    "   - Offer nearby ferry stations with relevant estimated distance and time to reach by comparing them against venue locations Latitude and Longitude when user asks regarding ferry or water way transportation. Calculate and provide the estimated distance between the venue and ferry station using thier relevant Latitude and Longitude.\n\n"
    
    "9. Related Disciplines in Sports:\n"
    "   - Clearly communicate that certain disciplines like 3x3 Basketball and Basketball, BMX racing and Freestyle BMX,\n"
    "     fall within a unified sport category. They are not separate sports, but interrelated disciplines within the same sport.\n\n"
    
    "10. Consistent Transportation Scenarios:\n"
    "   - For scenarios involving large group travel between venues, the responses must be uniform:\n"
    "     - Propose transportation options (buses, metros, etc.)\n"
    "     - Specify resource numbers and applicable capacity for each resource\n"
    "     - Present a consistent resource allocation strategy for the entire group\n"
    "   - You must consistently deliver the same response for identical scenarios."
)

prompt_ping = (
    "Must read and follow all the rules mentioned in system_message"
    "You must respond to every question based on the directions and rules given in the system_message\n"
    "You must respond to every question based on the information given in the venue_data and ferry_data\n"
)

df_venues = pd.read_csv("venues.csv")
venue_data = df_venues.to_csv(index=False, header=True)

df_ferry = pd.read_csv("ferry_terminals.csv")
ferry_data = df_ferry.to_csv(index=False, header=True)

venues = pd.read_csv("venues.csv")
brisbane_df = venues[venues["City"] == "Brisbane"]
goldcoast_df = venues[venues["City"] == "Gold Coast"]
sunshine_df = venues[venues["City"] == "Sunshine Coast"]
others_df = venues[venues["City"] == "Others"]

fixed_point_size = 5  # Adjust this value as needed


def generate_tooltip(row):
    tooltip = f"<div style='font-size: 14px;'><b>Venue:</b> {row['Venue']}<br>"
    tooltip += f"<b>Type:</b> {row['Type']}<br>"
    tooltip += f"<b>Sports:</b> {row['Sports']}<br>"
    tooltip += "</div>"
    return tooltip

venues['tooltip'] = venues.apply(generate_tooltip, axis=1)
brisbane_df['tooltip'] = brisbane_df.apply(generate_tooltip, axis=1)
goldcoast_df['tooltip'] = goldcoast_df.apply(generate_tooltip, axis=1)
sunshine_df['tooltip'] = sunshine_df.apply(generate_tooltip, axis=1)
others_df['tooltip'] = others_df.apply(generate_tooltip, axis=1)

m_venues = folium.Map(location=[venues.Latitude.mean(), venues.Longitude.mean()], zoom_start=5)
m_brisbane_df = folium.Map(location=[brisbane_df.Latitude.mean(), brisbane_df.Longitude.mean()], zoom_start=9)
m_goldcoast_df = folium.Map(location=[goldcoast_df.Latitude.mean(), goldcoast_df.Longitude.mean()], zoom_start=12)
m_sunshine_df = folium.Map(location=[sunshine_df.Latitude.mean(), sunshine_df.Longitude.mean()], zoom_start=12)
m_others_df = folium.Map(location=[others_df.Latitude.mean(), others_df.Longitude.mean()], zoom_start=5)


for _, row in venues.iterrows():
    folium.Marker(location=[row.Latitude, row.Longitude], radius=fixed_point_size,
                        popup=row['tooltip'],icon=folium.Icon(color="green")).add_to(m_venues)
for _, row in brisbane_df.iterrows():
    folium.Marker(location=[row.Latitude, row.Longitude], radius=fixed_point_size,
                        popup=row['tooltip'],icon=folium.Icon(color="blue")).add_to(m_brisbane_df)
for _, row in goldcoast_df.iterrows():
    folium.Marker(location=[row.Latitude, row.Longitude], radius=fixed_point_size,
                        popup=row['tooltip'],icon=folium.Icon(color="red")).add_to(m_goldcoast_df)    
for _, row in sunshine_df.iterrows():
    folium.Marker(location=[row.Latitude, row.Longitude], radius=fixed_point_size,
                        popup=row['tooltip'],icon=folium.Icon(color="purple")).add_to(m_sunshine_df)   
for _, row in others_df.iterrows():
    folium.Marker(location=[row.Latitude, row.Longitude], radius=fixed_point_size,
                        popup=row['tooltip'],icon=folium.Icon(color="orange")).add_to(m_others_df)


def show_normal_maps():
    st.title('🏅Brisbane 2032 Olympics Maps')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_brisbane = st.checkbox("Brisbane Venues", value=True)

    with col2:
        show_goldcoast = st.checkbox("Gold Coast Venues", value=True)

    with col3:
        show_sunshine = st.checkbox("Sunshine Coast Venues", value=True)

    with col4:
        show_others = st.checkbox("Other Venues", value=True)

    selected_dfs = []
    if show_brisbane:
        selected_dfs.append(brisbane_df)
    if show_goldcoast:
        selected_dfs.append(goldcoast_df)
    if show_sunshine:
        selected_dfs.append(sunshine_df)
    if show_others:
        selected_dfs.append(others_df)

    if len(selected_dfs) == 0:
        st.warning("Please select at least one city.")
    else:
        merged_df = pd.concat(selected_dfs)
        zoom_start = 8

        if show_brisbane and show_goldcoast and show_sunshine and show_others:
            zoom_start = 5
        elif show_others:
            zoom_start = 5

        m_merged = folium.Map(location=[merged_df.Latitude.mean(), merged_df.Longitude.mean()], zoom_start=zoom_start, tiles="openstreetmap")

        for _, row in merged_df.iterrows():
            city = row['City']
            color = None
            if city == 'Brisbane':
                color = 'red'
            elif city == 'Gold Coast':
                color = 'green'
            elif city == 'Sunshine Coast':
                color = 'blue'
            else:
                color = 'purple'

            folium.Marker(
                location=[row.Latitude, row.Longitude],
                radius=fixed_point_size,
                popup=row['tooltip'],
                icon=folium.Icon(color=color)
            ).add_to(m_merged)

        folium_static(m_merged, width=800, height=600)

    st.title("🛣️Route Optimizer")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.conversation_initialized = False

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
            
        if not st.session_state.conversation_initialized:
            st.session_state.conversation_history.append({"role": "user", "content": "system_message:\n" + system_message + "venue_data:\n" + venue_data + "ferry_data:\n" + ferry_data +"User question:\n" + prompt})
            st.session_state.conversation_initialized = True 
        else:
            st.session_state.conversation_history.append({"role": "user", "content": "must follow these notes:\n" + prompt_ping + "User question:\n" + prompt})

        with st.chat_message("user"):
            st.markdown(prompt)            
                    
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.conversation_history
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    show_normal_maps()     
