import streamlit as st
import requests
import json

# URL to the raw JSON file
url = 'https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Mods.json'


def getData():
    # Fetch the data
    response = requests.get(url)
    # Check for successful request
    if response.status_code == 200:
        mods_data = response.json()  # Parse JSON directly
        print(f"Successfully fetched {len(mods_data)} mods.")
        # Optionally, print a sample
        print(json.dumps(mods_data[0], indent=2))
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

# ---------------------------------------------------------------

# Set page configuration
st.set_page_config(page_title="Simple Dropdown App",
                   page_icon="📋",
                   layout="centered")

# Initialize session state for storing results
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None

# Main application
getData()
st.title("🔽 Simple Dropdown Selection")
st.write("Please select an option from the dropdown below and click submit.")

# Create dropdown with sample options
options = [
    "Option 1: Web Development",
]

# Dropdown selection
selected_value = st.selectbox("Choose your preferred option:",
                              options,
                              index=0,
                              help="Select one option from the dropdown menu")

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
        st.write(
            f"**Submission Time:** {st.session_state.get('submission_time', 'Just now')}"
        )
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
st.caption(
    "Simple Streamlit application with dropdown selection and submit functionality."
)
