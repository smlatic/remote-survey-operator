import streamlit as st

def run():
    st.title("Summary")

    st.header("Welcome to the Course Introduction")

    st.write("""
    This course aims to provide an overview of becoming a remote survey operator. 
    We'll cover topics ranging from basic operations, theory of various surveying equipment,
    familiarization steps, to advanced concepts in Geodesy and inertial navigation.
    """)
    
    st.video('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    
    st.write("""
    Let's start the journey together!
    """)

