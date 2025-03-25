import streamlit as st

# Set page config
st.set_page_config(
    page_title="UPSC Notes",
    page_icon="📝",
    layout="wide"
)

# Title
st.title("📝 UPSC Notes")

# Check if there are any notes in session state
if 'notes' not in st.session_state:
    st.session_state.notes = {}
if 'saved_notes' not in st.session_state:
    st.session_state.saved_notes = {}

# Display all notes
if st.session_state.notes or st.session_state.saved_notes:
    # Create tabs for different note categories
    tab1, tab2 = st.tabs(["Generated Notes", "Saved Notes"])
    
    with tab1:
        st.header("Generated Notes")
        for title, notes in st.session_state.notes.items():
            with st.expander(f"📌 {title}"):
                st.text_area("", notes, height=300, key=f"gen_{title}")
                if st.button("Save Note", key=f"save_gen_{title}"):
                    st.session_state.saved_notes[title] = notes
                    st.success("Note saved successfully!")
    
    with tab2:
        st.header("Saved Notes")
        for title, notes in st.session_state.saved_notes.items():
            with st.expander(f"📌 {title}"):
                st.text_area("", notes, height=300, key=f"saved_{title}")
                if st.button("Delete Note", key=f"delete_{title}"):
                    del st.session_state.saved_notes[title]
                    st.success("Note deleted successfully!")
else:
    st.info("No notes available. Generate notes from the main page to view them here!") 