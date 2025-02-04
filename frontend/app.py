import streamlit as st
import requests
import os
from datetime import datetime

# Backend API URL
BACKEND_URL = "http://localhost:8000"

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar - Login
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

# Main content
if "access_token" in st.session_state:
    # Sidebar - Session Management
    st.sidebar.header("Chat Sessions")
    if st.sidebar.button("New Chat"):
        response = requests.post(
            f"{BACKEND_URL}/chat/session",
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        if response.status_code == 200:
            st.session_state["current_session"] = response.json()["session_id"]
            st.session_state.messages = []  # Clear messages for new session
            st.experimental_rerun()

    # Get all sessions
    response = requests.get(
        f"{BACKEND_URL}/chat/sessions",
        headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
    )
    if response.status_code == 200:
        sessions = response.json()
        if sessions:
            session_options = {
                f"Session {s['session_id'][:8]} ({format_timestamp(s['created_at'])})": s['session_id']
                for s in sessions
            }
            selected_session_name = st.sidebar.selectbox(
                "Select Chat Session",
                options=list(session_options.keys()),
                index=0 if "current_session" not in st.session_state else 
                      list(session_options.values()).index(st.session_state["current_session"])
            )
            selected_session_id = session_options[selected_session_name]
            
            if "current_session" not in st.session_state or st.session_state["current_session"] != selected_session_id:
                st.session_state["current_session"] = selected_session_id
                # Load session history
                history_response = requests.get(
                    f"{BACKEND_URL}/chat/{selected_session_id}/history",
                    headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                )
                if history_response.status_code == 200:
                    st.session_state.messages = history_response.json()
                st.experimental_rerun()

            # Delete session button
            if st.sidebar.button("Delete Session"):
                delete_response = requests.delete(
                    f"{BACKEND_URL}/chat/session/{selected_session_id}",
                    headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
                )
                if delete_response.status_code == 200:
                    st.session_state.pop("current_session", None)
                    st.session_state.messages = []
                    st.experimental_rerun()

    # File upload section (only for authenticated users)
    st.sidebar.header("Upload Document")
    uploaded_file = st.sidebar.file_uploader("Choose a text file", type="txt")
    if uploaded_file is not None:
        files = {"file": uploaded_file.getvalue()}
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.post(f"{BACKEND_URL}/upload/", files=files, headers=headers)
        if response.status_code == 200:
            st.sidebar.success(response.json().get("message"))
        else:
            st.sidebar.error("Upload failed. Admin access required.")

    # Chat interface
    st.header("Chat with the Document")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question:"):
        if "current_session" in st.session_state:
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(
                f"{BACKEND_URL}/chat/{st.session_state['current_session']}",
                json={"query": prompt},
                headers=headers
            )
            if response.status_code == 200:
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": response.json().get("response")})
                st.experimental_rerun()
            else:
                st.error("Error communicating with the backend")
        else:
            st.warning("Please create or select a chat session")

else:
    st.warning("Please log in to access the chatbot")