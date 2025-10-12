"""
Basic Streamlit UI for Agentic AI - Step 4
Adding chat interface components
"""

import streamlit as st

# Configure the page
st.set_page_config(
    page_title="Agentic AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for chat history
# Session state persists data between user interactions
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Main content
st.title("🤖 Agentic AI Assistant")

# Create two columns for layout
col1, col2 = st.columns([3, 1])  # 3:1 ratio - chat takes more space

with col1:
    st.header("💬 Chat Interface")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**🤖 Agent:** {message['content']}")
    
    # Chat input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message here:")
        submit_button = st.form_submit_button("Send")
        
        # Process input when submitted
        if submit_button and user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # For now, just echo back (we'll connect to the agent later)
            st.session_state.chat_history.append({
                'role': 'agent',
                'content': f"I received your message: '{user_input}'"
            })
            
            # Rerun to show the new messages
            st.rerun()

with col2:
    st.header("📊 Status")
    st.write("**Status:** 🟢 Ready")
    st.write(f"**Messages:** {len(st.session_state.chat_history)}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()