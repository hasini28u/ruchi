# app.py

import streamlit as st
import llm_backends as backends
import config

# --- Streamlit UI ---
st.set_page_config(page_title="Ruchi: Your Culinary Assistant", page_icon="🌶️")
st.title("Ruchi: Your Culinary Assistant 🌶️")

# Add a select box to choose the language
language_choice = st.selectbox(
    "Select a language:",
    ("English", "Telugu")
)

# Initialize chat history for both languages
if "messages_english" not in st.session_state:
    st.session_state.messages_english = [{"role": "assistant", "content": "Hello! I am Ruchi, your culinary guide. What would you like to cook today?"}]
if "messages_telugu" not in st.session_state:
    st.session_state.messages_telugu = [{"role": "assistant", "content": "నమస్కారం! నేను రుచి, మీ వంటల గైడ్. ఈరోజు మీరు ఏమి వండాలని అనుకుంటున్నారు?"}]

# Determine which chat history to use based on language choice
if language_choice.lower() == "telugu":
    messages = st.session_state.messages_telugu
    user_placeholder = "మీ మనసులో ఏముంది?"
else:
    messages = st.session_state.messages_english
    user_placeholder = "What's on your mind?"

# Display chat messages from history on app rerun
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_query := st.chat_input(user_placeholder):
    with st.chat_message("user"):
        st.markdown(user_query)
    
    messages.append({"role": "user", "content": user_query})

    with st.chat_message("assistant"):
        with st.spinner("Ruchi is thinking..."):
            response = backends.ask(messages, language=language_choice)
            st.markdown(response)
    
    messages.append({"role": "assistant", "content": response})
