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
    if user_text.strip():  # Check if input is not empty
        # Process the input
        st.session_state.user_input = user_text
        st.session_state.submitted = True
        
        # Show success message
        st.success("Successfully submitted!")
        
        # Display the entered text
        st.info(f"**Your input:** {user_text}")
        
        # Optional: Add some additional processing feedback
        with st.expander("Input Details"):
            st.write(f"**Text entered:** {user_text}")
            st.write(f"**Character count:** {len(user_text)}")
            st.write(f"**Word count:** {len(user_text.split())}")
            st.write(f"**Status:** Processed successfully")
    else:
        st.error("Please enter some text before submitting!")

# Display previous input if exists
if st.session_state.submitted and st.session_state.user_input:
    st.divider()
    st.subheader("Previous Input")
    st.write(f"Last submitted text: **{st.session_state.user_input}**")
    
    # Clear button to reset
    if st.button("Clear Previous Input"):
        st.session_state.submitted = False
        st.session_state.user_input = None
        st.rerun()

# Footer information
st.divider()
st.caption("Simple Streamlit application with text input and submit functionality.")