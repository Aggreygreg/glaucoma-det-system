import streamlit as st
from database import register_doctor, verify_login, get_doctor_id_by_username

def show_registration_page():
    st.title("Doctor Registration")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    specialty = st.selectbox("Specialty", ["Ophthalmologist", "Optometrist", "Other"])
    hospital = st.text_input("Hospital/Clinic")
    email = st.text_input("Email")
    phone = st.text_input("Phone")

    if st.button("Register"):
        if register_doctor(username, password, specialty, hospital, email, phone):
            st.success("Registration successful! You can now log in.")
            #if st.button("Go to Login"):
                  #st.markdown('<a href="./#doctor-login" target="_self"><button style="width: 100%; height: 40px; background-color: #4CAF50; color: white; border: none; cursor: pointer;">Go to Login</button></a>', unsafe_allow_html=True)

        else:
            st.error("Username already exists.")

def show_login_page():
    st.title("Doctor Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_login(username, password):
            st.success(f"Correct credentials for {username}, click login button again!")
            # Get doctor ID and save it
            st.session_state.doctor_id = get_doctor_id_by_username(username)
            st.session_state.username = username  # Save username in session state
            return True
        else:
            st.error("Invalid username or password")
    return False
