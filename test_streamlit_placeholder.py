import streamlit as st
try:
    st.column_config.TextColumn("Test", placeholder="Ex:")
    print("Success")
except Exception as e:
    print(f"Error: {e}")
