"""
Basic Streamlit UI for Agentic AI - Step 1
A simple "Hello World" to test our setup
"""

import streamlit as st

# Configure the page
st.set_page_config(
    page_title="Agentic AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Main content
st.title("🤖 Agentic AI Assistant")
st.write("Welcome to your AI agent's web interface!")

# Simple test
st.write("This is our first step - testing that Streamlit works correctly.")

# Show some basic info
st.header("System Status")
st.write("✅ Streamlit is running")
st.write("✅ Python environment is active")
st.write("✅ Ready for development")

# Simple interaction
if st.button("Test Button"):
    st.success("Great! The UI is working correctly.")
    st.balloons()  # Fun animation to celebrate