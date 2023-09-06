import streamlit as st
from maps_ai_page import show_ai_maps
from normalpage import show_normal_maps
from PIL import Image
import activity_log 

# Load and resize the logo
image_path = "DTA Logo.png"
logo = Image.open(image_path)
new_size = (160, 100)
logo = logo.resize(new_size)

# Define valid credentials
valid_username = ["jay", "genene"]
valid_password = ["JAYDTA"]

# Check if user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Store the selected page globally
selected_page = None

def show_sidebar():
    global selected_page
    selected_page = st.sidebar.selectbox("Explore AI or Olypics Venues", ("Explore AI", "Olypics Venues"), key="sidebar_select")
    if st.sidebar.button("Sign Out"):
        activity_log.log_activity(st.session_state.username, "User logged out")
        st.session_state.logged_in = False
        selected_page = None
    st.sidebar.markdown("<br>" * 12, unsafe_allow_html=True)
    st.sidebar.image(logo, use_column_width=False, width=new_size[0])

def show_pages():
    if selected_page == "Explore AI":
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.conversation_initialized = False
        show_ai_maps()
    elif selected_page == "Olypics Venues":
        show_normal_maps()

def show_image():
    st.markdown("<br>" * 4, unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col5:
        st.image(logo, width=new_size[0], use_column_width=False)

# Placeholder for content
content_placeholder = st.empty()

if not st.session_state.logged_in:
    st.title('Brisbane 2032 Olympics Sign in🔐')
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if username in valid_username and password in valid_password:
            st.session_state.logged_in = True
            st.session_state.username = username
            activity_log.log_activity(username, "User logged in")
        else:
            st.error("Invalid Credentials")

    show_image()

if st.session_state.logged_in:
    show_sidebar()
    show_pages()
