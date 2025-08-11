import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Simple Dropdown App",
    page_icon="📋",
    layout="centered"
)

# Initialize session state for storing results
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None

# Main application
st.title("🔽 Simple Dropdown Selection")
st.write("Please select an option from the dropdown below and click submit.")

# Create dropdown with sample options
options = [
    "Option 1: Web Development",
    "Option 2: Data Analysis",
    "Option 3: Machine Learning",
    "Option 4: Mobile Development",
    "Option 5: Cloud Computing",
    "Option 6: Cybersecurity"
]

# Dropdown selection
selected_value = st.selectbox(
    "Choose your preferred option:",
    options,
    index=0,
    help="Select one option from the dropdown menu"
)

# Submit button
if st.button("Submit Selection", type="primary"):
    # Process the selection
    st.session_state.selected_option = selected_value
    st.session_state.submitted = True
    
    # Show success message
    st.success(f"✅ Successfully submitted!")
    
    # Display the selected value
    st.info(f"**Your selection:** {selected_value}")
    
    # Optional: Add some additional processing feedback
    with st.expander("📊 Selection Details"):
        st.write(f"**Selected Option:** {selected_value}")
        st.write(f"**Submission Time:** Just now")
        st.write(f"**Status:** Processed successfully")

# Display previous selection if exists
if st.session_state.submitted and st.session_state.selected_option:
    st.divider()
    st.subheader("Previous Selection")
    st.write(f"Last submitted option: **{st.session_state.selected_option}**")
    
    # Clear button to reset
    if st.button("Clear Previous Selection"):
        st.session_state.submitted = False
        st.session_state.selected_option = None
        st.rerun()

# Footer information
st.divider()
st.caption("Simple Streamlit application with dropdown selection and submit functionality.")
