import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Simple Input App",
    page_icon="📝",
    layout="centered"
)

# Initialize session state for storing results
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'user_input' not in st.session_state:
    st.session_state.user_input = None

# Main application
st.title("📝 Simple Input Form")
st.write("Please enter your text in the input box below and click submit.")

# Create input box
user_text = st.text_input(
    "Enter your text:",
    placeholder="Type something here...",
    help="Enter any text you'd like to submit"
)

# Submit button
if st.button("Submit", type="primary"):
    if user_text.strip():
        print(user_text)
