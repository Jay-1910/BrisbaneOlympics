import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import openai
import os


os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

filter_ping = ("You have 2 functions: filter_df_and_save_by_sport('sport name') and filter_df_and_save_by_city('city name')\n"
"Based on the User question, just give me the appropriate function with argument (replace with sport_name or city_name) such as filter_df_and_save_by_sport('volleyball') and filter_df_and_save_by_city('brisbane'). You must not provide anything other text in your response other than function.\n")


def convert_message_to_string(message):
    if 'by_sport' in message:
        target = message.split('(')[1].split(')')[0]
        return ' '.join([word.title() for word in target.split()]) + ' Hosting Venues'
    elif 'by_city' in message:
        target = message.split('(')[1].split(')')[0]
        return ' '.join([word.title() for word in target.split()]) + ' Venues'
    else:
        return "Invalid message format"
        
def filter_df_and_save_by_sport(sport):
    df = pd.read_csv('venues_all_cities.csv')
    filtered_data = df[df['Sports'].str.contains(sport, case=False, na=False)]
    if not filtered_data.empty:
        m = folium.Map(location=[filtered_data['Latitude'].mean(), filtered_data['Longitude'].mean()], zoom_start=5)
        for index, row in filtered_data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=row['Venue']
            ).add_to(m)
        return m
    else:
        st.write("No venues found for the selected sport.")

def filter_df_and_save_by_city(city):
    df = pd.read_csv('venues_all_cities.csv')
    filtered_data = df[df['City'].str.contains(city, case=False, na=False)]
    if not filtered_data.empty:
        m = folium.Map(location=[filtered_data['Latitude'].mean(), filtered_data['Longitude'].mean()], zoom_start=9)
        for index, row in filtered_data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=row['Venue']
            ).add_to(m)
        return m
    else:
        st.write("No venues found for the selected city.")

def generate_tooltip(row):
    tooltip = f"<div style='font-size: 14px;'><b>Venue:</b> {row['Venue']}<br>"
    tooltip += f"<b>Type:</b> {row['Type']}<br>"
    tooltip += f"<b>Sports:</b> {row['Sports']}<br>"
    tooltip += "</div>"
    return tooltip

def show_ai_maps():
    st.title('🏅Brisbane 2032 Olympics Interactive Maps')

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.conversation_initialized = False

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.conversation_history.append({"role": "user", "content": "Must follow these instructions: " + filter_ping + "User question:\n" + prompt})

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
            map_title = convert_message_to_string(full_response)
            map_title = map_title.replace('"', ' ')
            st.header(map_title)
            filter_map = eval(full_response)
            folium_static(filter_map)

#         st.session_state.messages.append({"role": "user", "content": prompt})
#         st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Clear the conversation history after each interaction
        st.session_state.conversation_history = []

if __name__ == "__main__":
    show_ai_maps()
