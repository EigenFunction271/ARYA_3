import streamlit as st
import requests
import os

# Backend API URL
BACKEND_URL = "http://localhost:8000"

# Login form
st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    response = requests.post(
        f"{BACKEND_URL}/token",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        st.session_state["access_token"] = response.json().get("access_token")
        st.sidebar.success("Logged in successfully")
    else:
        st.sidebar.error("Login failed")

# File upload section (only for authenticated users)
if "access_token" in st.session_state:
    st.sidebar.header("Upload Document")
    uploaded_file = st.sidebar.file_uploader("Choose a text file", type="txt")
    if uploaded_file is not None:
        files = {"file": uploaded_file.getvalue()}
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.post(f"{BACKEND_URL}/upload/", files=files, headers=headers)
        st.sidebar.success(response.json().get("message"))

# Chat interface (only for authenticated users)
if "access_token" in st.session_state:
    st.header("Chat with the Document")
    user_input = st.text_input("Ask a question:")
    if st.button("Send"):
        if user_input:
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(f"{BACKEND_URL}/chat/", json={"query": user_input}, headers=headers)
            if response.status_code == 200:
                st.write(f"**Response:** {response.json().get('response')}")
            else:
                st.error("Error communicating with the backend")
else:
    st.warning("Please log in to access the chatbot")