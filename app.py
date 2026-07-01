import streamlit as st

st.set_page_config(page_title="GPX Analyzer", layout="wide")

st.title("⚽ GPX Analyzer")
st.subheader("Football Performance Analysis")

player = st.text_input("👤 Player Name")

uploaded_file = st.file_uploader(
    "📤 Upload GPX File",
    type=["gpx"]
)

if uploaded_file:
    st.success("✅ File uploaded successfully")

    st.markdown("## Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Distance", "-- km")

    with col2:
        st.metric("Max Speed", "-- km/h")

    with col3:
        st.metric("Duration", "--")

    st.info("The GPX analysis engine will be added in the next step.")
