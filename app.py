"""
Streamlit UI for Agentic AI - Step 5
Connecting to the actual AI agent system
"""

import streamlit as st
import os
import traceback
from datetime import datetime

# Import our agent components
# These are the modules we built that contain the AI agent logic
try:
    from main import run_agent  # Main agent execution function
    from dotenv import load_dotenv  # For loading environment variables
    load_dotenv()  # Load API keys from .env file
    AGENT_AVAILABLE = True
except ImportError as e:
    AGENT_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Configure the page
st.set_page_config(
    page_title="Agentic AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Add custom CSS for better visibility and modern design
st.markdown("""
<style>
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Status panel styling */
    .status-panel {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        background-color: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2196f3;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #2196f3;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1976d2;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Chat area styling */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        background-color: #fafafa;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
# Session state persists data between user interactions
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def process_agent_request(user_input: str):
    """
    Process user input through the AI agent and add response to chat history.
    
    This function:
    1. Checks if the agent system is available
    2. Validates API key configuration
    3. Calls the actual AI agent with error handling
    4. Adds the response (or error) to chat history
    
    Args:
        user_input: The user's message to process
    """
    
    # Check if agent is available
    if not AGENT_AVAILABLE:
        st.session_state.chat_history.append({
            'role': 'agent',
            'content': f"❌ Error: Agent system not available. {IMPORT_ERROR}",
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        return
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        st.session_state.chat_history.append({
            'role': 'agent',
            'content': "❌ Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        return
    
    # Show processing message
    processing_msg = {
        'role': 'agent',
        'content': "🤖 Processing your request...",
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'processing': True  # Flag to identify temporary message
    }
    st.session_state.chat_history.append(processing_msg)
    
    try:
        # Call the actual AI agent
        # This is where the magic happens - your agent will plan and execute!
        agent_response = run_agent(user_input)
        
        # Remove processing message
        st.session_state.chat_history = [msg for msg in st.session_state.chat_history if not msg.get('processing')]
        
        # Add real agent response
        st.session_state.chat_history.append({
            'role': 'agent',
            'content': str(agent_response),
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        # Remove processing message
        st.session_state.chat_history = [msg for msg in st.session_state.chat_history if not msg.get('processing')]
        
        # Add error message with details
        error_msg = f"❌ Agent Error: {str(e)}"
        st.session_state.chat_history.append({
            'role': 'agent',
            'content': error_msg,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'error_details': traceback.format_exc()  # For debugging
        })

# Main content
st.markdown('<h1 class="main-header">🤖 Agentic AI Assistant</h1>', unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([3, 1])  # 3:1 ratio - chat takes more space

with col1:
    st.header("💬 Chat Interface")
    
    # Chat container for better styling
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history with improved formatting and better contrast
    for message in st.session_state.chat_history:
        timestamp = message.get('timestamp', '')
        
        if message['role'] == 'user':
            # User messages - blue background with dark text
            st.markdown(f"""
            <div style="background-color: #2196f3; color: white; padding: 12px; border-radius: 15px; margin: 8px 0; border-left: 4px solid #1976d2;">
                <strong style="color: white;">You</strong> <small style="color: #e3f2fd;">({timestamp})</small><br>
                <span style="color: white;">{message['content']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Agent messages with better contrast
            if message.get('processing'):
                bg_color = "#ff9800"  # Orange for processing
                text_color = "white"
                border_color = "#f57c00"
            elif 'error' in message['content'].lower():
                bg_color = "#f44336"  # Red for errors
                text_color = "white"
                border_color = "#d32f2f"
            else:
                bg_color = "#4caf50"  # Green for successful responses
                text_color = "white"
                border_color = "#388e3c"
                
            st.markdown(f"""
            <div style="background-color: {bg_color}; color: {text_color}; padding: 12px; border-radius: 15px; margin: 8px 0; border-left: 4px solid {border_color};">
                <strong style="color: {text_color};">🤖 Agent</strong> <small style="color: rgba(255,255,255,0.8);">({timestamp})</small><br>
                <span style="color: {text_color};">{message['content']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Show error details in expandable section
            if message.get('error_details'):
                with st.expander("🔍 Debug Details"):
                    st.code(message['error_details'])
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close chat container
    
    # Chat input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message here:")
        submit_button = st.form_submit_button("Send")
        
        # Process input when submitted
        if submit_button and user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            
            # Call the actual AI agent
            process_agent_request(user_input)
            
            # Rerun to show the new messages
            st.rerun()

with col2:
    st.header("📊 Status")
    
    # Check system status
    if not AGENT_AVAILABLE:
        st.write("**Status:** ❌ Agent Error")
        st.error(f"Import Error: {IMPORT_ERROR}")
    elif not os.getenv('OPENAI_API_KEY'):
        st.write("**Status:** ⚠️ No API Key")
        st.warning("Set OPENAI_API_KEY environment variable")
    else:
        st.write("**Status:** 🟢 Ready")
    
    st.write(f"**Messages:** {len(st.session_state.chat_history)}")
    
    # Show last activity if available
    if st.session_state.chat_history:
        last_msg = st.session_state.chat_history[-1]
        if 'timestamp' in last_msg:
            st.write(f"**Last Activity:** {last_msg['timestamp']}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()