import streamlit as st

st.write("Streamlit version:", st.__version__)

if st.button("Rerun"):
    st.experimental_rerun()
